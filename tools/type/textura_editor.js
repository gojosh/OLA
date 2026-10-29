// The textura proof page's stroke editor (tools/type/textura.py inlines this file into the page; decision 0012).
//
// A textura letter is the strokes of the pen through its own named measurements: the nodes of its
// strokes (a pair of measurements, name.x and name.y, in plate pixels) and their settings (handle
// lengths, headings, a pip's size, how a spiral tightens). Here those are moved by hand: drag a
// node, or set a setting with its slider. The letter is drawn again by the local server
// (type.py serve), by the same code as the build, as they move, over Pugin's. Saving holds what was
// changed in the letter's recipe (`held`, which every fit keeps as it is); a held measurement can
// be let go back to the fit. Save and rebuild also rebuilds the font and this page.
//
// A group of the family's settings shared by several letters (the split top of b, d, h, k and l)
// opens the same way: its settings with sliders, and all its letters drawn side by side as they
// move. Saving holds them in source.json.
(function () {
  const API = '/api/pugin-textura';
  const NS = 'http://www.w3.org/2000/svg';
  const $ = s => document.querySelector(s);
  const el = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  };
  const pathD = segs => segs.map((q, i) => (i ? '' : `M${q[0][0]},${q[0][1]}`) + `C${q[1][0]},${q[1][1]} ${q[2][0]},${q[2][1]} ${q[3][0]},${q[3][1]}`).join('');
  const round = v => Math.round(v * 1000) / 1000;

  let api = false;
  fetch(`${API}/status`, { cache: 'no-store' }).then(r => { api = r.ok; document.documentElement.classList.toggle('has-api', api); }).catch(() => {});

  const panel = $('#se'), svg = $('#se-svg'), list = $('#se-list'), status = $('#se-status'), title = $('#se-title'), many = $('#se-many');
  const summary = panel.querySelector('aside summary');
  let mode = 'letter';   // or 'group': a group of the family's settings, drawn on several letters
  const ref = el('image', { class: 'se-ref', preserveAspectRatio: 'none' }, svg);
  const con = el('g', { class: 'se-con' }, svg);
  const shape = el('path', { class: 'se-outline' }, con);
  const pens = el('g', { class: 'se-pens' }, con);
  const handles = el('g', { class: 'se-handles' }, con);
  const tag = el('text', { class: 'se-tag' }, con);

  let L = null;          // the letter as the server gave it
  let values = {};       // its measurements as they stand here
  let saved = {};        // as saved
  let release = new Set();
  let history = [];
  let sel = null, drag = null, inflight = false, pending = false, viewSet = false;

  function changed() {
    return Object.keys(values).filter(k => Math.abs(values[k] - saved[k]) > 1e-6);
  }

  function clamp(k, v) {
    const s = L.spec[k];
    return Math.min(Math.max(v, s.lo), s.hi);
  }

  let last = null;       // the last drawing's numbers
  function setStatus(o) {
    if (o) last = o;
    if (!last) return;
    const n = changed().length + release.size;
    const tail = n ? ` · <b>${n}</b> unsaved` : ' · saved';
    if (mode === 'group') {
      status.innerHTML = 'From Pugin\'s edge on average: ' + L.letters.map(g => `${L.refs[g].char} <b>${last[g].mean_px}</b> px${last[g].ok ? '' : ' <b class="bad">(checks FAIL)</b>'}`).join(' · ') + tail;
      return;
    }
    status.innerHTML = `<b>${last.mean_px}</b> px from Pugin's edge on average · outline checks ${last.ok ? 'pass' : '<b class="bad">FAIL</b>'} · ${last.contour_count} contour(s)` + tail;
  }

  const views = {};      // in a group: each letter's own drawing
  const GROUP_W = 120, GROUP_H = 220;                  // its window, in plate pixels
  function groupViews() {
    many.innerHTML = '';
    for (const g of L.letters) {
      const fig = document.createElement('figure');
      const v = document.createElementNS(NS, 'svg');
      fig.appendChild(v);
      const cap = document.createElement('figcaption');
      cap.textContent = L.refs[g].char;
      fig.appendChild(cap);
      many.appendChild(fig);
      const [x0, y0, x1, y1] = L.refs[g].box;
      el('image', { class: 'se-ref', preserveAspectRatio: 'none', href: `/pugin-textura/${L.refs[g].reference}`, x: x0, y: y0, width: x1 - x0, height: y1 - y0 }, v);
      const c = el('g', {}, v);
      views[g] = { svg: v, con: c, shape: el('path', { class: 'se-outline' }, c), framed: false };
    }
  }

  async function drawGroup() {
    const r = await fetch(`${API}/family/${encodeURIComponent(L.group)}/outlines`, { method: 'POST', body: JSON.stringify({ values }) });
    const o = await r.json();
    if (!r.ok) { status.innerHTML = `<b class="bad">The pen can't draw that:</b> ${o.error}`; return; }
    for (const g of L.letters) {
      const w = views[g], d = o[g];
      w.shape.setAttribute('d', d.contours.map(pathD).join(''));
      if (d.affine) { const [a, b, c, dd, e, f] = d.affine; w.con.setAttribute('transform', `matrix(${a},${dd},${b},${e},${c},${f})`); }
      if (!w.framed) {                               // the same window on every letter, at the same scale: its split top, and the stem below it
        const A = d.affine || [1, 0, 0, 0, 1, 0];
        const pts = [];
        for (const c of d.contours) for (const q of c) for (const [x, y] of q) pts.push([A[0] * x + A[1] * y + A[2], A[3] * x + A[4] * y + A[5]]);
        const top = Math.min(...pts.map(p => p[1]));
        const near = pts.filter(p => p[1] < top + 30).map(p => p[0]);
        const cx = (Math.min(...near) + Math.max(...near)) / 2;
        w.svg.setAttribute('viewBox', `${cx - GROUP_W / 2} ${top - 12} ${GROUP_W} ${GROUP_H}`);
        w.framed = true;
      }
    }
    setStatus(o);
  }

  async function draw() {                              // ask the server to draw the letter from `values`
    if (inflight) { pending = true; return; }
    if (mode === 'group') {
      inflight = true;
      try { await drawGroup(); } finally { inflight = false; if (pending) { pending = false; draw(); } }
      return;
    }
    inflight = true;
    try {
      const r = await fetch(`${API}/outline/${encodeURIComponent(L.glyph)}`, { method: 'POST', body: JSON.stringify({ values }) });
      const o = await r.json();
      if (!r.ok) { status.innerHTML = `<b class="bad">The pen can't draw that:</b> ${o.error}`; return; }
      shape.setAttribute('d', o.contours.map(pathD).join(''));
      pens.innerHTML = '';
      for (const s of o.strokes) el('path', { d: pathD(s) }, pens);
      if (o.affine) { const [a, b, c, d, e, f] = o.affine; con.setAttribute('transform', `matrix(${a},${d},${b},${e},${c},${f})`); }
      else con.removeAttribute('transform');
      if (!viewSet) { frame(o); renderHandles(); }
      setStatus(o);
    } finally {
      inflight = false;
      if (pending) { pending = false; draw(); }
    }
  }

  function frame(o) {                                  // the view: Pugin's letter and ours, with a margin
    const [x0, y0, x1, y1] = L.ink;
    let lo = [x0, y0], hi = [x1, y1];
    const A = o.affine || [1, 0, 0, 0, 1, 0];                 // where the outline is drawn, over Pugin's
    for (const c of o.contours) for (const q of c) for (const [x, y] of q) {
      const p = [A[0] * x + A[1] * y + A[2], A[3] * x + A[4] * y + A[5]];
      lo = [Math.min(lo[0], p[0]), Math.min(lo[1], p[1])]; hi = [Math.max(hi[0], p[0]), Math.max(hi[1], p[1])];
    }
    const m = 12;
    svg.setAttribute('viewBox', `${lo[0] - m} ${lo[1] - m} ${hi[0] - lo[0] + 2 * m} ${hi[1] - lo[1] + 2 * m}`);
    viewSet = true;
  }

  function renderHandles() {
    handles.innerHTML = '';
    if (mode === 'group') return;
    const vb = svg.viewBox.baseVal, px = vb && vb.width ? vb.width / svg.clientWidth : 0.5;     // plate pixels per screen pixel
    for (const n of L.nodes) {
      const x = values[`${n}.x`], y = values[`${n}.y`];
      const moved = changed().some(k => k === `${n}.x` || k === `${n}.y`);
      const held = L.held.includes(`${n}.x`) || L.held.includes(`${n}.y`);
      const c = el('circle', { cx: x, cy: y, r: 5 * px, class: `se-node${n === sel ? ' sel' : ''}${moved ? ' moved' : ''}${held ? ' held' : ''}`, 'data-n': n }, handles);
      el('title', {}, c).textContent = n;
    }
    if (sel) { tag.textContent = sel; tag.setAttribute('x', values[`${sel}.x`] + 8 * px); tag.setAttribute('y', values[`${sel}.y`] - 8 * px); tag.style.fontSize = `${13 * px}px`; }
    else tag.textContent = '';
  }

  function renderGroupList() {                         // the group's settings, with their sliders
    list.innerHTML = '';
    for (const k of Object.keys(L.spec)) {
      const s = L.spec[k], row = document.createElement('div');
      row.className = 'se-row se-wide' + (Math.abs(values[k] - saved[k]) > 1e-6 ? ' moved' : '');
      const step = (s.hi - s.lo) <= 2 ? 0.01 : 0.1;
      row.innerHTML = `<label title="${k}">${s.meaning.replace(/^the split top[^:]*: /, '')}</label>
        <input type="range" min="${s.lo}" max="${s.hi}" step="${step}" value="${values[k]}">
        <input type="number" min="${s.lo}" max="${s.hi}" step="${step}" value="${round(values[k])}">
        <span class="se-held">${L.by_hand.includes(k) ? 'held · by hand' : 'held'}</span>`;
      const [range, num] = row.querySelectorAll('input');
      const set = v => { values[k] = clamp(k, +v); range.value = values[k]; num.value = round(values[k]); draw(); setStatus(); };
      range.addEventListener('pointerdown', () => history.push({ ...values }));
      num.addEventListener('focus', () => history.push({ ...values }));
      range.addEventListener('input', () => set(range.value));
      range.addEventListener('change', renderGroupList);
      num.addEventListener('change', () => { set(num.value); renderGroupList(); });
      list.appendChild(row);
    }
  }

  function renderList() {                              // every measurement, with its slider
    if (mode === 'group') return renderGroupList();
    list.innerHTML = '';
    const keys = Object.keys(L.spec).sort();
    let group = null;
    for (const k of keys) {
      const g = k.includes('.') ? k.split('.')[0] : '(the letter)';
      if (g !== group) { group = g; const h = document.createElement('h4'); h.textContent = g; list.appendChild(h); }
      const s = L.spec[k], row = document.createElement('div');
      const isHeld = L.held.includes(k) && !release.has(k), byHand = L.by_hand.includes(k);
      row.className = 'se-row' + (Math.abs(values[k] - saved[k]) > 1e-6 ? ' moved' : '') + (isHeld ? ' held' : '');
      const step = (s.hi - s.lo) <= 2 ? 0.01 : 0.1;
      row.innerHTML = `<label title="${k}">${k.includes('.') ? k.slice(g.length + 1) : k}</label>
        <input type="range" min="${s.lo}" max="${s.hi}" step="${step}" value="${values[k]}">
        <input type="number" min="${s.lo}" max="${s.hi}" step="${step}" value="${round(values[k])}">
        <span class="se-held">${release.has(k) ? 'let go: the fit sets it again on Save and rebuild' : isHeld ? (byHand ? 'held · by hand' : 'held') : ''}${isHeld ? ' <button title="let the fit set it again (on Save and rebuild)">let go</button>' : ''}</span>`;
      const [range, num] = row.querySelectorAll('input');
      const set = v => { values[k] = clamp(k, +v); range.value = values[k]; num.value = round(values[k]); renderHandles(); draw(); };
      range.addEventListener('pointerdown', () => history.push({ ...values }));
      num.addEventListener('focus', () => history.push({ ...values }));
      range.addEventListener('input', () => set(range.value));
      range.addEventListener('change', renderList);
      num.addEventListener('change', () => { set(num.value); renderList(); });
      const b = row.querySelector('button');
      if (b) b.addEventListener('click', () => { release.add(k); renderList(); setStatus(); });
      list.appendChild(row);
    }
  }

  function toLetter(ev) {                              // a pointer's place in the letter's own coordinates
    const p = svg.createSVGPoint();
    p.x = ev.clientX; p.y = ev.clientY;
    const q = p.matrixTransform(con.getScreenCTM().inverse());
    return [q.x, q.y];
  }

  svg.addEventListener('pointerdown', ev => {
    const n = ev.target.dataset && ev.target.dataset.n;
    if (!n) { sel = null; renderHandles(); return; }
    ev.preventDefault();
    sel = n;
    history.push({ ...values });
    const [x, y] = toLetter(ev);
    drag = { dx: values[`${n}.x`] - x, dy: values[`${n}.y`] - y };
    svg.setPointerCapture(ev.pointerId);
    renderHandles();
  });
  svg.addEventListener('pointermove', ev => {
    if (!drag) return;
    const [x, y] = toLetter(ev);
    values[`${sel}.x`] = clamp(`${sel}.x`, x + drag.dx);
    values[`${sel}.y`] = clamp(`${sel}.y`, y + drag.dy);
    renderHandles();
    draw();
  });
  const end = () => { if (drag) { drag = null; renderList(); } };
  svg.addEventListener('pointerup', end);
  svg.addEventListener('pointercancel', end);

  document.addEventListener('keydown', ev => {
    if (panel.hidden || !sel || /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return;
    const step = ev.shiftKey ? 5 : 0.5;
    const d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[ev.key];
    if (!d) return;
    ev.preventDefault();
    history.push({ ...values });
    values[`${sel}.x`] = clamp(`${sel}.x`, values[`${sel}.x`] + d[0]);
    values[`${sel}.y`] = clamp(`${sel}.y`, values[`${sel}.y`] + d[1]);
    renderHandles(); renderList(); draw();
  });

  async function open(g) {
    if (!api) { alert('The stroke editor needs the local proof server: start "font-proofs" (tools/type/type.py serve) and open this page from it.'); return; }
    const r = await fetch(`${API}/letter/${encodeURIComponent(g)}`, { cache: 'no-store' });
    if (!r.ok) { alert(`Can't edit ${g}: ${(await r.json()).error}`); return; }
    L = await r.json();
    mode = 'letter';
    panel.classList.remove('group');
    values = { ...L.values }; saved = { ...L.values }; release = new Set(); history = []; sel = null; viewSet = false; last = null;
    title.textContent = `Strokes of ${L.char}`;
    summary.textContent = 'How this letter is drawn';
    $('#se-desc').textContent = L.description;
    const [x0, y0, x1, y1] = L.box;
    ref.setAttribute('href', `/pugin-textura/${L.reference}`);
    ref.setAttribute('x', x0); ref.setAttribute('y', y0); ref.setAttribute('width', x1 - x0); ref.setAttribute('height', y1 - y0);
    panel.hidden = false;
    document.body.classList.add('se-open');
    renderHandles(); renderList(); draw();
  }

  async function openGroup(name) {
    if (!api) { alert('The stroke editor needs the local proof server: start "font-proofs" (tools/type/type.py serve) and open this page from it.'); return; }
    const r = await fetch(`${API}/family/${encodeURIComponent(name)}`, { cache: 'no-store' });
    if (!r.ok) { alert(`Can't edit ${name}: ${(await r.json()).error}`); return; }
    L = await r.json();
    mode = 'group';
    panel.classList.add('group');
    values = { ...L.values }; saved = { ...L.values }; release = new Set(); history = []; sel = null; last = null;
    title.textContent = `${L.title[0].toUpperCase()}${L.title.slice(1)} of ${L.letters.join(', ')}`;
    summary.textContent = 'What these settings are';
    $('#se-desc').textContent = 'Settings the family holds, shared by these letters, so every one has the same top. Saving holds them in source.json, which every build keeps.';
    panel.hidden = false;
    document.body.classList.add('se-open');
    groupViews(); renderList(); draw();
  }

  function close() {
    if ((changed().length || release.size) && !confirm('Leave without saving?')) return;
    panel.hidden = true;
    document.body.classList.remove('se-open');
  }

  async function save() {
    const set = Object.fromEntries(changed().map(k => [k, round(values[k])]));
    if (mode === 'group') {
      const r = await fetch(`${API}/family/${encodeURIComponent(L.group)}/hold`, { method: 'POST', body: JSON.stringify({ set }) });
      const o = await r.json();
      if (!r.ok) { status.innerHTML = `<b class="bad">Couldn't save:</b> ${o.error}`; return false; }
      L.by_hand = o.by_hand; saved = { ...values };
      renderList(); setStatus();
      return true;
    }
    const r = await fetch(`${API}/hold/${encodeURIComponent(L.glyph)}`, { method: 'POST', body: JSON.stringify({ set, release: [...release] }) });
    const o = await r.json();
    if (!r.ok) { status.innerHTML = `<b class="bad">Couldn't save:</b> ${o.error}`; return false; }
    for (const k of release) values[k] = saved[k];
    L.held = o.held; L.by_hand = o.by_hand;
    saved = { ...values }; release = new Set();
    renderHandles(); renderList(); draw();
    return true;
  }

  async function rebuild() {
    if (!(await save())) return;
    const r = await fetch(`${API}/rebuild`, { method: 'POST' });
    if (!r.ok && r.status !== 409) { status.textContent = "Couldn't start the build."; return; }
    const t0 = Date.now();
    panel.classList.add('busy');
    const poll = async () => {
      const s = await (await fetch(`${API}/status`, { cache: 'no-store' })).json();
      if (s.running) { status.textContent = `Building the font and this page… ${Math.round((Date.now() - t0) / 1000)} s`; return setTimeout(poll, 1500); }
      panel.classList.remove('busy');
      if (s.ok) { location.hash = mode === 'group' ? `g-${L.letters[0]}` : `g-${L.glyph}`; location.reload(); }
      else status.innerHTML = `<b class="bad">The build stopped with an error:</b><pre>${(s.log || '').slice(-1200).replace(/</g, '&lt;')}</pre>`;
    };
    setTimeout(poll, 1500);
  }

  panel.addEventListener('click', ev => {
    const act = ev.target.dataset && ev.target.dataset.act;
    if (act === 'undo' && history.length) { values = history.pop(); renderHandles(); renderList(); draw(); }
    if (act === 'reset') { history.push({ ...values }); values = { ...saved }; release = new Set(); renderHandles(); renderList(); draw(); }
    if (act === 'save') save();
    if (act === 'rebuild') rebuild();
    if (act === 'close') close();
  });
  document.querySelectorAll('[data-edit]').forEach(b => b.addEventListener('click', () => open(b.dataset.edit)));
  document.querySelectorAll('[data-edit-group]').forEach(b => b.addEventListener('click', () => openGroup(b.dataset.editGroup)));
})();
