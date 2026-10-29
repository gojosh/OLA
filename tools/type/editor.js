// The proof page's point editor (tools/type/type.py inlines this file into the page).
//
// Each constructed glyph on the page carries its construction's outline (plate pixels, y down) and
// the adjustments saved for it: moves of single control points, keyed by contour, segment and point.
// Dragging a node or handle adds to those moves, with a type designer's habits: a node carries its
// handles; a smooth node's other handle turns to stay in line; a handle at an extreme stays flat or
// upright (hold Alt to free it); a mirrored letter stays mirrored; lines stay lines. Saving writes
// fonts/<family>/adjustments/<glyph>.json through the local server (type.py serve); the build applies
// the moves after fitting, by the same rules (construct.adjust).
(function () {
  const API = `/api/${FAMILY}`;
  let api = false;
  fetch(`${API}/status`, { cache: 'no-store' }).then(r => { api = r.ok; document.documentElement.classList.toggle('has-api', api); }).catch(() => {});

  const NS = 'http://www.w3.org/2000/svg';
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const mul = (a, k) => [a[0] * k, a[1] * k];
  const len = a => Math.hypot(a[0], a[1]);
  const deg = a => Math.atan2(a[1], a[0]) * 180 / Math.PI;
  const clone = x => JSON.parse(JSON.stringify(x));
  const turn = (a, b) => { const la = len(a), lb = len(b); if (la < 1e-9 || lb < 1e-9) return 0;
    return Math.acos(Math.max(-1, Math.min(1, (a[0] * b[0] + a[1] * b[1]) / (la * lb)))) * 180 / Math.PI; };
  const flatOrUpright = v => { const a = Math.abs(deg(v)) % 90; return Math.min(a, 90 - a) < 0.5; };
  const bez = (q, t) => { const u = 1 - t; return [0, 1].map(k => u * u * u * q[0][k] + 3 * u * u * t * q[1][k] + 3 * u * t * t * q[2][k] + t * t * t * q[3][k]); };
  function extremaTs(q) {                              // where x or y turns back inside the curve
    const ts = [];
    for (const k of [0, 1]) {
      const [p0, p1, p2, p3] = q.map(p => p[k]);
      const a = -p0 + 3 * p1 - 3 * p2 + p3, b = 2 * (p0 - 2 * p1 + p2), c = p1 - p0;
      let roots = [];
      if (Math.abs(a) < 1e-12) { if (Math.abs(b) > 1e-12) roots = [-c / b]; }
      else { const disc = b * b - 4 * a * c; if (disc >= 0) { const s = Math.sqrt(disc); roots = [(-b + s) / (2 * a), (-b - s) / (2 * a)]; } }
      for (const r of roots) if (r > 0.02 && r < 0.98) ts.push(r);
    }
    return ts;
  }
  function swell(q) {                                  // how far a curve bulges past its nodes (px)
    const lo = [Math.min(q[0][0], q[3][0]), Math.min(q[0][1], q[3][1])], hi = [Math.max(q[0][0], q[3][0]), Math.max(q[0][1], q[3][1])];
    let m = 0;
    for (let i = 1; i < 64; i++) { const p = bez(q, i / 64); for (const k of [0, 1]) m = Math.max(m, lo[k] - p[k], p[k] - hi[k]); }
    return m;
  }
  function isLine(q) {
    const d = sub(q[3], q[0]), L = len(d);
    if (L < 1e-9) return false;
    return [1, 2].every(k => { const v = sub(q[k], q[0]); return Math.abs(v[0] * d[1] - v[1] * d[0]) / L < 1e-6; });
  }

  let active = null;     // the glyph the arrow keys move

  function Glyph(fig) {
    const data = JSON.parse(fig.querySelector('script.edit-data').textContent);
    const svg = fig.querySelector('.ov-wrap svg');
    const path = svg.querySelector('.L-outline');
    const nodesEl = svg.querySelector('.L-nodes');
    const bar = fig.querySelector('.edit-bar'), status = bar.querySelector('.edit-status'), info = fig.querySelector('.edit-info');
    const base = data.base, mir = data.mirrored, axis = data.axis, scale = data.scale;
    const lineSeg = base.map(c => c.map(isLine));
    let edits = new Map(data.points.map(p => [`${p.contour}/${p.segment}/${p.point}`, [p.dx, p.dy]]));
    let saved = key(), cur = null, sel = null, drag = null, editing = false;
    const history = [];
    const stale = data.stale || 0;

    function key() { return JSON.stringify([...edits].sort()); }

    function compute() {
      const out = clone(base);
      for (const [k, d] of edits) { const [c, s, p] = k.split('/').map(Number); if (out[c] && out[c][s]) out[c][s][p] = add(out[c][s][p], d); }
      out.forEach((cont, c) => {
        cont.forEach((q, s) => { if (lineSeg[c][s]) { const d = sub(q[3], q[0]); q[1] = add(q[0], mul(d, 1 / 3)); q[2] = add(q[0], mul(d, 2 / 3)); } });
        const m = mir[c];
        if (m == null) return;
        cont[0][0][0] = axis; cont[0][1][1] = cont[0][0][1];
        cont[m - 1][3][0] = axis; cont[m - 1][2][1] = cont[m - 1][3][1];
        for (let i = 0; i < m; i++) cont[2 * m - 1 - i] = cont[i].map(p => [2 * axis - p[0], p[1]]).reverse();
      });
      return out;
    }

    // A point given in the whole contour, as the build stores it: a mirrored contour's right half is
    // made from its left, so a move there is the mirrored move of its partner on the left.
    function canonical(c, s, p, d) {
      const m = mir[c];
      return (m != null && s >= m) ? [c, 2 * m - 1 - s, 3 - p, [-d[0], d[1]]] : [c, s, p, d];
    }

    function apply(moves) {
      const acc = new Map();
      for (const [c, s, p, d] of moves) {
        const [cc, ss, pp, dd] = canonical(c, s, p, d), k = `${cc}/${ss}/${pp}`, a = acc.get(k);
        acc.set(k, a ? { d: add(a.d, dd), n: a.n + 1 } : { d: dd, n: 1 });   // a node on the axis is reached from both sides
      }
      for (const [k, a] of acc) {
        const v = add(edits.get(k) || [0, 0], mul(a.d, 1 / a.n));
        if (Math.abs(v[0]) < 1e-4 && Math.abs(v[1]) < 1e-4) edits.delete(k); else edits.set(k, v);
      }
    }

    function moves(c, s, p, d, free) {
      const m = base[c].length, q = cur[c];
      if (p === 0) {                                     // a node carries its handles
        const r = (s - 1 + m) % m;
        return [[c, s, 0, d], [c, r, 3, d], [c, s, 1, d], [c, r, 2, d]];
      }
      const [ns, np, os, op] = p === 1 ? [s, 0, (s - 1 + m) % m, 2] : [(s + 1) % m, 0, (s + 1) % m, 1];
      const node = q[ns][np], h = q[s][p], o = q[os][op];
      const v = sub(h, node);
      if (!free && flatOrUpright(v) && len(v) > 1e-6) {  // a handle at an extreme keeps its direction
        const u = mul(v, 1 / len(v)), t = d[0] * u[0] + d[1] * u[1];
        d = mul(u, t);
      }
      const out = [[c, s, p, d]];
      const smooth = turn(sub(node, o), v) < 0.5 && !lineSeg[c][os];
      if (smooth && len(sub(o, node)) > 1e-6) {          // its partner turns to stay in line
        const nv = sub(add(h, d), node);
        if (len(nv) > 1e-6) out.push([c, os, op, sub(sub(node, mul(nv, len(sub(o, node)) / len(nv))), o)]);
      }
      return out;
    }

    function move(d, free) {
      apply(moves(sel.c, sel.s, sel.p, d, free));
      render();
    }

    function toSvg(ev) {
      const pt = svg.createSVGPoint(); pt.x = ev.clientX; pt.y = ev.clientY;
      const r = pt.matrixTransform(svg.getScreenCTM().inverse());
      return [r.x, r.y];
    }

    function el(tag, attrs, parent) {
      const e = document.createElementNS(NS, tag);
      for (const k in attrs) e.setAttribute(k, attrs[k]);
      parent.appendChild(e);
      return e;
    }

    function render() {
      cur = compute();
      path.setAttribute('d', cur.map(cont => `M${cont[0][0][0].toFixed(2)} ${cont[0][0][1].toFixed(2)} ` +
        cont.map(q => `C${q[1].join(' ')} ${q[2].join(' ')} ${q[3].join(' ')}`).join(' ') + ' Z').join(' '));
      nodesEl.replaceChildren();
      const r = 2.6;
      cur.forEach((cont, c) => cont.forEach((q, s) => {
        if (!lineSeg[c][s]) [[0, 1], [3, 2]].forEach(([a, b]) => {
          if (len(sub(q[a], q[b])) < 0.3) return;
          el('line', { class: 'hl', x1: q[a][0], y1: q[a][1], x2: q[b][0], y2: q[b][1] }, nodesEl);
          const h = el('circle', { class: 'hp' + (sel && sel.c === c && sel.s === s && sel.p === b ? ' sel' : ''), cx: q[b][0], cy: q[b][1], r: 1.9 }, nodesEl);
          Object.assign(h.dataset, { c, s, p: b });
        });
      }));
      cur.forEach((cont, c) => cont.forEach((q, s) => {
        const prev = cont[(s - 1 + cont.length) % cont.length];
        const tin = len(sub(prev[3], prev[2])) > 1e-6 ? sub(prev[3], prev[2]) : sub(prev[3], prev[0]);
        const tout = len(sub(q[1], q[0])) > 1e-6 ? sub(q[1], q[0]) : sub(q[3], q[0]);
        const corner = turn(tin, tout) > 0.5;
        const cls = 'nd' + (corner ? ' corner' : '') + (sel && sel.c === c && sel.s === s && sel.p === 0 ? ' sel' : '');
        const n = corner ? el('rect', { class: cls, x: q[0][0] - r, y: q[0][1] - r, width: 2 * r, height: 2 * r }, nodesEl)
                         : el('circle', { class: cls, cx: q[0][0], cy: q[0][1], r }, nodesEl);
        Object.assign(n.dataset, { c, s, p: 0 });
        el('title', {}, n).textContent = data.names[c][s];
      }));
      // a curve that now bulges past its nodes gets a node at each extreme inside it when the build
      // runs: mark them
      let bulging = 0;
      cur.forEach((cont, c) => cont.forEach((q, s) => {
        if (swell(q) <= 0.2) return;
        const ts = extremaTs(q);
        if (!ts.length) return;
        bulging++;
        el('path', { class: 'bulge', d: `M${q[0].join(' ')} C${q[1].join(' ')} ${q[2].join(' ')} ${q[3].join(' ')}` }, nodesEl);
        ts.forEach(t => { const p = bez(q, t); el('circle', { class: 'xtr', cx: p[0], cy: p[1], r: 2.2 }, nodesEl); });
      }));
      const nEdits = new Set([...edits.keys()].map(k => k.split('/').slice(0, 2).join('/'))).size;
      const dirty = key() !== saved;
      status.textContent = (edits.size ? `${edits.size} point${edits.size > 1 ? 's' : ''} moved by hand` : 'no points moved by hand') +
        (dirty ? ' · not saved' : edits.size ? ' · saved' : '') + (stale ? ` · ${stale} stale adjustment(s) skipped by the build` : '') +
        (bulging && dirty ? ` · ${bulging} curve${bulging > 1 ? 's' : ''} now bulge${bulging > 1 ? '' : 's'} past ${bulging > 1 ? 'their' : 'its'} nodes: ` +
          'the build will put a node at each red point, moving a nearby node there where it can' : '') +
        (bulging && !dirty ? ` · the build put a node at each red point (the extremes your moves made): ${data.moved} moved there, ${data.added} added` : '') +
        (!dirty && data.check.length ? ` · the last build's outline check: ${data.check.join('; ')}` : '');
      bar.classList.toggle('dirty', dirty);
      if (sel) {
        const [cc, ss, pp] = canonical(sel.c, sel.s, sel.p, [0, 0]);
        const e = edits.get(`${cc}/${ss}/${pp}`) || [0, 0];
        const q = cur[sel.c][sel.s], what = sel.p === 0 ? 'node' : 'handle';
        let extra = '';
        if (sel.p) { const node = sel.p === 1 ? q[0] : q[3], v = sub(q[sel.p], node);
          extra = ` · handle ${(len(v) * scale).toFixed(0)} units long at ${(-deg(v)).toFixed(1)}°`; }
        info.textContent = `${data.names[sel.c][sel.s]} (${what}) · moved ${(e[0] * scale).toFixed(1)}, ${(-e[1] * scale).toFixed(1)} units from the construction${extra}`;
      } else info.textContent = editing ? 'Drag a node or handle. Arrow keys nudge the selected point by 1 unit, Shift by 10. Alt frees a handle at an extreme.' : '';
    }

    svg.addEventListener('pointerdown', ev => {
      if (!editing) return;
      const t = ev.target.closest('[data-c]');
      if (!t) { sel = null; render(); return; }
      ev.preventDefault();
      active = api_glyph;
      sel = { c: +t.dataset.c, s: +t.dataset.s, p: +t.dataset.p };
      history.push(new Map(edits));
      drag = { last: toSvg(ev) };
      svg.setPointerCapture(ev.pointerId);
      render();
    });
    svg.addEventListener('pointermove', ev => {
      if (!drag) return;
      const p = toSvg(ev), d = sub(p, drag.last);
      drag.last = p;
      move(d, ev.altKey);
    });
    const end = () => { drag = null; };
    svg.addEventListener('pointerup', end);
    svg.addEventListener('pointercancel', end);

    function nudge(ev) {
      if (!editing || !sel) return false;
      const step = (ev.shiftKey ? 10 : 1) / scale;
      const d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[ev.key];
      if (!d) return false;
      history.push(new Map(edits));
      move(d, ev.altKey);
      return true;
    }

    function points() {
      return [...edits].map(([k, d]) => { const [c, s, p] = k.split('/').map(Number);
        return { contour: c, segment: s, point: p, node: data.names[c][s], dx: +d[0].toFixed(3), dy: +d[1].toFixed(3) }; });
    }

    async function save() {
      const body = JSON.stringify({ points: points() });
      if (!api) {                                         // no server: hand the file over instead
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob([body], { type: 'application/json' }));
        a.download = `${data.glyph.replace('.', '_')}.json`;
        a.click();
        status.textContent = `downloaded: put it in fonts/${FAMILY}/adjustments/ and rebuild`;
        return false;
      }
      const r = await fetch(`${API}/adjustments/${encodeURIComponent(data.glyph)}`, { method: 'POST', body });
      if (!r.ok) { status.textContent = 'could not save'; return false; }
      saved = key();
      render();
      return true;
    }

    async function rebuild() {
      if (!(await save())) return;
      const r = await fetch(`${API}/rebuild`, { method: 'POST' });
      if (!r.ok && r.status !== 409) { status.textContent = 'could not start the build'; return; }
      bar.classList.add('busy');
      const t0 = Date.now();
      const poll = async () => {
        const s = await (await fetch(`${API}/status`, { cache: 'no-store' })).json();
        if (s.running) { status.textContent = `building… ${Math.round((Date.now() - t0) / 1000)} s`; return setTimeout(poll, 1500); }
        bar.classList.remove('busy');
        if (s.ok) { location.hash = fig.id; location.reload(); }
        else { status.textContent = 'the build stopped with an error; see below'; info.textContent = s.log.split('\n').filter(l => /Error|Traceback|line \d+/.test(l)).join('\n') || s.log.slice(-800); }
      };
      setTimeout(poll, 1500);
    }

    bar.addEventListener('click', ev => {
      const act = ev.target.dataset && ev.target.dataset.act;
      if (act === 'undo' && history.length) { edits = history.pop(); render(); }
      if (act === 'reset') { history.push(new Map(edits)); edits = new Map(); render(); }
      if (act === 'save') save();
      if (act === 'rebuild') rebuild();
    });
    bar.querySelector('[data-act=edit]').addEventListener('change', ev => {
      editing = ev.target.checked;
      fig.classList.toggle('editing', editing);
      if (editing) {
        const n = fig.querySelector('.layers input[data-l=nodes]');
        if (!n.checked) { n.checked = true; n.dispatchEvent(new Event('change')); }
        active = api_glyph;
      } else sel = null;
      render();
    });

    const api_glyph = { nudge };
    render();
    return api_glyph;
  }

  document.querySelectorAll('figure.ov').forEach(fig => { if (fig.querySelector('script.edit-data')) Glyph(fig); });
  document.addEventListener('keydown', ev => { if (active && active.nudge(ev)) ev.preventDefault(); });
})();
