# 2026-10-28 — A point editor on the Lombardic proof page

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh: "can we make the handles live on the proof page? What's the best way to handle final tweaks? Can you process them and integrate them into the build process?" Brief: `docs/brief/2026-10-28-manual-adjustments.md`.
- **The recommendation**, now decision 0010, accepted (Josh: "Accept decision 0010: final tweaks are recorded point moves made on the proof page and applied by the build."):
  - Keep final tweaks as recorded moves of single control points on top of the construction, never as edits to the generated UFO.
  - Make them on the proof page, store them in `fonts/<family>/adjustments/<glyph>.json`, and have every build apply them after fitting and check the outline again.
  - Measurement-level changes stay in recipe `corrections`.
  - A font editor takes over only once the family is frozen.
- **The editor** (`tools/type/editor.js`, inlined into the proof page):
  - Under each glyph: **Edit points**, **Filled**, **Undo**, **Remove all moves**, **Save**, **Save and rebuild**.
  - A node carries its handles; a smooth node's other handle turns to stay in line.
  - A handle at an extreme keeps its direction (Alt frees it).
  - Mirrored letters stay mirrored: a move on the right is stored as the mirrored move on the left, and axis nodes stay on the axis with flat handles. Lines stay lines.
  - Arrow keys nudge the selected point one font unit (Shift for ten).
  - The info line names the point and how far it has moved, in font units.
- **The server** (`type.py serve`, now behind the `font-proofs` entry in `.claude/launch.json`): serves `fonts/` on localhost and adds a small API.
  - It saves a glyph's adjustments (or deletes the file when none are left), and runs the build and proof in the background, with a status the page polls before it reloads.
  - It accepts only glyph names that have recipes. Without the server, Save downloads the file instead.
- **The build** (`construct.adjust`):
  - It applies the moves after fitting: lines stay lines; mirrored contours are regenerated from the left half, which is also what the font's unit rounding uses.
  - Each move is checked against the node name it was made on. If the construction has changed, the move is skipped and reported as stale.
  - The report keeps the construction's outline before the moves, for the editor.
- **Tested end to end in the app's browser.**
  - Dragged the I's top-left curl: the right curl followed, mirrored, and the page showed 4 points moved, not saved.
  - Save and rebuild wrote `adjustments/I.json`, the build applied 4 points with the checks passing, and the page reloaded on the I showing them saved. The compiled I stayed exactly symmetric.
  - Dragged a flat handle diagonally: it stayed flat and only changed length.
  - Then removed the moves and rebuilt; no adjustments remain.
- **A side effect to know.** Editing `construct.py` changes every letter's fit fingerprint, so the next build refits all of them (about a minute). The shared values moved slightly (stem_plain 40.05 px, trefoil_d 24.5 px). Letter files don't do this; only the shared modules do.

- **First real use: Josh's G, and what went wrong.**
  - Josh moved 8 points on G and rebuilt. The build applied them, but the outline check failed: two curves now bulged past their nodes. One was a tilted handle at the nub's right side, an extreme, which the editor allows with Alt; the other was a moved handle at the trefoil's join.
  - The server treated any check failure as an error, so the page didn't reload and Josh saw "an error".
  - Josh: "if bulging past the node on the x or y axis is something to avoid, feel free to rework my edit to achieve the same thing without such bulging."
- **The fix.** The build now reworks such moves while keeping their shape (`construct.add_extremes`, `construct.drop_redundant`):
  - it puts a node at each new extreme;
  - where a neighbouring node has become redundant (smooth and no longer an extreme), it merges that node's two curves, so in effect the node moves to the extreme. Limit: within 0.35 px of the moved shape, about half a font unit.
  - Josh's recorded moves stay exactly as he made them.
  - On G: the nub's right node moved to the new extreme. Nodes were added at the beak's dip into the bulb and the spiral's low point, both beside corners where nothing can merge. G passes its checks.
- **Page and editor.** A check failure no longer stops the page from reloading; the glyph shows its result. The editor marks bulging curves in red while dragging and says what the build will do or did.
- **Also fixed.** K's foot could swell in some refits, depending on small run-to-run differences. Its bottom (and H's and N's) is now placed relative to the two-lobe terminal's end, so it can't rise above it.

## What changed
- **Created:**
  - `tools/type/editor.js`
  - `docs/decisions/0010-adjustments-by-hand.md` (accepted)
  - `docs/brief/2026-10-28-manual-adjustments.md`
- **Updated:**
  - `tools/type/type.py` (serve; adjustments in the build; the editor on the proof page)
  - `tools/type/construct.py` (`adjust`, `mirrored_counts`)
  - `.claude/launch.json` (font-proofs runs `type.py serve`)
  - the family README (Adjusting by hand), `docs/decisions/README.md`, `docs/roadmap.md`

## Open threads
- Still to build: M and W (both forms), the cross, the dot ornament.
