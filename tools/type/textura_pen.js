// The textura's pen editor (decision 0013): a letter drawn by hand, point by point. Each point is
// where the pen is, the nib's angle there and how hard it's pressed; the pen's path runs smoothly
// through the points (sharply at a corner), and its angle and pressure change smoothly between them.
// The server draws the letter from the points with the build's own pen, as they move. Saving keeps
// them in the letter's recipe, and the build draws the letter from them.
(function () {
  const $ = s => document.querySelector(s);
  const NS = 'http://www.w3.org/2000/svg';
  const API = '/api/pugin-textura';
  const panel = $('#pe'), svg = $('#pe-svg'), list = $('#pe-list'), status = $('#pe-status'), title = $('#pe-title');
  if (!panel) return;
  let L = null, pts = [], saved = '', history = [], sel = -1, drag = null, inflight = false, pending = false, last = null;
  const el = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const round = (v, n = 2) => Math.round(v * 10 ** n) / 10 ** n;
  const snapshot = () => JSON.stringify(pts);
  const remember = () => { history.push(snapshot()); if (history.length > 200) history.shift(); };
  const pathD = c => c.map((q, i) => (i ? '' : `M${q[0][0]},${q[0][1]}`) + `C${q[1][0]},${q[1][1]} ${q[2][0]},${q[2][1]} ${q[3][0]},${q[3][1]}`).join('') + 'Z';
  const unit = a => [Math.cos(a * Math.PI / 180), -Math.sin(a * Math.PI / 180)];

  let layers = {};
  function build() {                                   // the canvas: Pugin's letter, Josh's drawing, then what's drawn
    svg.innerHTML = '';
    const [x0, y0, x1, y1] = L.box;
    el('image', { class: 'se-ref', preserveAspectRatio: 'none', href: `/pugin-textura/${L.reference}`, x: x0, y: y0, width: x1 - x0, height: y1 - y0 }, svg);
    if (L.hand) el('image', { class: 'pe-hand', preserveAspectRatio: 'none', href: `/pugin-textura/${L.hand.src}`, x: L.hand.x, y: L.hand.y, width: L.hand.w, height: L.hand.h }, svg);
    layers.outline = el('path', { class: 'pe-outline' }, svg);
    layers.path = el('path', { class: 'pe-path' }, svg);
    layers.nibs = el('g', { class: 'pe-nibs' }, svg);
    layers.points = el('g', {}, svg);
    const m = 10;
    svg.setAttribute('viewBox', `${x0 - m} ${y0 - m} ${x1 - x0 + 2 * m} ${y1 - y0 + 2 * m}`);
    layers.path.addEventListener('dblclick', addAt);
  }

  function setStatus() {
    if (!last) return;
    const dirty = snapshot() !== saved;
    status.innerHTML = (last.mean_px == null ? '' : `<b>${last.mean_px}</b> px from ${L.hand ? 'Josh\'s drawing' : 'Pugin\'s main stroke'} on average, 95% within ${last.p95_px}, at most ${last.max_px} · `) +
      `outline checks ${last.ok ? 'pass' : '<b class="bad">FAIL</b>'} · ${pts.length} points` + (dirty ? ' · <b>unsaved</b>' : ' · saved');
  }

  async function draw() {                              // the server draws the letter from the points
    if (inflight) { pending = true; return; }
    inflight = true;
    try {
      const r = await fetch(`${API}/pen/${L.glyph}/outline`, { method: 'POST', body: JSON.stringify({ points: pts }) });
      const o = await r.json();
      if (!r.ok) { status.innerHTML = `<b class="bad">The pen can't draw that:</b> ${o.error}`; return; }
      last = o;
      layers.outline.setAttribute('d', o.contours.map(pathD).join(''));
      layers.path.setAttribute('d', o.path.length ? `M${o.path[0][0][0]},${o.path[0][0][1]}` + o.path.map(q => `C${q[1][0]},${q[1][1]} ${q[2][0]},${q[2][1]} ${q[3][0]},${q[3][1]}`).join('') : '');
      setStatus();
    } finally {
      inflight = false;
      if (pending) { pending = false; draw(); }
    }
  }

  function renderPoints() {                            // each point, and the nib there: its width and angle
    layers.nibs.innerHTML = ''; layers.points.innerHTML = '';
    const vb = svg.viewBox.baseVal, px = vb && vb.width ? vb.width / svg.clientWidth : 0.3;
    pts.forEach((q, i) => {
      const [ux, uy] = unit(q.angle), h = L.nib.width * q.pressure / 2;
      el('line', { class: 'pe-nib' + (i === sel ? ' sel' : ''), x1: q.x - h * ux, y1: q.y - h * uy, x2: q.x + h * ux, y2: q.y + h * uy }, layers.nibs);
      if (i === sel) {
        const t = el('circle', { class: 'pe-turn', cx: q.x + h * ux, cy: q.y + h * uy, r: 5 * px, 'data-i': i, 'data-turn': 1 }, layers.points);
        el('title', {}, t).textContent = 'turn the nib';
      }
      const c = q.corner
        ? el('rect', { class: 'pe-pt' + (i === sel ? ' sel' : ''), x: q.x - 4 * px, y: q.y - 4 * px, width: 8 * px, height: 8 * px, 'data-i': i }, layers.points)
        : el('circle', { class: 'pe-pt' + (i === sel ? ' sel' : ''), cx: q.x, cy: q.y, r: 4.5 * px, 'data-i': i }, layers.points);
      el('title', {}, c).textContent = `point ${i + 1}`;
    });
  }

  function renderList() {
    list.innerHTML = '<div class="pe-row head"><span>#</span><span>x</span><span>y</span><span>angle</span><span>pressure</span><span title="corner">c</span></div>';
    pts.forEach((q, i) => {
      const row = document.createElement('div');
      row.className = 'pe-row' + (i === sel ? ' sel' : '');
      row.innerHTML = `<span>${i + 1}</span>` + ['x', 'y', 'angle', 'pressure'].map(k =>
        `<input type="number" data-k="${k}" step="${k === 'pressure' ? 0.01 : k === 'angle' ? 1 : 0.5}" value="${round(q[k], k === 'pressure' ? 3 : 2)}">`).join('') +
        `<input type="checkbox" data-k="corner" ${q.corner ? 'checked' : ''} title="a corner: the path turns sharply here">`;
      row.addEventListener('focusin', () => { if (sel !== i) { sel = i; renderPoints(); markRows(); } });
      row.querySelectorAll('input').forEach(inp => {
        inp.addEventListener('focus', remember);
        inp.addEventListener('change', () => {
          q[inp.dataset.k] = inp.dataset.k === 'corner' ? inp.checked : +inp.value;
          renderPoints(); draw();
        });
      });
      list.appendChild(row);
    });
  }
  const markRows = () => list.querySelectorAll('.pe-row:not(.head)').forEach((r, i) => r.classList.toggle('sel', i === sel));
  const refresh = () => { renderPoints(); renderList(); draw(); };

  function toPlate(ev) {
    const p = svg.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY;
    const q = p.matrixTransform(svg.getScreenCTM().inverse());
    return [q.x, q.y];
  }

  svg.addEventListener('pointerdown', ev => {
    const t = ev.target;
    if (t.dataset.i === undefined) return;
    const i = +t.dataset.i;
    remember();
    sel = i;
    drag = { i, turn: !!t.dataset.turn };
    svg.setPointerCapture(ev.pointerId);
    renderPoints(); markRows();
    ev.preventDefault();
  });
  svg.addEventListener('pointermove', ev => {
    if (!drag) return;
    const [x, y] = toPlate(ev), q = pts[drag.i];
    if (drag.turn) {                                   // the nib turns to point at the pointer, the way it's been turning
      let a = Math.atan2(-(y - q.y), x - q.x) * 180 / Math.PI;
      while (a - q.angle > 180) a -= 360;
      while (q.angle - a > 180) a += 360;
      q.angle = round(a, 2);
    } else { q.x = round(x); q.y = round(y); }
    renderPoints(); draw();
  });
  svg.addEventListener('pointerup', () => { if (drag) { drag = null; renderList(); } });

  function addAt(ev) {                                 // a new point where the path was double-clicked
    if (!last || !last.path.length) return;
    const [x, y] = toPlate(ev);
    let best = [1e9, 0, 0];
    last.path.forEach((q, k) => {
      for (let s = 0; s <= 1; s += 0.02) {
        const m = 1 - s, bx = m * m * m * q[0][0] + 3 * m * m * s * q[1][0] + 3 * m * s * s * q[2][0] + s * s * s * q[3][0],
              by = m * m * m * q[0][1] + 3 * m * m * s * q[1][1] + 3 * m * s * s * q[2][1] + s * s * s * q[3][1];
        const d = (bx - x) ** 2 + (by - y) ** 2;
        if (d < best[0]) best = [d, k, s];
      }
    });
    const [, k, s] = best, a = pts[k], b = pts[k + 1];
    remember();
    pts.splice(k + 1, 0, { x: round(x), y: round(y), angle: round(a.angle + (b.angle - a.angle) * s), pressure: round(a.pressure + (b.pressure - a.pressure) * s, 3), corner: false });
    sel = k + 1;
    refresh();
  }

  document.addEventListener('keydown', ev => {
    if (panel.hidden || ev.target.tagName === 'INPUT') return;
    if ((ev.metaKey || ev.ctrlKey) && ev.key === 'z') { undo(); ev.preventDefault(); return; }
    if (sel < 0) return;
    const q = pts[sel], big = ev.shiftKey;
    const act = {
      ArrowLeft: () => q.x = round(q.x - (big ? 2 : 0.5)), ArrowRight: () => q.x = round(q.x + (big ? 2 : 0.5)),
      ArrowUp: () => q.y = round(q.y - (big ? 2 : 0.5)), ArrowDown: () => q.y = round(q.y + (big ? 2 : 0.5)),
      '[': () => q.angle = round(q.angle + (big ? 5 : 1)), ']': () => q.angle = round(q.angle - (big ? 5 : 1)),
      '{': () => q.angle = round(q.angle + 5), '}': () => q.angle = round(q.angle - 5),
      '-': () => q.pressure = round(Math.max(0.05, q.pressure - (big ? 0.05 : 0.01)), 3), '_': () => q.pressure = round(Math.max(0.05, q.pressure - 0.05), 3),
      '=': () => q.pressure = round(q.pressure + (big ? 0.05 : 0.01), 3), '+': () => q.pressure = round(q.pressure + 0.05, 3),
      c: () => q.corner = !q.corner, C: () => q.corner = !q.corner,
      Delete: () => { if (pts.length > 2) { pts.splice(sel, 1); sel = Math.min(sel, pts.length - 1); } },
      Backspace: () => { if (pts.length > 2) { pts.splice(sel, 1); sel = Math.min(sel, pts.length - 1); } },
    }[ev.key];
    if (!act) return;
    remember(); act(); refresh(); ev.preventDefault();
  });

  function undo() { if (history.length) { pts = JSON.parse(history.pop()); sel = Math.min(sel, pts.length - 1); refresh(); } }

  async function save() {
    const r = await fetch(`${API}/pen/${L.glyph}/save`, { method: 'POST', body: JSON.stringify({ points: pts }) });
    const o = await r.json();
    if (!r.ok) { status.innerHTML = `<b class="bad">Couldn't save:</b> ${o.error}`; return false; }
    saved = snapshot(); setStatus();
    return true;
  }

  async function rebuild() {
    if (!(await save())) return;
    panel.classList.add('busy');
    status.innerHTML = 'Rebuilding the font and this page…';
    const r = await fetch(`${API}/rebuild`, { method: 'POST' });
    if (!r.ok && r.status !== 409) { status.innerHTML = `<b class="bad">Couldn't rebuild:</b> ${(await r.json()).error}`; panel.classList.remove('busy'); return; }
    for (;;) {
      await new Promise(res => setTimeout(res, 1500));
      const s = await (await fetch(`${API}/status`, { cache: 'no-store' })).json();
      if (s.running) continue;
      if (s.ok) { location.hash = `g-${L.glyph}`; location.reload(); }
      else { status.innerHTML = `<b class="bad">The build failed:</b><pre>${(s.log || '').slice(-1500)}</pre>`; panel.classList.remove('busy'); }
      return;
    }
  }

  async function open(g) {
    const r = await fetch(`${API}/pen/${g}`, { cache: 'no-store' });
    if (!r.ok) { alert(`Can't draw ${g}: ${(await r.json()).error}`); return; }
    L = await r.json();
    pts = L.points.map(q => ({ ...q }));
    saved = L.drawn ? snapshot() : '';
    history = []; sel = -1; last = null;
    title.textContent = `Draw the stroke of ${L.char}` + (L.drawn ? '' : ' (from its construction; not yet saved)');
    panel.hidden = false;
    document.body.classList.add('se-open');
    build(); refresh();
  }
  function close() { panel.hidden = true; document.body.classList.remove('se-open'); }

  panel.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', () => ({
    undo, reset: () => { if (saved) { remember(); pts = JSON.parse(saved); refresh(); } }, save, rebuild, close,
  })[b.dataset.act]()));
  panel.querySelectorAll('[data-show]').forEach(c => c.addEventListener('change', () => panel.classList.toggle('no-' + c.dataset.show, !c.checked)));
  window.addEventListener('resize', () => { if (!panel.hidden) renderPoints(); });
  fetch(`${API}/status`, { cache: 'no-store' }).then(r => {
    if (r.ok) document.querySelectorAll('[data-pen]').forEach(b => b.addEventListener('click', () => open(b.dataset.pen)));
  }).catch(() => {});
})();
