"""
Note -> statements, indexed by context.

Model A asked one open-ended question ("find all relations in this note"), which
the literature puts at roughly 75% relation precision. Model B asks two
constrained ones:

    1. which of these ~50 known contexts does this statement live in?   (classification)
    2. which known terms occur in it?                                   (string match, no LLM)

Trading generation for classification plus lookup is the reliability win, and it
comes from the shape of the model rather than from better prompting.
"""

import json
import re
from pathlib import Path
from typing import Optional

from src.logger import log
from src.atlas.schema import (
    NoteExtraction, Provenance, ProvenanceKind, Statement, Term,
)
from src.atlas.store import AtlasStore

PAGE_RE = re.compile(r"<!--\s*Page\s+(\d+)\s*-->")
HEADING_RE = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)


EXTRACT_PROMPT = """\
You are indexing a page of a student's mathematics lecture notes into an atlas.

The atom is a STATEMENT IN A CONTEXT. A context is the ambient theory a statement
lives in - the setting whose axioms it assumes. You must classify every statement
into exactly one of the contexts listed below. Do not invent context ids.

AVAILABLE CONTEXTS (id -- name):
{contexts}

WHAT TO EXTRACT

statements: every theorem, lemma, definition, corollary, or solution method that
the notes actually assert. For each:
  - context      : the id of the MOST SPECIFIC context whose assumptions the
                   statement needs. A statement about integrating factors for
                   y' + p(x)y = q(x) lives in LinearODE, not in ODE.
  - slogan       : a short canonical English sentence naming the result, with no
                   notation. This is a join key: two notes stating the same
                   result must produce the same slogan. e.g. "an exact equation
                   has a potential function whose differential is the equation".
  - hypotheses   : the conditions required, as short phrases.
  - conclusion   : what follows.
  - statement_latex : the statement as written, LaTeX preserved.
  - status       : THEOREM if asserted true, DEFINITION if it defines a term,
                   FALSE if the notes give a counterexample, OPEN if unresolved.
  - role         : Theorem | Lemma | Corollary | Proposition | Definition | Axiom | Method
  - exact_quote  : a verbatim snippet (max 200 chars) from the text.

terms: mathematical names the notes DEFINE. For each: name, the context id it is
defined in, kind (OBJECT | PROPERTY | CONSTRUCTION | OPERATOR), and the definition.

RULES
1. Classify by what the statement ASSUMES, not by the chapter it appears in.
2. Do not extract exercises, worked numeric examples, headings, or admin text.
3. If a statement genuinely does not fit any listed context, omit it rather than
   forcing it into a wrong one. Omissions are cheap; misclassifications are not.
4. Prefer fewer, well-formed statements over many vague ones.

NOTE TEXT
{text}
"""


def _context_listing(store: AtlasStore) -> str:
    rows = []
    for cid, c in sorted(store.contexts.items(), key=lambda kv: kv[1].get("course", "")):
        rows.append(f"  {cid} -- {c.get('name', cid)}")
    return "\n".join(rows)


def _locate(text: str, quote: str) -> tuple[Optional[int], Optional[str]]:
    """Recover page number and enclosing heading for a verbatim quote."""
    if not quote:
        return None, None
    idx = text.find(quote[:60])
    if idx < 0:
        return None, None
    before = text[:idx]
    pages = PAGE_RE.findall(before)
    heads = HEADING_RE.findall(before)
    return (int(pages[-1]) if pages else None, heads[-1].strip() if heads else None)


def extract_note(
    note_path: Path, store: AtlasStore, model_hint: Optional[str] = None
) -> tuple[list[Statement], list[Term], dict]:
    """Runs stage 1 (classification) then stage 2 (term matching) for one note."""
    from google.genai import types as genai_types
    from src.llm.gemini import get_gemini_client, get_gemini_candidate_models

    text = note_path.read_text(encoding="utf-8")
    client = get_gemini_client()
    if not client:
        log.warning("No Gemini client; cannot extract.")
        return [], [], {"error": "no client"}

    prompt = EXTRACT_PROMPT.format(contexts=_context_listing(store), text=text)
    valid_ctx = set(store.contexts)

    raw = None
    used_model = None
    for model in ([model_hint] if model_hint else []) + get_gemini_candidate_models():
        if not model:
            continue
        try:
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=NoteExtraction,
                    temperature=0.1,
                ),
            )
            raw = json.loads(resp.text)
            used_model = model
            break
        except Exception as e:
            log.warning(f"Extraction via '{model}' failed: {e}")

    if raw is None:
        return [], [], {"error": "all models failed"}

    prov_base = {"doc_title": note_path.name, "doc_path": str(note_path)}
    stats: list[Statement] = []
    dropped_ctx = 0

    for s in raw.get("statements", []):
        ctx = s.get("context")
        if ctx not in valid_ctx:
            dropped_ctx += 1
            continue
        quote = (s.get("provenance") or [{}])[0].get("exact_quote", "") if s.get("provenance") else ""
        quote = quote or s.get("exact_quote", "") or ""
        page, heading = _locate(text, quote)
        try:
            st = Statement(
                context=ctx,
                slogan=(s.get("slogan") or "").strip(),
                hypotheses=s.get("hypotheses") or [],
                conclusion=s.get("conclusion") or "",
                statement_latex=s.get("statement_latex") or "",
                status=s.get("status") or "THEOREM",
                role=s.get("role"),
                provenance_kind=ProvenanceKind.EXTRACTED,
                provenance=[Provenance(**prov_base, page_number=page,
                                       section_heading=heading, exact_quote=quote[:200])],
            )
        except Exception as e:
            log.debug(f"Malformed statement skipped: {e}")
            continue
        if st.slogan:
            stats.append(st)

    terms: list[Term] = []
    for t in raw.get("terms", []):
        ctx = t.get("context")
        if ctx not in valid_ctx or not t.get("name"):
            continue
        try:
            terms.append(Term(
                name=t["name"].strip(), context=ctx,
                kind=t.get("kind") or "PROPERTY",
                definition_latex=t.get("definition_latex") or t.get("definition") or "",
                provenance_kind=ProvenanceKind.EXTRACTED,
                provenance=[Provenance(**prov_base)],
            ))
        except Exception:
            continue

    # ---- stage 2: term occurrence, no LLM ------------------------------
    known = {t.name.lower(): t for t in list(store.terms.values()) + terms}
    for st in stats:
        hay = f"{st.slogan} {st.conclusion} {' '.join(st.hypotheses)} {st.statement_latex}".lower()
        st.uses_terms = sorted({
            t.key for name, t in known.items()
            if len(name) > 3 and re.search(rf"\b{re.escape(name)}", hay)
        })

    report = {
        "model": used_model,
        "statements": len(stats),
        "terms": len(terms),
        "dropped_unknown_context": dropped_ctx,
        "with_page": sum(1 for s in stats if s.provenance and s.provenance[0].page_number),
    }
    log.info(f"{note_path.name}: {report}")
    return stats, terms, report
