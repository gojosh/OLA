# 2026-10-29 — Pugin Textura: a stroke editor on the proof page

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-stroke-editor.md`). Working on the e's crossing member, Josh asked whether he should adjust its detail lines by hand, then: "Yes, build a stroke editor for the textura proof page: drag a stroke's nodes and settings, saved into the recipe so the build keeps them." Recorded as decision 0012 (accepted).
- **What it moves.** The Lombardic's editor (decision 0010) moves outline points. A textura letter is pen strokes through named measurements, and moved points would be redrawn by the pen on the next build. So the textura editor moves the measurements themselves:
  - the nodes of a letter's strokes (pairs `name.x`/`name.y`), dragged on the letter or nudged with the arrow keys;
  - everything else (handle lengths, headings, pip sizes, how a spiral tightens), with sliders bounded as the fit bounds them.
- **Server** (`textura.Workbench`, served by `type.py serve`):
  - routes `GET /api/pugin-textura/letter/<g>` (measurements, bounds, values, which are held, the nodes, where Pugin's letter is) and `POST .../outline/<g>` (the letter drawn from measurements sent, by the build's own code: outline, pen paths, mean distance from Pugin's edge, the outline checks in font units);
  - `POST .../hold/<g>` (save into the recipe's `held`, listed in `held_by_hand`; let-go measurements removed);
  - `POST .../rebuild` (`textura.py build --fit none`, or `--fit` the let-go measurements, then the proof).
  - A letter redraws in 40–60 ms, so it follows a drag.
  - `type.py` now needs skia-pathops, for the textura's pen.
- **Page** (`tools/type/textura_editor.js`, inlined by `textura.py proof`):
  - **Edit strokes** on each card of a letter Pugin drew opens a full-window editor: Pugin's ink in grey, the outline in red, the pen's paths in orange, nodes as handles (green free, blue held, red changed), and the measurements listed by stroke.
  - Undo, Back to saved, Save, Save and rebuild, Close.
  - The squeezed y and z are drawn over his second line, and dragging maps through the squeeze.
- **Tested end to end in the browser:**
  - drag (the outline follows; status counts unsaved changes), undo, save (the recipe gained `held` and `held_by_hand`);
  - Save and rebuild (the build kept the held value, the page reloaded);
  - let go, then Save and rebuild (the build refitted just that measurement, back to its fitted value).
  - The e's recipe was restored after testing; it matches what it was apart from timestamps.
  - Letters checked: e, y, a.
- **Fixes on the way:**
  - the view framed the y's empty top (now framed on Pugin's ink);
  - nodes are a steady size on screen;
  - the status didn't count a pending let-go.

## What changed
- **Created:** `docs/decisions/0012-textura-stroke-editor.md`, `docs/brief/2026-10-29-textura-stroke-editor.md`, `tools/type/textura_editor.js`, this log
- **Updated:**
  - `tools/type/textura.py` (`Workbench`; Edit strokes and the editor panel on the proof page; cards anchored by letter)
  - `tools/type/type.py` (the textura's routes; a rebuild state per family; skia-pathops)
  - `docs/decisions/README.md`, `fonts/pugin-textura/README.md`, `docs/roadmap.md`

## Open threads
- **Single positions** (a stem's x, a stroke's end y) are set with sliders, not dragged; only pairs are nodes. A drag handle along one axis could come next if Josh wants it.
- The proof server must be restarted to pick up changes to the letters' code (it keeps the workbench loaded).
