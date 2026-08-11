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
from pathlib import Path

import networkx as nx

from src.logger import log

DATA = Path(__file__).parent / "data" / "contexts.json"
OUT = Path(__file__).resolve().parents[3] / "static" / "lattice.html"

ROW_H = 74
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


def build_layout(data: dict) -> dict:
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

    return {
        "nodes": nodes, "edges": edges, "over": over,
        "canvas": {"w": round(canvas_w), "h": PAD * 2 + (max(layers) + 1) * ROW_H},
        "maxDepth": max(layers),
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
      <div>corroborated<b id="s-corr">0</b></div>
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

  document.getElementById('s-nodes').textContent = D.nodes.length;
  document.getElementById('s-edges').textContent = D.edges.length;
  document.getElementById('s-corr').textContent = D.edges.filter(e => e.tier === 'corroborated').length;
  document.getElementById('s-depth').textContent = D.maxDepth + 1;

  // ---- draw -------------------------------------------------------------
  svg.setAttribute('width', D.canvas.w);
  svg.setAttribute('height', D.canvas.h);
  svg.setAttribute('viewBox', `0 0 ${D.canvas.w} ${D.canvas.h}`);

  const gRules = el('g'), gOver = el('g'), gEdges = el('g'), gNodes = el('g');
  svg.append(gRules, gOver, gEdges, gNodes);

  for (let d = 0; d <= D.maxDepth; d++) {
    const y = 48 + d * 74 + 15;
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

  // ---- highlight --------------------------------------------------------
  let pinned = null;

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
  }

  function clear() {
    nodeEls.forEach(g => g.classList.remove('dim', 'lit', 'sel'));
    edgeEls.forEach(p => p.classList.remove('lit', 'dim'));
    overEls.forEach(els => els.forEach(x => x.classList.remove('lit', 'dim')));
    applyFilters();
  }

  function select(id) {
    if (pinned === id) { pinned = null; clear(); renderPanel(null); return; }
    pinned = id; light(id); renderPanel(id);
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
      <div class="panel-sec">${wiki}</div>`;
    panel.querySelectorAll('[data-goto]').forEach(b =>
      b.addEventListener('click', () => select(b.dataset.goto)));
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

  let spineOnly = false, showOver = true;
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
    const on = id => active.has(byId.get(id).course);
    nodeEls.forEach((g, id) => g.classList.toggle('dim', !on(id)));
    D.edges.forEach(e => {
      edgeEls.get(e.from + '>' + e.to)
        .classList.toggle('hidden', (spineOnly && e.tier === 'single') || !(on(e.from) && on(e.to)));
    });
    D.over.forEach(e => {
      const vis = showOver && on(e.from) && on(e.to);
      overEls.get(e.from + '~' + e.to).forEach(x => x.classList.toggle('hidden', !vis));
    });
  }

  function el(tag, attrs = {}, text) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }

  renderPanel(null);
  applyFilters();
})();
</script>
"""


def render() -> Path:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    layout = build_layout(data)
    html = (PAGE
            .replace("__SCOPE__", layout["scope"] or "Context lattice")
            .replace("__DATA__", json.dumps(layout, separators=(",", ":"))))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    log.info(f"Rendered {len(layout['nodes'])} contexts to {OUT}")
    return OUT


if __name__ == "__main__":
    print(render())
