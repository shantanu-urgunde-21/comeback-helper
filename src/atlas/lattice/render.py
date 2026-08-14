"""
Render the context lattice as a Hasse diagram.

    python -m src.atlas.lattice.render

Writes `static/lattice.html` — self-contained, no external assets.

Layout is deterministic and semantic: vertical position is longest-path depth
in the lattice, so height *is* the order relation. That is the whole claim of
the Model B design — abstraction as a spatial axis rather than another edge in
a force-directed tangle. Horizontal order is chosen only to reduce crossings.
"""

import json
import re
from pathlib import Path

import networkx as nx

from src.logger import log

# ---------------------------------------------------------------------------
# Half-day probe: is there a real second axis *inside* a context, orthogonal
# to lattice depth? Scalar-vs-system was chosen because it's mechanically
# visible in hypothesis text (unlike e.g. "two-solution vs n-solution", which
# needs real parsing) and it already showed real structure by hand on
# HomogeneousLinearODE: 4 of 16 statements are the vector-valued analogue of
# statements already sitting in the scalar cluster. This is a heuristic, not
# an extraction pass — if the axis proves worth it, promote it to a real
# closed-set tag classification the way context assignment already works.
# ---------------------------------------------------------------------------
_SYSTEM_RE = re.compile(r"\bsystem\b|x\^\(\d+\)|mathbf", re.I)


def _sub_tag(st: dict) -> str:
    blob = " ".join(st.get("hypotheses") or []) + " " + st.get("slogan", "") + " " + st.get("conclusion", "")
    return "system" if _SYSTEM_RE.search(blob) else "scalar"

DATA = Path(__file__).parent / "data" / "contexts.json"
OUT = Path(__file__).resolve().parents[3] / "static" / "lattice.html"
OUT_ATLAS = Path(__file__).resolve().parents[3] / "static" / "atlas.html"

ROW_H = 100
NODE_H = 30
GAP_X = 26
PAD = 48


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------


def _depths(G: nx.DiGraph) -> dict[str, int]:
    depth = {n: 0 for n in G}
    for n in nx.topological_sort(G.reverse()):
        for child in G.reverse().successors(n):
            depth[child] = max(depth[child], depth[n] + 1)
    return depth


def _node_width(label: str) -> float:
    return max(96.0, min(262.0, 22 + len(label) * 7.15))


def _order_layers(G: nx.DiGraph, layers: dict[int, list[str]], sweeps: int = 12):
    """
    Barycentre crossing reduction. Each node drifts toward the mean position of
    its neighbours in the adjacent layer; alternating passes settle it.
    """
    pos = {n: i for lvl in layers for i, n in enumerate(layers[lvl])}
    depths_sorted = sorted(layers)

    for s in range(sweeps):
        order = depths_sorted if s % 2 == 0 else list(reversed(depths_sorted))
        for lvl in order:
            adj_lvl = lvl - 1 if s % 2 == 0 else lvl + 1
            if adj_lvl not in layers:
                continue
            adj = set(layers[adj_lvl])

            def bary(n: str) -> float:
                nbrs = [m for m in set(G.successors(n)) | set(G.predecessors(n)) if m in adj]
                return sum(pos[m] for m in nbrs) / len(nbrs) if nbrs else pos[n]

            layers[lvl].sort(key=lambda n: (bary(n), n))
            for i, n in enumerate(layers[lvl]):
                pos[n] = i
    return layers


TERM_H = 16
TERM_GAP_Y = 8


def build_layout(
    data: dict,
    statements: list[dict] | None = None,
    terms: list[dict] | None = None,
) -> dict:
    G = nx.DiGraph()
    for c in data["contexts"]:
        G.add_node(c["id"], **c)
    for c in data["contexts"]:
        for p in c["extends"]:
            G.add_edge(c["id"], p)  # child -> parent (upward)

    depth = _depths(G)
    layers: dict[int, list[str]] = {}
    for n, d in depth.items():
        layers.setdefault(d, []).append(n)
    for d in layers:
        layers[d].sort(key=lambda n: (G.nodes[n]["course"], G.nodes[n]["name"]))
    layers = _order_layers(G, layers)

    widths = {n: _node_width(G.nodes[n]["name"]) for n in G}
    row_span = {
        d: sum(widths[n] for n in ns) + GAP_X * (len(ns) - 1)
        for d, ns in layers.items()
    }
    canvas_w = max(row_span.values()) + PAD * 2

    nodes = []
    for d, ns in sorted(layers.items()):
        x = (canvas_w - row_span[d]) / 2
        for n in ns:
            a = G.nodes[n]
            nodes.append({
                "id": n, "name": a["name"], "course": a["course"],
                "wiki": a.get("wikipedia"), "depth": d,
                "x": round(x, 1), "y": PAD + d * ROW_H,
                "w": round(widths[n], 1), "h": NODE_H,
                "extends": a["extends"],
            })
            x += widths[n] + GAP_X

    src = data.get("edge_sources", {})
    edges = []
    for child, parent in G.edges():
        s = src.get(f"{child}->{parent}", [])
        edges.append({
            "from": child, "to": parent, "sources": s,
            "tier": "corroborated" if len(s) >= 2 else "single",
        })

    # `over` edges are parameterisations, not order relations — they are drawn
    # but deliberately excluded from depth, so they may run sideways or upward.
    over = [
        {"from": c["id"], "to": p, "sources": src.get(f"{c['id']}->{p}", [])}
        for c in data["contexts"] for p in c.get("over", [])
        if p in {n["id"] for n in nodes}
    ]

    # Terms are the vocabulary layer: drawn as small labelled nodes directly
    # beneath the context that defines them, above the statements that use it.
    # Reading order top-to-bottom then becomes theory -> vocabulary -> facts.
    node_by_id = {n["id"]: n for n in nodes}
    terms_by_ctx: dict[str, list[dict]] = {}
    for t in (terms or []):
        terms_by_ctx.setdefault(t["context"], []).append(t)

    placed_terms: list[dict] = []
    ctx_term_row_h: dict[str, float] = {}
    for cid, group in terms_by_ctx.items():
        host = node_by_id.get(cid)
        if not host:
            continue
        group.sort(key=lambda t: t["name"])
        widths_t = [max(56.0, min(150.0, 16 + len(t["name"]) * 6.4)) for t in group]
        span = sum(widths_t) + 6 * (len(widths_t) - 1)
        x = host["x"] + host["w"] / 2 - span / 2
        y = host["y"] + NODE_H + TERM_GAP_Y
        for t, w in zip(group, widths_t):
            placed_terms.append({**t, "x": round(x, 1), "y": round(y, 1), "w": round(w, 1), "h": TERM_H})
            x += w + 6
        ctx_term_row_h[cid] = TERM_H + TERM_GAP_Y

    term_by_key = {t["key"]: t for t in placed_terms}

    # Usage edges: a statement -> every term it cites. Colour by whether the
    # term is actually visible from the statement's context (defined there or
    # in an ancestor) — the same check validate.py's term-not-visible gate
    # runs, so a misclassification shows up as a visibly wrong-looking edge on
    # the canvas instead of only as a line in a JSON report.
    ancestors_of = {cid: nx.descendants(G, cid) for cid in G}
    term_use_edges = []
    for st in (statements or []):
        for key in st.get("uses_terms", []):
            t = term_by_key.get(key)
            if not t:
                continue
            valid = t["context"] == st["context"] or t["context"] in ancestors_of.get(st["context"], set())
            term_use_edges.append({"term": key, "statement_context": st["context"],
                                   "statement_slogan": st["slogan"], "valid": valid,
                                   "statement_id": st["id"]})

    # Disambiguation: terms sharing a name across different contexts. Model B's
    # whole premise is that these must never merge — this is what makes that
    # claim visible rather than asserted. Not a bug when it fires; it is the
    # feature working.
    by_name: dict[str, list[str]] = {}
    for t in placed_terms:
        by_name.setdefault(t["name"].strip().lower(), []).append(t["key"])
    disambiguation_edges = [
        {"a": keys[i], "b": keys[i + 1], "name": name}
        for name, keys in by_name.items() if len(keys) > 1
        for i in range(len(keys) - 1)
    ]

    # Statements are plotted beneath the context that holds them: the lattice
    # supplies their coordinates, so nothing about their position is guessed.
    #
    # Within a context they are grouped by `role` — THEOREM/LEMMA/COROLLARY vs
    # METHOD vs DEFINITION are a different kind of claim (a fact you know vs a
    # recipe you follow), and separating them turns an undifferentiated wall of
    # dots into a legible sub-cluster. This is a real second axis that was
    # already being collected and simply never drawn.
    ROLE_FAMILY = {
        "Theorem": "theorem", "Lemma": "theorem", "Corollary": "theorem",
        "Proposition": "theorem", "Axiom": "theorem",
        "Definition": "definition", "Method": "method",
    }
    FAMILY_ORDER = {"theorem": 0, "method": 1, "definition": 2}

    placed: list[dict] = []
    grouped: dict[str, list[dict]] = {}
    TAG_ORDER = {"scalar": 0, "system": 1}

    for st in (statements or []):
        st["family"] = ROLE_FAMILY.get(st.get("role") or "", "theorem")
        st["sub_tag"] = _sub_tag(st)
        grouped.setdefault(st["context"], []).append(st)

    for cid, group in grouped.items():
        host = node_by_id.get(cid)
        if not host:
            continue
        group.sort(key=lambda s: (
            FAMILY_ORDER.get(s["family"], 0), TAG_ORDER.get(s["sub_tag"], 0), s["slogan"],
        ))
        per_row = max(1, int(host["w"] // 13))
        col = 0
        row = 0
        # A break starts a new row when family OR sub_tag changes, so a
        # scalar/system split is visible as a row gap without a new colour.
        prev_key = None
        for st in group:
            key = (st["family"], st["sub_tag"])
            if prev_key is not None and key != prev_key and col > 0:
                row += 1
                col = 0
            prev_key = key
            placed.append({**st, "_row": row, "_col": col})
            col += 1
            if col >= per_row:
                row += 1
                col = 0

        term_offset = ctx_term_row_h.get(cid, 0)
        max_col_in_row: dict[int, int] = {}
        for st in placed[-len(group):]:
            max_col_in_row[st["_row"]] = max(max_col_in_row.get(st["_row"], 0), st["_col"])
        for st in placed[-len(group):]:
            n_in_row = max_col_in_row[st["_row"]] + 1
            span = (n_in_row - 1) * 13
            st["x"] = round(host["x"] + host["w"] / 2 - span / 2 + st["_col"] * 13, 1)
            st["y"] = host["y"] + NODE_H + 14 + term_offset + st["_row"] * 14
            del st["_row"], st["_col"]

    for n in nodes:
        group = grouped.get(n["id"], [])
        n["n_statements"] = len(group)
        n["family_counts"] = {
            fam: sum(1 for s in group if s["family"] == fam)
            for fam in ("theorem", "method", "definition")
            if any(s["family"] == fam for s in group)
        }
        n["term_row_h"] = ctx_term_row_h.get(n["id"], 0)

    return {
        "nodes": nodes, "edges": edges, "over": over,
        "statements": placed, "terms": placed_terms,
        "term_use_edges": term_use_edges, "disambiguation_edges": disambiguation_edges,
        "canvas": {"w": round(canvas_w), "h": PAD * 2 + (max(layers) + 1) * ROW_H},
        "maxDepth": max(layers), "rowH": ROW_H, "nodeH": NODE_H, "pad": PAD,
        "meta": data.get("provenance", {}),
        "scope": data.get("scope", ""),
    }


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

PAGE = """<title>Context Lattice · ODE, Calculus, Linear Algebra</title>
<style>
  :root {
    --ground:#F6F7F9; --surface:#FFFFFF; --surface-2:#EFF2F6;
    --ink:#12151C; --muted:#5A6472; --faint:#8B94A3;
    --rule:#DDE1E8; --rule-strong:#C4CBD6;
    --accent:#2B5FD9; --accent-soft:#E4EBFB;
    --c-foundations:#6B7789; --c-linear:#B0761A; --c-analysis:#177C7C;
    --c-calculus:#6F4CBC; --c-ode:#C43F36;
    --edge:#B8C0CC; --edge-weak:#D6DBE3;
    --term-ok:#2F8F5B; --term-bad:#C43F36;
    --shadow:0 1px 2px rgba(18,21,28,.06), 0 8px 24px rgba(18,21,28,.06);
    --serif: ui-serif, "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif;
    --sans: ui-sans-serif, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --mono: ui-monospace, SFMono-Regular, "SF Mono", "Cascadia Mono", Consolas, "Liberation Mono", monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --ground:#0D1017; --surface:#151A23; --surface-2:#1B212C;
      --ink:#E6E9EF; --muted:#98A2B3; --faint:#6D7889;
      --rule:#262D3A; --rule-strong:#39424F;
      --accent:#6E9BFF; --accent-soft:#1B2740;
      --c-foundations:#94A0B2; --c-linear:#E0A33C; --c-analysis:#3FB3B3;
      --c-calculus:#A98BE8; --c-ode:#F2685C;
      --edge:#3B4453; --edge-weak:#2A313D;
      --term-ok:#4CB37C; --term-bad:#F2685C;
      --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
    }
  }
  :root[data-theme="dark"] {
    --ground:#0D1017; --surface:#151A23; --surface-2:#1B212C;
    --ink:#E6E9EF; --muted:#98A2B3; --faint:#6D7889;
    --rule:#262D3A; --rule-strong:#39424F;
    --accent:#6E9BFF; --accent-soft:#1B2740;
    --c-foundations:#94A0B2; --c-linear:#E0A33C; --c-analysis:#3FB3B3;
    --c-calculus:#A98BE8; --c-ode:#F2685C;
    --edge:#3B4453; --edge-weak:#2A313D;
    --term-ok:#4CB37C; --term-bad:#F2685C;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
  }

  * { box-sizing:border-box; }
  body {
    margin:0; background:var(--ground); color:var(--ink);
    font-family:var(--sans); font-size:15px; line-height:1.55;
    -webkit-font-smoothing:antialiased;
  }
  .wrap { display:flex; flex-direction:column; min-height:100vh; }

  header {
    display:flex; flex-wrap:wrap; align-items:baseline; gap:.5rem 1.25rem;
    padding:1.4rem 1.75rem 1rem; border-bottom:1px solid var(--rule);
    background:var(--surface);
  }
  h1 { font-family:var(--serif); font-size:1.5rem; font-weight:600; margin:0; letter-spacing:-.01em; }
  .sub { color:var(--muted); font-size:.85rem; }
  .stats { margin-left:auto; display:flex; gap:1.5rem; font-family:var(--mono);
           font-size:.75rem; font-variant-numeric:tabular-nums; color:var(--muted); }
  .stats b { display:block; color:var(--ink); font-size:1.05rem; font-weight:600; }

  .controls {
    display:flex; flex-wrap:wrap; align-items:center; gap:.5rem .75rem;
    padding:.7rem 1.75rem; border-bottom:1px solid var(--rule);
    background:var(--surface-2); font-size:.8rem;
  }
  .ctl-label { text-transform:uppercase; letter-spacing:.07em; font-size:.68rem;
               color:var(--faint); font-weight:600; }
  .chip {
    display:inline-flex; align-items:center; gap:.4rem; padding:.28rem .6rem;
    border:1px solid var(--rule-strong); border-radius:100px; background:var(--surface);
    color:var(--muted); cursor:pointer; font:inherit; font-size:.78rem;
    transition:background .12s, color .12s, border-color .12s;
  }
  .chip:hover { border-color:var(--accent); color:var(--ink); }
  .chip:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
  .chip[aria-pressed="true"] { background:var(--accent-soft); border-color:var(--accent); color:var(--ink); }
  .chip .dot { width:9px; height:9px; border-radius:50%; background:currentColor; }
  .sep { width:1px; align-self:stretch; background:var(--rule-strong); margin:0 .35rem; }

  main { display:flex; flex:1; min-height:0; align-items:stretch; }
  .canvas-scroll { flex:1; overflow:auto; position:relative; }
  .gutter-label {
    position:sticky; left:0; top:0; z-index:2; pointer-events:none;
    display:flex; justify-content:space-between; padding:.45rem .9rem;
    font-family:var(--mono); font-size:.66rem; letter-spacing:.06em;
    text-transform:uppercase; color:var(--faint);
    background:linear-gradient(var(--ground), transparent);
  }
  svg { display:block; }
  .row-rule { stroke:var(--rule); stroke-width:1; }
  .depth-tick { font-family:var(--mono); font-size:10px; fill:var(--faint);
                font-variant-numeric:tabular-nums; }

  .edge { fill:none; stroke:var(--edge); stroke-width:1.4; }
  .edge.single { stroke:var(--edge-weak); stroke-dasharray:3 3; }
  .edge.lit { stroke:var(--accent); stroke-width:2.2; stroke-dasharray:none; }
  .edge.dim { opacity:.14; }
  .edge.hidden { display:none; }

  /* `over` is parameterisation, not order — distinguished by form, not hue,
     so it never competes with the course palette. */
  .over-edge { fill:none; stroke:var(--ink); stroke-width:1.1; opacity:.34;
               stroke-dasharray:1 4; stroke-linecap:round; }
  .over-cap { fill:none; stroke:var(--ink); stroke-width:1.1; opacity:.5; }
  .over-edge.hidden, .over-cap.hidden { display:none; }
  .over-edge.lit { stroke:var(--accent); opacity:1; stroke-width:1.8; }
  .over-cap.lit { stroke:var(--accent); opacity:1; }
  .over-edge.dim, .over-cap.dim { opacity:.07; }

  /* Statements sit beneath the context that holds them. Their coordinates come
     from the lattice, so nothing about where they land is guessed. */
  .stmt { cursor:pointer; }
  .stmt-mark { stroke:var(--surface); stroke-width:1.1; fill:var(--ink); }
  .stmt.definition .stmt-mark { fill:none; stroke:var(--ink); stroke-width:1.5; }
  .stmt.false .stmt-mark { fill:var(--c-ode); stroke:var(--c-ode); }
  .stmt:hover .stmt-mark, .stmt.sel .stmt-mark { fill:var(--accent); stroke:var(--accent); }
  .stmt.hidden { display:none; }
  .stmt.dim { opacity:.15; }
  .node.populated rect { stroke:var(--ink); stroke-width:1.8; }
  .count { font-family:var(--mono); font-size:9.5px; fill:var(--faint); }

  /* Dense contexts (>6 statements) collapse to a badge: a count broken down by
     role-family instead of an undifferentiated wall of dots. Click to expand. */
  .stmt-badge { cursor:pointer; }
  .stmt-badge rect { fill:var(--surface-2); stroke:var(--rule-strong); rx:8; }
  .stmt-badge:hover rect { stroke:var(--accent); }
  .stmt-badge text { font-family:var(--mono); font-size:9.5px; fill:var(--muted); }
  .stmt-badge .fam-theorem { fill:var(--ink); }
  .stmt-badge .fam-method { fill:var(--accent); }
  .stmt-badge .fam-definition { fill:var(--faint); }
  .stmt-badge.hidden { display:none; }
  .stmt-badge.dim { opacity:.15; }

  /* Terms: the vocabulary layer, drawn between a context and the statements
     that use it. Dashed border marks them as a different kind of thing from a
     context (a defined name, not a theory). */
  .term { cursor:pointer; }
  .term rect { rx:8; fill:var(--surface); stroke:var(--rule-strong);
               stroke-width:1; stroke-dasharray:2.5 2; }
  .term text { font-size:9.5px; fill:var(--muted); dominant-baseline:middle; }
  .term:hover rect, .term.sel rect { stroke:var(--accent); fill:var(--accent-soft); }
  .term:focus-visible rect { outline:none; stroke:var(--accent); stroke-width:2; }
  .term.hidden { display:none; }
  .term.dim { opacity:.18; }
  .term.lit rect { stroke:var(--accent); stroke-width:1.6; }

  /* A statement -> term usage link. Green when the term is actually visible
     from the statement's context (defined there or in an ancestor); red when
     it is not — the same check validate.py's term-not-visible gate runs, now
     drawn instead of only logged. */
  .term-use { fill:none; stroke-width:1; opacity:.45; }
  .term-use.valid { stroke:var(--term-ok); }
  .term-use.invalid { stroke:var(--term-bad); stroke-dasharray:2 3; opacity:.7; }
  .term-use.hidden { display:none; }
  .term-use.dim { opacity:.08; }
  .term-use.lit { opacity:1; stroke-width:1.8; }

  /* Two terms with the same name in different contexts — the disambiguation
     case. This is the feature working, not an error: Model B's identity is
     (name, context), so these can never merge, and this link is how you see
     that two "Wronskian"s are deliberately kept apart. */
  .disambig { fill:none; stroke:var(--faint); stroke-width:1; stroke-dasharray:1 3;
              opacity:.55; }
  .disambig.hidden { display:none; }
  .disambig.dim { opacity:.1; }
  .disambig.lit { stroke:var(--accent); opacity:1; }

  .node rect { rx:6; fill:var(--surface); stroke:var(--rule-strong); stroke-width:1; }
  .node text { font-size:12.5px; fill:var(--ink); dominant-baseline:middle; }
  .node { cursor:pointer; }
  .node .swatch { rx:2; }
  .node:focus-visible rect { outline:none; stroke:var(--accent); stroke-width:2.5; }
  .node.lit rect { stroke:var(--accent); stroke-width:2; }
  .node.sel rect { fill:var(--accent-soft); stroke:var(--accent); stroke-width:2.5; }
  .node.dim { opacity:.2; }

  aside {
    width:340px; flex:none; border-left:1px solid var(--rule); background:var(--surface);
    padding:1.4rem 1.4rem 2rem; overflow-y:auto;
  }
  aside h2 { font-family:var(--serif); font-size:1.15rem; margin:.15rem 0 .1rem; font-weight:600; }
  .kicker { font-family:var(--mono); font-size:.68rem; letter-spacing:.08em;
            text-transform:uppercase; color:var(--faint); }
  .id { font-family:var(--mono); font-size:.76rem; color:var(--muted); word-break:break-all; }
  .panel-sec { margin-top:1.35rem; }
  .panel-sec h3 { font-size:.7rem; text-transform:uppercase; letter-spacing:.08em;
                  color:var(--faint); margin:0 0 .5rem; font-weight:600; }
  .rel { display:flex; flex-direction:column; gap:.3rem; }
  .rel button {
    display:flex; justify-content:space-between; align-items:center; gap:.5rem;
    width:100%; text-align:left; padding:.35rem .55rem; border:1px solid var(--rule);
    border-radius:5px; background:var(--surface); color:var(--ink); cursor:pointer;
    font:inherit; font-size:.82rem;
  }
  .rel button:hover { border-color:var(--accent); background:var(--accent-soft); }
  .rel button:focus-visible { outline:2px solid var(--accent); outline-offset:1px; }
  .tier { font-family:var(--mono); font-size:.62rem; letter-spacing:.05em;
          text-transform:uppercase; color:var(--faint); white-space:nowrap; }
  .tier.ok { color:var(--c-analysis); }
  .tier.weak { color:var(--c-linear); }
  .empty { color:var(--faint); font-size:.82rem; font-style:italic; }
  .note { color:var(--muted); font-size:.78rem; line-height:1.5; }
  a { color:var(--accent); }

  @media (max-width:900px) {
    main { flex-direction:column; }
    aside { width:auto; border-left:none; border-top:1px solid var(--rule); }
    .stats { width:100%; margin-left:0; }
  }
  @media (prefers-reduced-motion:reduce) { * { transition:none !important; } }
</style>

<div class="wrap">
  <header>
    <div>
      <h1>Context Lattice</h1>
      <div class="sub">__SCOPE__ &middot; ordered by axiom inclusion</div>
    </div>
    <div class="stats">
      <div>contexts<b id="s-nodes">0</b></div>
      <div>relations<b id="s-edges">0</b></div>
      <div>statements<b id="s-stmts">0</b></div>
      <div>terms<b id="s-terms">0</b></div>
      <div>populated<b id="s-pop">0</b></div>
      <div>depth<b id="s-depth">0</b></div>
    </div>
  </header>

  <div class="controls">
    <span class="ctl-label">Courses</span>
    <span id="course-chips" style="display:flex;gap:.4rem;flex-wrap:wrap"></span>
    <span class="sep"></span>
    <button class="chip" id="tier-toggle" aria-pressed="false">
      Trusted spine only
    </button>
    <button class="chip" id="over-toggle" aria-pressed="true">
      Show <em style="font-style:italic">over</em> parameters
    </button>
    <button class="chip" id="stmt-toggle" aria-pressed="true">
      Show statements
    </button>
    <button class="chip" id="term-toggle" aria-pressed="true">
      Show terms &amp; links
    </button>
    <button class="chip" id="empty-toggle" aria-pressed="false">
      Populated contexts only
    </button>
    <span class="note" style="margin-left:auto">
      Height is the relation &mdash; a context sits below everything it assumes. No arrowheads needed.
    </span>
  </div>

  <main>
    <div class="canvas-scroll">
      <div class="gutter-label"><span>&uarr; more general</span><span>more structure &darr;</span></div>
      <svg id="svg" role="img" aria-label="Hasse diagram of mathematical contexts ordered by axiom inclusion"></svg>
    </div>
    <aside id="panel"></aside>
  </main>
</div>

<script id="lattice-data" type="application/json">__DATA__</script>
<script>
(function () {
  const D = JSON.parse(document.getElementById('lattice-data').textContent);
  const svg = document.getElementById('svg');
  const NS = 'http://www.w3.org/2000/svg';
  const COURSE_VAR = {
    'foundations':'--c-foundations', 'linear algebra':'--c-linear',
    'analysis':'--c-analysis', 'calculus':'--c-calculus', 'ode':'--c-ode'
  };

  const byId = new Map(D.nodes.map(n => [n.id, n]));
  const parents = new Map(D.nodes.map(n => [n.id, []]));
  const children = new Map(D.nodes.map(n => [n.id, []]));
  D.edges.forEach(e => { parents.get(e.from).push(e); children.get(e.to).push(e); });
  const overOut = new Map(D.nodes.map(n => [n.id, []]));
  const overIn = new Map(D.nodes.map(n => [n.id, []]));
  D.over.forEach(e => { overOut.get(e.from).push(e); overIn.get(e.to).push(e); });

  const stmtsByCtx = new Map();
  (D.statements || []).forEach(s => {
    if (!stmtsByCtx.has(s.context)) stmtsByCtx.set(s.context, []);
    stmtsByCtx.get(s.context).push(s);
  });

  document.getElementById('s-nodes').textContent = D.nodes.length;
  document.getElementById('s-edges').textContent = D.edges.length;
  document.getElementById('s-stmts').textContent = (D.statements || []).length;
  document.getElementById('s-terms').textContent = (D.terms || []).length;
  document.getElementById('s-pop').textContent = stmtsByCtx.size + ' / ' + D.nodes.length;
  document.getElementById('s-depth').textContent = D.maxDepth + 1;

  // ---- draw -------------------------------------------------------------
  svg.setAttribute('width', D.canvas.w);
  svg.setAttribute('height', D.canvas.h);
  svg.setAttribute('viewBox', `0 0 ${D.canvas.w} ${D.canvas.h}`);

  const gRules = el('g'), gOver = el('g'), gEdges = el('g'), gTermLinks = el('g'),
        gNodes = el('g'), gTerms = el('g'), gStmts = el('g');
  svg.append(gRules, gOver, gEdges, gTermLinks, gNodes, gTerms, gStmts);

  for (let d = 0; d <= D.maxDepth; d++) {
    const y = D.pad + d * D.rowH + D.nodeH / 2;
    const line = el('line', { x1: 30, y1: y, x2: D.canvas.w - 12, y2: y, class: 'row-rule' });
    line.setAttribute('opacity', '.5');
    gRules.append(line);
    gRules.append(el('text', { x: 8, y: y + 3.5, class: 'depth-tick' }, String(d)));
  }

  const edgeEls = new Map();
  D.edges.forEach(e => {
    const a = byId.get(e.from), b = byId.get(e.to);
    const x1 = a.x + a.w / 2, y1 = a.y;
    const x2 = b.x + b.w / 2, y2 = b.y + b.h;
    const my = (y1 + y2) / 2;
    const p = el('path', {
      d: `M${x1},${y1} C${x1},${my} ${x2},${my} ${x2},${y2}`,
      class: 'edge ' + (e.tier === 'single' ? 'single' : '')
    });
    gEdges.append(p);
    edgeEls.set(e.from + '>' + e.to, p);
  });

  // `over` edges join the sides of two boxes: they are not vertical structure,
  // so they must not read as one. Hollow cap marks the parameter end.
  const overEls = new Map();
  D.over.forEach(e => {
    const a = byId.get(e.from), b = byId.get(e.to);
    const aRight = a.x + a.w / 2 < b.x + b.w / 2;
    const x1 = aRight ? a.x + a.w : a.x, y1 = a.y + a.h / 2;
    const x2 = aRight ? b.x : b.x + b.w, y2 = b.y + b.h / 2;
    const bow = Math.min(70, Math.abs(y2 - y1) * .45 + 22) * (aRight ? 1 : -1);
    const p = el('path', {
      d: `M${x1},${y1} C${x1 + bow},${y1} ${x2 - bow},${y2} ${x2},${y2}`,
      class: 'over-edge'
    });
    const cap = el('circle', { cx: x2, cy: y2, r: 2.6, class: 'over-cap' });
    gOver.append(p, cap);
    overEls.set(e.from + '~' + e.to, [p, cap]);
  });

  const nodeEls = new Map();
  D.nodes.forEach(n => {
    const g = el('g', { class: 'node', tabindex: '0', role: 'button',
                        'aria-label': n.name + ', depth ' + n.depth });
    const col = `var(${COURSE_VAR[n.course]})`;
    g.append(el('rect', { x: n.x, y: n.y, width: n.w, height: n.h }));
    g.append(el('rect', { x: n.x + 7, y: n.y + n.h / 2 - 4.5, width: 4, height: 9,
                          class: 'swatch', fill: col }));
    const t = el('text', { x: n.x + 17, y: n.y + n.h / 2 }, n.name);
    g.append(t);
    if (n.n_statements) {
      g.classList.add('populated');
      g.append(el('text', { x: n.x + n.w - 7, y: n.y + n.h / 2 + 3,
                            class: 'count', 'text-anchor': 'end' }, String(n.n_statements)));
    }
    gNodes.append(g);
    nodeEls.set(n.id, g);

    g.addEventListener('mouseenter', () => { if (!pinned) light(n.id); });
    g.addEventListener('mouseleave', () => { if (!pinned) clear(); });
    g.addEventListener('focus', () => { if (!pinned) light(n.id); });
    g.addEventListener('click', () => select(n.id));
    g.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); select(n.id); }
    });
  });

  // ---- terms: the vocabulary layer ---------------------------------------
  const termEls = new Map();
  const termById = new Map((D.terms || []).map(t => [t.key, t]));

  (D.terms || []).forEach(t => {
    const g = el('g', { class: 'term', tabindex: '0', role: 'button',
                        'aria-label': `${t.name}, defined in ${t.context}` });
    g.append(el('rect', { x: t.x, y: t.y, width: t.w, height: t.h }));
    const label = t.name.length > 16 ? t.name.slice(0, 15) + '…' : t.name;
    g.append(el('text', { x: t.x + t.w / 2, y: t.y + t.h / 2, 'text-anchor': 'middle' }, label));
    g.append(el('title', {}, `${t.name} (${t.kind})\ndefined in ${t.context}${t.definition_latex ? '\n' + t.definition_latex : ''}`));
    gTerms.append(g);
    termEls.set(t.key, g);
    g.addEventListener('mouseenter', () => { if (!pinned) lightTerm(t.key); });
    g.addEventListener('mouseleave', () => { if (!pinned) clear(); });
    g.addEventListener('click', ev => { ev.stopPropagation(); selectTerm(t.key); });
    g.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); selectTerm(t.key); }
    });
  });

  // Definition edge: context -> its own terms. Short and always valid, so no
  // colour coding needed — it exists mainly to visually anchor the term row.
  const defEdgeEls = new Map();
  (D.terms || []).forEach(t => {
    const host = byId.get(t.context);
    if (!host) return;
    const x = t.x + t.w / 2, y1 = host.y + host.h, y2 = t.y;
    const p = el('path', {
      d: `M${x},${y1} L${x},${y2}`, class: 'term-use valid', 'stroke-dasharray': '1 2',
    });
    gTermLinks.append(p);
    defEdgeEls.set(t.key, p);
  });

  // Usage edges: a statement cites a term. Green = the term is actually
  // visible from that context (defined there or in an ancestor); red dashed =
  // it is not — the exact case validate.py's term-not-visible gate flags,
  // drawn instead of only logged. A statement can sit above or below its
  // term's context depending on which direction the citation runs, so the
  // curve bows toward whichever side has more vertical room.
  const termUseEls = [];
  (D.term_use_edges || []).forEach(u => {
    const t = termById.get(u.term);
    const stmtNode = stmtById.get(u.statement_id);
    if (!t || !stmtNode) return;
    const x1 = t.x + t.w / 2, y1 = t.y + t.h;
    const x2 = stmtNode.x, y2 = stmtNode.y;
    const my = (y1 + y2) / 2;
    const p = el('path', {
      d: `M${x1},${y1} C${x1},${my} ${x2},${my} ${x2},${y2}`,
      class: 'term-use ' + (u.valid ? 'valid' : 'invalid'),
    });
    p.append(el('title', {}, `${t.name} used by: ${u.statement_slogan}` +
      (u.valid ? '' : '\n⚠ not visible from this context — likely a missing lattice relation')));
    gTermLinks.append(p);
    termUseEls.push({ term: u.term, stmt: u.statement_id, el: p });
  });

  // Disambiguation: two terms, same name, different context — never merged.
  const disambigEls = [];
  (D.disambiguation_edges || []).forEach(d => {
    const a = termById.get(d.a), b = termById.get(d.b);
    if (!a || !b) return;
    const x1 = a.x + a.w, y1 = a.y + a.h / 2, x2 = b.x, y2 = b.y + b.h / 2;
    const p = el('path', { d: `M${x1},${y1} L${x2},${y2}`, class: 'disambig' });
    p.append(el('title', {}, `"${d.name}" — same name, different context. Kept apart on purpose.`));
    gTermLinks.append(p);
    disambigEls.push({ a: d.a, b: d.b, el: p });
  });

  function lightTerm(key) {
    termEls.forEach((g, k) => g.classList.toggle('lit', k === key));
    termUseEls.forEach(u => u.el.classList.toggle('lit', u.term === key));
    disambigEls.forEach(d => d.el.classList.toggle('lit', d.a === key || d.b === key));
  }

  // Shape encodes role-family (a fact vs a recipe vs a definition); fill/outline
  // still encodes status (theorem/definition/false). Two independent channels.
  const FAM_LABEL = { theorem: 'Thm', method: 'Method', definition: 'Def' };
  function markFor(family, x, y) {
    if (family === 'method') {
      const s = 5;
      return el('path', { class: 'stmt-mark',
        d: `M${x},${y - s} L${x + s},${y} L${x},${y + s} L${x - s},${y} Z` });
    }
    if (family === 'definition') {
      const s = 3.6;
      return el('rect', { class: 'stmt-mark', x: x - s, y: y - s, width: s * 2, height: s * 2 });
    }
    return el('circle', { class: 'stmt-mark', cx: x, cy: y, r: 4 });
  }

  const DENSE_THRESHOLD = 6;
  const expanded = new Set();   // context ids the user has expanded past the badge

  const stmtEls = new Map();
  const badgeEls = new Map();
  const stmtById = new Map((D.statements || []).map(s => [s.id, s]));

  function drawStatement(st) {
    const cls = st.status === 'FALSE' ? 'false'
              : st.status === 'DEFINITION' ? 'definition' : 'theorem';
    const g = el('g', { class: 'stmt ' + cls, tabindex: '0', role: 'button',
                        'aria-label': st.slogan });
    g.append(markFor(st.family, st.x, st.y));
    g.append(el('title', {}, `${st.status} · ${st.role || ''} · ${st.sub_tag} · ${st.context}\n${st.slogan}`));
    gStmts.append(g);
    stmtEls.set(st.id, g);
    g.addEventListener('click', ev => { ev.stopPropagation(); selectStmt(st.id); });
    g.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); selectStmt(st.id); }
    });
    g.classList.toggle('hidden', !showStmts);
  }

  function drawBadge(cid, host, counts) {
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    const parts = Object.entries(counts).map(([f, n]) => `${n} ${FAM_LABEL[f]}`);
    const w = Math.max(58, 14 + parts.join(' · ').length * 5.6);
    const x = host.x + host.w / 2 - w / 2, y = host.y + host.h + (host.term_row_h || 0) + 8;
    const g = el('g', { class: 'stmt-badge', tabindex: '0', role: 'button',
                        'aria-label': `${total} statements: ${parts.join(', ')}. Click to expand.` });
    g.append(el('rect', { x, y, width: w, height: 17 }));
    let tx = x + 7;
    Object.entries(counts).forEach(([fam, n], i) => {
      if (i > 0) {
        const sep = el('text', { x: tx, y: y + 12 }, '·');
        sep.setAttribute('fill', 'var(--rule-strong)');
        g.append(sep);
        tx += 8;
      }
      g.append(el('text', { x: tx, y: y + 12, class: 'fam-' + fam }, String(n)));
      tx += String(n).length * 5.6 + 2;
      const lbl = el('text', { x: tx, y: y + 12 }, FAM_LABEL[fam]);
      g.append(lbl);
      tx += FAM_LABEL[fam].length * 5.6 + 6;
    });
    gStmts.append(g);
    badgeEls.set(cid, g);
    const toggle = ev => { ev.stopPropagation(); expanded.add(cid); refreshDensity(); };
    g.addEventListener('click', toggle);
    g.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggle(ev); }
    });
  }

  function refreshDensity() {
    stmtEls.forEach(g => g.remove());
    badgeEls.forEach(g => g.remove());
    stmtEls.clear();
    badgeEls.clear();

    D.nodes.forEach(n => {
      const group = (D.statements || []).filter(s => s.context === n.id);
      if (!group.length) return;
      if (group.length > DENSE_THRESHOLD && !expanded.has(n.id)) {
        drawBadge(n.id, n, n.family_counts || {});
      } else {
        group.forEach(drawStatement);
      }
    });
    applyFilters();
  }

  // ---- highlight --------------------------------------------------------
  let pinned = null, pinnedStmt = null, pinnedTerm = null;

  function walk(id, map, key) {
    const seen = new Set(), edges = new Set(), stack = [id];
    while (stack.length) {
      const cur = stack.pop();
      for (const e of map.get(cur) || []) {
        const nxt = e[key];
        edges.add(e.from + '>' + e.to);
        if (!seen.has(nxt)) { seen.add(nxt); stack.push(nxt); }
      }
    }
    return { seen, edges };
  }

  function light(id) {
    const up = walk(id, parents, 'to');
    const down = walk(id, children, 'from');
    const keep = new Set([id, ...up.seen, ...down.seen]);
    const keepE = new Set([...up.edges, ...down.edges]);

    nodeEls.forEach((g, nid) => {
      g.classList.toggle('dim', !keep.has(nid));
      g.classList.toggle('lit', keep.has(nid) && nid !== id);
      g.classList.toggle('sel', nid === id);
    });
    edgeEls.forEach((p, k) => {
      p.classList.toggle('lit', keepE.has(k));
      p.classList.toggle('dim', !keepE.has(k));
    });
    const ownOver = new Set([
      ...overOut.get(id).map(e => e.from + '~' + e.to),
      ...overIn.get(id).map(e => e.from + '~' + e.to),
    ]);
    overEls.forEach((els, k) => els.forEach(x => {
      x.classList.toggle('lit', ownOver.has(k));
      x.classList.toggle('dim', !ownOver.has(k));
    }));
    stmtEls.forEach((g, sid) => g.classList.toggle('dim', !keep.has(stmtById.get(sid).context)));
    badgeEls.forEach((g, cid) => g.classList.toggle('dim', !keep.has(cid)));
    termEls.forEach((g, key) => g.classList.toggle('dim', !keep.has(termById.get(key).context)));
    defEdgeEls.forEach((p, key) => p.classList.toggle('dim', !keep.has(termById.get(key).context)));
    termUseEls.forEach(u => {
      const t = termById.get(u.term), stNode = stmtById.get(u.stmt);
      const on = t && keep.has(t.context) && stNode && keep.has(stNode.context);
      u.el.classList.toggle('dim', !on);
    });
    disambigEls.forEach(d => {
      const a = termById.get(d.a), b = termById.get(d.b);
      const on = (a && keep.has(a.context)) || (b && keep.has(b.context));
      d.el.classList.toggle('dim', !on);
    });
  }

  function clear() {
    nodeEls.forEach(g => g.classList.remove('dim', 'lit', 'sel'));
    edgeEls.forEach(p => p.classList.remove('lit', 'dim'));
    overEls.forEach(els => els.forEach(x => x.classList.remove('lit', 'dim')));
    stmtEls.forEach(g => g.classList.remove('dim'));
    badgeEls.forEach(g => g.classList.remove('dim'));
    termEls.forEach(g => g.classList.remove('dim', 'lit', 'sel'));
    defEdgeEls.forEach(p => p.classList.remove('dim'));
    termUseEls.forEach(u => u.el.classList.remove('dim', 'lit'));
    disambigEls.forEach(d => d.el.classList.remove('dim', 'lit'));
    applyFilters();
  }

  function select(id) {
    pinnedStmt = null; pinnedTerm = null;
    stmtEls.forEach(g => g.classList.remove('sel'));
    termEls.forEach(g => g.classList.remove('sel'));
    if (pinned === id) { pinned = null; clear(); renderPanel(null); return; }
    pinned = id; light(id); renderPanel(id);
  }

  function selectStmt(sid) {
    const st = stmtById.get(sid);
    if (!st) return;
    pinnedTerm = null;
    termEls.forEach(g => g.classList.remove('sel'));
    stmtEls.forEach((g, k) => g.classList.toggle('sel', k === sid));
    pinnedStmt = sid;
    pinned = st.context;
    light(st.context);
    renderStmtPanel(st);
  }

  function selectTerm(key) {
    const t = termById.get(key);
    if (!t) return;
    if (pinnedTerm === key) { pinnedTerm = null; pinned = null; clear(); renderPanel(null); return; }
    pinnedStmt = null;
    stmtEls.forEach(g => g.classList.remove('sel'));
    termEls.forEach((g, k) => g.classList.toggle('sel', k === key));
    pinnedTerm = key;
    pinned = t.context;
    light(t.context);
    lightTerm(key);
    renderTermPanel(t);
  }

  function renderTermPanel(t) {
    const uses = (D.term_use_edges || []).filter(u => u.term === t.key);
    const siblings = (D.disambiguation_edges || [])
      .filter(d => d.a === t.key || d.b === t.key)
      .map(d => termById.get(d.a === t.key ? d.b : d.a))
      .filter(Boolean);
    panel.innerHTML = `
      <span class="kicker">Term &middot; ${t.context}</span>
      <h2>${t.name}</h2>
      <div class="id">${t.kind}</div>
      ${t.definition_latex ? `<div class="panel-sec"><h3>Definition</h3>
        <p class="note" style="font-family:var(--mono);font-size:.72rem;overflow-x:auto">${t.definition_latex}</p></div>` : ''}
      <div class="panel-sec">
        <h3>Used by ${uses.length ? '(' + uses.length + ')' : ''}</h3>
        ${uses.length ? `<div class="rel">${uses.map(u => `
          <button data-goto-stmt="${u.statement_id}"><span>${u.statement_slogan}</span>
          <span class="tier ${u.valid ? 'ok' : 'weak'}">${u.valid ? u.statement_context : 'not visible'}</span></button>
        `).join('')}</div>` : '<p class="empty">not cited by any indexed statement yet</p>'}
      </div>
      ${siblings.length ? `<div class="panel-sec">
        <h3>Same name, different context</h3>
        <p class="note" style="margin-bottom:.5rem">Kept apart on purpose — Model B's identity is
          (name, context), so these can never silently merge.</p>
        <div class="rel">${siblings.map(s => `<button data-goto-term="${s.key}">
          <span>${s.name}</span><span class="tier">${s.context}</span></button>`).join('')}</div>
      </div>` : ''}`;
    panel.querySelectorAll('[data-goto-stmt]').forEach(b =>
      b.addEventListener('click', () => selectStmt(b.dataset.gotoStmt)));
    panel.querySelectorAll('[data-goto-term]').forEach(b =>
      b.addEventListener('click', () => selectTerm(b.dataset.gotoTerm)));
  }

  function renderStmtPanel(st) {
    const p = st.provenance || {};
    const where = [p.doc_title, p.page_number ? 'p. ' + p.page_number : null,
                   p.section_heading].filter(Boolean).join(' · ');
    const colour = st.status === 'FALSE' ? 'var(--c-ode)' : 'var(--ink)';
    panel.innerHTML = `
      <span class="kicker">Statement &middot; ${st.context}</span>
      <h2>${st.slogan}</h2>
      <div class="id" style="color:${colour}">${st.status}${st.role ? ' &middot; ' + st.role : ''}
        &middot; <span style="text-transform:capitalize">${st.sub_tag}</span></div>
      <p class="note" style="margin-top:.3rem">
        Grouped by role (shape) and by a probe scalar/system tag (row position) —
        a heuristic read of the hypothesis text, not yet a real classification.
      </p>
      ${st.hypotheses && st.hypotheses.length ? `
        <div class="panel-sec"><h3>Hypotheses</h3>
          <div class="rel">${st.hypotheses.map(h => `<button disabled style="cursor:default">${h}</button>`).join('')}</div>
        </div>` : ''}
      ${st.conclusion ? `<div class="panel-sec"><h3>Conclusion</h3><p class="note">${st.conclusion}</p></div>` : ''}
      ${st.statement_latex ? `<div class="panel-sec"><h3>As written</h3>
        <p class="note" style="font-family:var(--mono);font-size:.72rem;overflow-x:auto">${st.statement_latex}</p></div>` : ''}
      <div class="panel-sec"><h3>Source</h3>
        <p class="note">${where || '<span class="empty">no provenance recorded</span>'}</p>
        ${p.exact_quote ? `<p class="note" style="border-left:2px solid var(--rule-strong);padding-left:.6rem;margin-top:.5rem">${p.exact_quote}</p>` : ''}
      </div>
      <div class="panel-sec">
        <button class="chip" data-goto="${st.context}">Open context ${st.context}</button>
      </div>`;
    panel.querySelectorAll('[data-goto]').forEach(b =>
      b.addEventListener('click', () => select(b.dataset.goto)));
  }

  // ---- inspector --------------------------------------------------------
  const panel = document.getElementById('panel');

  function relList(edges, dir) {
    if (!edges.length) return '<p class="empty">none</p>';
    return '<div class="rel">' + edges.map(e => {
      const other = dir === 'up' ? e.to : e.from;
      const tier = e.tier === 'corroborated'
        ? '<span class="tier ok">' + e.sources.length + ' sources</span>'
        : '<span class="tier weak">' + e.sources.join(', ') + '</span>';
      return `<button data-goto="${other}"><span>${byId.get(other).name}</span>${tier}</button>`;
    }).join('') + '</div>';
  }

  function stmtSection(id) {
    const list = stmtsByCtx.get(id) || [];
    if (!list.length) return `<div class="panel-sec"><h3>Statements</h3>
      <p class="empty">nothing from your notes lands here yet</p></div>`;
    return `<div class="panel-sec">
      <h3>Statements from your notes</h3>
      <div class="rel">${list.map(s => `
        <button data-stmt="${s.id}"><span>${s.slogan}</span>
        <span class="tier ${s.status === 'THEOREM' ? 'ok' : 'weak'}">${s.status}</span></button>`).join('')}
      </div></div>`;
  }

  function termSection(id) {
    const list = (D.terms || []).filter(t => t.context === id);
    if (!list.length) return '';
    return `<div class="panel-sec">
      <h3>Terms defined here</h3>
      <div class="rel">${list.map(t => `
        <button data-term="${t.key}"><span>${t.name}</span>
        <span class="tier">${t.kind}</span></button>`).join('')}
      </div></div>`;
  }

  function overSection(id) {
    const out = overOut.get(id), inc = overIn.get(id);
    if (!out.length && !inc.length) return '';
    const line = (e, other, verb) =>
      `<button data-goto="${other}"><span>${verb} ${byId.get(other).name}</span>
       <span class="tier">parameter</span></button>`;
    return `<div class="panel-sec">
      <h3>Over &mdash; parameters, not order</h3>
      <div class="rel">
        ${out.map(e => line(e, e.to, 'over')).join('')}
        ${inc.map(e => line(e, e.from, 'parameterises')).join('')}
      </div>
      <p class="note" style="margin-top:.5rem">Changing this slot can change which
      theorems hold &mdash; a normal matrix over &#8450; is diagonalisable, over &#8477; it need not be.</p>
    </div>`;
  }

  function renderPanel(id) {
    if (!id) {
      panel.innerHTML = `
        <span class="kicker">Inspector</span>
        <h2>Nothing selected</h2>
        <p class="note">Hover any context to trace its full ancestry and everything
        built on top of it. Click to pin.</p>
        <div class="panel-sec">
          <h3>Reading the diagram</h3>
          <p class="note">Vertical position is longest-path depth, so a context always
          sits below every theory it assumes. Solid lines are relations two or more
          independent sources agreed on; dashed lines were claimed by one and are still
          under review.</p>
          <p class="note" style="margin-top:.6rem">Faint dotted curves are a different
          relation: <em>over</em>. A vector space is <em>over</em> a field, a normed
          space <em>over</em> &#8477; or &#8450;. These are parameters, not order, so they
          are held out of the depth calculation &mdash; folding them in routed 39 of 54
          contexts through Field and added six spurious levels.</p>
          <p class="note" style="margin-top:.6rem">Dashed boxes beneath a context are its
          <strong>terms</strong> &mdash; the vocabulary it defines. A line down to a
          statement is that term in use: green if the term is actually visible from
          there, red dashed if it isn't (a gap in the lattice). A faint dotted line
          between two terms with the same name means they were kept apart on
          purpose &mdash; identity here is (name, context), so they can never merge.</p>
        </div>`;
      return;
    }
    const n = byId.get(id);
    const wiki = n.wiki
      ? `<a href="https://en.wikipedia.org/wiki/${encodeURIComponent(n.wiki.replace(/ /g,'_'))}"
           target="_blank" rel="noopener">Wikipedia &rarr;</a>` : '';
    panel.innerHTML = `
      <span class="kicker">${n.course} &middot; depth ${n.depth}</span>
      <h2>${n.name}</h2>
      <div class="id">${n.id}</div>
      <div class="panel-sec">
        <h3>Extends &mdash; assumed by this context</h3>
        ${relList(parents.get(id), 'up')}
      </div>
      <div class="panel-sec">
        <h3>Extended by &mdash; built on this</h3>
        ${relList(children.get(id), 'down')}
      </div>
      ${overSection(id)}
      ${termSection(id)}
      ${stmtSection(id)}
      <div class="panel-sec">${wiki}</div>`;
    panel.querySelectorAll('[data-goto]').forEach(b =>
      b.addEventListener('click', () => select(b.dataset.goto)));
    panel.querySelectorAll('[data-stmt]').forEach(b =>
      b.addEventListener('click', () => selectStmt(b.dataset.stmt)));
    panel.querySelectorAll('[data-term]').forEach(b =>
      b.addEventListener('click', () => selectTerm(b.dataset.term)));
  }

  // ---- filters ----------------------------------------------------------
  const courses = [...new Set(D.nodes.map(n => n.course))].sort();
  const active = new Set(courses);
  const chipBox = document.getElementById('course-chips');
  courses.forEach(c => {
    const b = document.createElement('button');
    b.className = 'chip'; b.setAttribute('aria-pressed', 'true');
    b.innerHTML = `<span class="dot" style="color:var(${COURSE_VAR[c]})"></span>${c}`;
    b.addEventListener('click', () => {
      active.has(c) ? active.delete(c) : active.add(c);
      b.setAttribute('aria-pressed', String(active.has(c)));
      pinned = null; renderPanel(null); clear();
    });
    chipBox.append(b);
  });

  let spineOnly = false, showOver = true, showStmts = true, populatedOnly = false, showTerms = true;
  const stmtBtn = document.getElementById('stmt-toggle');
  if (stmtBtn) stmtBtn.addEventListener('click', () => {
    showStmts = !showStmts;
    stmtBtn.setAttribute('aria-pressed', String(showStmts));
    pinned = null; renderPanel(null); clear();
  });
  const termBtn = document.getElementById('term-toggle');
  if (termBtn) termBtn.addEventListener('click', () => {
    showTerms = !showTerms;
    termBtn.setAttribute('aria-pressed', String(showTerms));
    pinned = null; renderPanel(null); clear();
  });
  const emptyBtn = document.getElementById('empty-toggle');
  if (emptyBtn) emptyBtn.addEventListener('click', () => {
    populatedOnly = !populatedOnly;
    emptyBtn.setAttribute('aria-pressed', String(populatedOnly));
    pinned = null; renderPanel(null); clear();
  });

  const tierBtn = document.getElementById('tier-toggle');
  tierBtn.addEventListener('click', () => {
    spineOnly = !spineOnly;
    tierBtn.setAttribute('aria-pressed', String(spineOnly));
    pinned = null; renderPanel(null); clear();
  });
  const overBtn = document.getElementById('over-toggle');
  overBtn.addEventListener('click', () => {
    showOver = !showOver;
    overBtn.setAttribute('aria-pressed', String(showOver));
    pinned = null; renderPanel(null); clear();
  });

  function applyFilters() {
    const on = id => active.has(byId.get(id).course)
      && (!populatedOnly || (byId.get(id).n_statements || 0) > 0);
    nodeEls.forEach((g, id) => g.classList.toggle('dim', !on(id)));
    stmtEls.forEach((g, sid) => {
      const s = stmtById.get(sid);
      g.classList.toggle('hidden', !showStmts || !on(s.context));
    });
    badgeEls.forEach((g, cid) => g.classList.toggle('hidden', !showStmts || !on(cid)));
    D.edges.forEach(e => {
      edgeEls.get(e.from + '>' + e.to)
        .classList.toggle('hidden', (spineOnly && e.tier === 'single') || !(on(e.from) && on(e.to)));
    });
    D.over.forEach(e => {
      const vis = showOver && on(e.from) && on(e.to);
      overEls.get(e.from + '~' + e.to).forEach(x => x.classList.toggle('hidden', !vis));
    });
    termEls.forEach((g, key) => g.classList.toggle('hidden', !showTerms || !on(termById.get(key).context)));
    defEdgeEls.forEach((p, key) => p.classList.toggle('hidden', !showTerms || !on(termById.get(key).context)));
    termUseEls.forEach(u => {
      const t = termById.get(u.term), stNode = stmtById.get(u.stmt);
      const vis = showTerms && showStmts && t && on(t.context) && stNode && on(stNode.context);
      u.el.classList.toggle('hidden', !vis);
    });
    disambigEls.forEach(d => {
      const a = termById.get(d.a), b = termById.get(d.b);
      const vis = showTerms && a && on(a.context) && b && on(b.context);
      d.el.classList.toggle('hidden', !vis);
    });
  }

  function el(tag, attrs = {}, text) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }

  renderPanel(null);
  refreshDensity();
})();
</script>
"""


def _load_statements() -> list[dict]:
    """Flatten the atlas store into plot-ready statement records."""
    try:
        from src.atlas.store import AtlasStore
    except Exception:
        return []
    try:
        store = AtlasStore()
    except Exception as e:
        log.warning(f"No atlas store available ({e}); rendering lattice only.")
        return []

    out = []
    for s in store.statements.values():
        p = s.provenance[0].model_dump(mode="json") if s.provenance else {}
        out.append({
            "id": s.id, "context": s.context, "slogan": s.slogan,
            "status": s.status.value, "role": s.role.value if s.role else None,
            "hypotheses": s.hypotheses, "conclusion": s.conclusion,
            "statement_latex": s.statement_latex, "provenance": p,
            "uses_terms": s.uses_terms,
        })
    return out


def _load_terms() -> list[dict]:
    """Flatten the atlas store's term table into plot-ready records."""
    try:
        from src.atlas.store import AtlasStore
        store = AtlasStore()
    except Exception as e:
        log.warning(f"No atlas store available ({e}); rendering without terms.")
        return []

    out = []
    for t in store.terms.values():
        out.append({
            "key": t.key, "name": t.name, "context": t.context,
            "kind": t.kind.value, "definition_latex": t.definition_latex,
            "aliases": t.aliases, "uses_terms": t.uses_terms,
        })
    return out


def render(with_statements: bool = False, out: Path | None = None) -> Path:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    statements = _load_statements() if with_statements else []
    terms = _load_terms() if with_statements else []
    layout = build_layout(data, statements, terms)

    title = ("Atlas · statements on the context lattice" if with_statements
             else "Context Lattice · ODE, Calculus, Linear Algebra")
    scope = layout["scope"] or "Context lattice"
    if with_statements:
        scope = f"{scope} &middot; {len(statements)} statements from your notes"

    html = (PAGE
            .replace("Context Lattice · ODE, Calculus, Linear Algebra", title, 1)
            .replace("__SCOPE__", scope)
            .replace("__DATA__", json.dumps(layout, separators=(",", ":"))))

    target = out or (OUT_ATLAS if with_statements else OUT)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    log.info(f"Rendered {len(layout['nodes'])} contexts, "
             f"{len(statements)} statements, {len(terms)} terms to {target}")
    return target


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--statements", action="store_true",
                    help="plot the indexed statements onto the lattice")
    a = ap.parse_args()
    print(render(with_statements=a.statements))
