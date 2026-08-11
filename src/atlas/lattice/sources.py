"""
Independent transcription sources for the context lattice.

The lattice is not novel information — it is in Wikipedia's lede sentences, in
Wikidata's `subclass of` chains, and in any LLM's weights. So this is a
*transcription problem with redundancy*, not an extraction problem: read it
from several places and diff them (see `merge.py`).

Each source emits candidate `(child, parent)` pairs meaning "child extends
parent" — child assumes everything parent assumes, and more.
"""

import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

import requests

from src.logger import log
from src.atlas.lattice.seed import ALL_CONTEXTS, ContextSeed, wikipedia_title_map

UA = {"User-Agent": "comeback-helper-lattice/0.1 (educational knowledge graph)"}
WIKI_API = "https://en.wikipedia.org/w/api.php"
SPARQL = "https://query.wikidata.org/sparql"

# Wikipedia throttles a burst of ~50 requests hard. Pace, retry, and cache to
# disk so iterating on the parser costs nothing.
_CACHE = Path(".storage/lattice_cache")
_LAST_CALL = [0.0]
_MIN_INTERVAL = 0.4


def _paced_get(params: dict, cache_key: Optional[str] = None,
               url: str = WIKI_API, extra_headers: Optional[dict] = None,
               attempts: int = 4) -> Optional[dict]:
    """GET with disk cache, minimum call spacing, and exponential backoff."""
    if cache_key:
        _CACHE.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", cache_key)[:120]
        cached = _CACHE / f"{safe}.json"
        if cached.exists():
            try:
                return json.loads(cached.read_text(encoding="utf-8"))
            except Exception:
                pass

    for attempt in range(attempts):
        wait = _MIN_INTERVAL - (time.time() - _LAST_CALL[0])
        if wait > 0:
            time.sleep(wait)
        _LAST_CALL[0] = time.time()
        try:
            r = requests.get(
                url, params=params,
                headers={**UA, **(extra_headers or {})}, timeout=45,
            )
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"status {r.status_code}")
            r.raise_for_status()
            data = r.json()
            if cache_key:
                cached.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception as e:
            if attempt == attempts - 1:
                log.warning(f"request failed after {attempts} attempts: {e}")
                return None
            time.sleep(1.5 * (2 ** attempt))
    return None


# ---------------------------------------------------------------------------
# Source 1: Wikipedia lede links
#
# Maths articles follow an editorial convention: the first paragraph is a
# definition. Links in that paragraph are the things you must already have in
# order to *state* the definition — which, restricted to context articles, is
# very close to axiom inclusion. Crucially it is asymmetric in the right
# direction: "Metric space" ledes to topology; "Topological space" does not
# lede to metric spaces.
# ---------------------------------------------------------------------------


class _FirstParaLinks(HTMLParser):
    """Collects /wiki/ links appearing in the first substantive <p> block."""

    def __init__(self):
        super().__init__()
        self.depth_p = 0
        self.para_index = 0
        self.text_len = 0
        self.links: list[str] = []
        self._done = False

    def handle_starttag(self, tag, attrs):
        if self._done:
            return
        if tag == "p":
            self.depth_p += 1
            self.text_len = 0
            self.links = self.links if self.para_index else []
        elif tag == "a" and self.depth_p > 0:
            href = dict(attrs).get("href", "")
            m = re.match(r"^/wiki/([^#:?]+)$", href)
            if m:
                title = requests.utils.unquote(m.group(1)).replace("_", " ")
                self.links.append(title)

    def handle_endtag(self, tag):
        if tag == "p" and self.depth_p > 0:
            self.depth_p -= 1
            # A hatnote or empty <p> has almost no text; keep looking.
            if self.text_len > 80:
                self.para_index += 1
                self._done = True

    def handle_data(self, data):
        if self.depth_p > 0:
            self.text_len += len(data.strip())


def _fetch_lede_html(title: str) -> Optional[str]:
    data = _paced_get(
        {"action": "parse", "page": title, "prop": "text",
         "section": "0", "format": "json", "redirects": "1"},
        cache_key=f"lede_{title}",
    )
    try:
        return data["parse"]["text"]["*"]
    except Exception:
        log.warning(f"Wikipedia lede unavailable for '{title}'")
        return None


def wikipedia_edges() -> tuple[list[tuple[str, str]], dict]:
    """Returns (edges, coverage_report). Edge = (child_id, parent_id)."""
    title_to_id = wikipedia_title_map()
    edges: set[tuple[str, str]] = set()
    missing: list[str] = []
    hits = 0

    for ctx in ALL_CONTEXTS:
        if not ctx.wikipedia:
            continue
        html = _fetch_lede_html(ctx.wikipedia)
        if not html:
            missing.append(ctx.id)
            continue

        parser = _FirstParaLinks()
        parser.feed(html)
        hits += 1

        for linked_title in parser.links:
            target = title_to_id.get(linked_title)
            if target and target != ctx.id:
                edges.add((ctx.id, target))

    log.info(f"Wikipedia: {len(edges)} candidate edges from {hits} ledes.")
    return sorted(edges), {"articles_read": hits, "missing": missing}


# ---------------------------------------------------------------------------
# Source 2: Wikidata `subclass of` (P279)
#
# A genuinely curated partial order, no convention-mining required. Coverage
# for mathematical structures is patchy, so this is a seed/validator rather
# than a complete source.
# ---------------------------------------------------------------------------


def _resolve_qids(contexts: list[ContextSeed]) -> dict[str, str]:
    """Wikipedia title → QID, batched 40 at a time."""
    titled = [c for c in contexts if c.wikipedia]
    qids: dict[str, str] = {}

    for i in range(0, len(titled), 40):
        batch = titled[i:i + 40]
        payload = _paced_get(
            {"action": "query", "prop": "pageprops",
             "ppprop": "wikibase_item", "redirects": "1",
             "titles": "|".join(c.wikipedia for c in batch),
             "format": "json"},
            cache_key=f"qids_{i}_{len(batch)}",
        )
        if not payload:
            continue
        data = payload.get("query", {})
        normalized = {n["from"]: n["to"] for n in data.get("normalized", [])}
        redirects = {n["from"]: n["to"] for n in data.get("redirects", [])}
        resolved = {}
        for page in data.get("pages", {}).values():
            q = page.get("pageprops", {}).get("wikibase_item")
            if q:
                resolved[page["title"]] = q
        for c in batch:
            t = c.wikipedia
            t = normalized.get(t, t)
            t = redirects.get(t, t)
            if t in resolved:
                qids[c.id] = resolved[t]

    log.info(f"Wikidata: resolved {len(qids)} QIDs.")
    return qids


def wikidata_edges() -> tuple[list[tuple[str, str]], dict]:
    qids = _resolve_qids(ALL_CONTEXTS)
    if not qids:
        return [], {"resolved": 0, "note": "no QIDs resolved"}

    qid_to_id = {q: cid for cid, q in qids.items()}
    values = " ".join(f"wd:{q}" for q in qids.values())
    query = f"""
    SELECT ?a ?b WHERE {{
      VALUES ?a {{ {values} }}
      ?a wdt:P279 ?b .
    }}
    """

    edges: set[tuple[str, str]] = set()
    external = 0
    payload = _paced_get(
        {"query": query, "format": "json"},
        cache_key="sparql_p279",
        url=SPARQL,
        extra_headers={"Accept": "application/sparql-results+json"},
    )
    if not payload:
        return [], {"resolved": len(qids), "error": "SPARQL request failed"}

    for b in payload["results"]["bindings"]:
        a = b["a"]["value"].rsplit("/", 1)[-1]
        bq = b["b"]["value"].rsplit("/", 1)[-1]
        if a in qid_to_id and bq in qid_to_id:
            child, parent = qid_to_id[a], qid_to_id[bq]
            if child != parent:
                edges.add((child, parent))
        else:
            external += 1

    log.info(f"Wikidata: {len(edges)} in-scope P279 edges ({external} pointed outside scope).")
    return sorted(edges), {"resolved": len(qids), "out_of_scope": external}


# ---------------------------------------------------------------------------
# Source 3: LLM background knowledge
#
# The prompt must fight the dominant failure mode explicitly: pedagogical
# order is NOT axiom inclusion, and a subject taxonomy is NOT a lattice.
# ---------------------------------------------------------------------------

LATTICE_PROMPT = """\
You are transcribing a well-known mathematical structure: the partial order of \
mathematical CONTEXTS (ambient theories) ordered by AXIOM INCLUSION.

DEFINITION. "A extends B" means: every axiom of B is assumed by A, and A assumes \
strictly more. A is therefore the MORE SPECIFIC setting.
  correct:   MetricSpace extends TopologicalSpace   (a metric induces a topology)
  correct:   HilbertSpace extends InnerProductSpace
  correct:   Field extends IntegralDomain

CRITICAL RULES — these are the two ways this task is usually failed:

1. TEACHING ORDER IS IRRELEVANT. Many courses teach metric spaces before general
   topological spaces. That does NOT make TopologicalSpace extend MetricSpace.
   Judge only by "does A assume everything B assumes, plus more?"

2. DO NOT PRODUCE A SUBJECT TAXONOMY. "Analysis -> Real Analysis -> Measure Theory"
   is a classification of topics and is WRONG here. You are producing axiom
   inclusion between theories, not a table of contents.

Emit only immediate parents (the transitive reduction). If A extends B and B
extends C, do not also emit A extends C. A context may have several immediate
parents (e.g. NormedVectorSpace extends both VectorSpace and MetricSpace) —
that is expected and important.

Use ONLY these context ids. Do not invent new ones.
{context_list}

Return JSON: {{"edges": [{{"child": "<id>", "parent": "<id>", "why": "<max 12 words>"}}]}}
"""


def llm_edges() -> tuple[list[tuple[str, str]], dict]:
    from google.genai import types as genai_types
    from src.llm.gemini import get_gemini_client, get_gemini_candidate_models

    client = get_gemini_client()
    if not client:
        log.warning("No Gemini client; skipping LLM source.")
        return [], {"note": "gemini unavailable"}

    ids = {c.id for c in ALL_CONTEXTS}
    listing = "\n".join(f"  {c.id}  ({c.name})" for c in ALL_CONTEXTS)
    prompt = LATTICE_PROMPT.format(context_list=listing)

    for model in get_gemini_candidate_models():
        try:
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.0,
                ),
            )
            raw = json.loads(resp.text).get("edges", [])
            edges: set[tuple[str, str]] = set()
            reasons: dict[str, str] = {}
            dropped = 0
            for e in raw:
                c, p = e.get("child"), e.get("parent")
                if c in ids and p in ids and c != p:
                    edges.add((c, p))
                    reasons[f"{c}->{p}"] = e.get("why", "")
                else:
                    dropped += 1
            log.info(f"LLM ({model}): {len(edges)} edges, {dropped} dropped as out-of-vocabulary.")
            return sorted(edges), {"model": model, "dropped": dropped, "reasons": reasons}
        except Exception as e:
            log.warning(f"LLM source via '{model}' failed: {e}")

    return [], {"note": "all candidates failed"}
