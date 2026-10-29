# 2026-10-29 — Pugin Textura: u, w and j

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh: "Continue wth the next letters". After the 24 on the plate, the next letters are the three Pugin didn't draw. Under decision 0008 they are drafted in his idiom as proposals, built from the fitted measurements of the letter each is modelled on, as the Lombardic's modern Y was.
- **The three proposals** (`textura_letters.py`, `DERIVED`):
  - **u** is n turned over: two minims, the first's foot running on to end against the second's stem, so they join at the foot as n's join at the head. Built from n. `minim` gained `before`, the foot's counterpart to `after`.
  - **w** is u followed by v's second stroke, which stops with the nib's cut against the second minim's foot. Built from v, whose strokes set the pitch.
  - **j** is i running on past the baseline and turning left at the descender line, as ſ's tail does, with i's hairline stroke above. Built from i.
- **The build** (`textura.py`) makes letters built from another's measurements: it takes the model letter's fitted values, adds nothing fitted, and records `derived_from` and a proposal note in the recipe. The proof shows them on their own, marked as proposals.
- **The proof** now sets ordinary text: "Kyrie eleison, Gloria in excelsis deo, Agnus dei, Dominus vobiscum, Te deum laudamus, Ave maris stella, Ecce ancilla domini, Salve regina, World without end". Checked in the browser.
- **Clearance above and below the x-height.**
  - At text size, d's arm leaning back over its bowl looked as if it touched a preceding l's spur ("world"). Raising the textura's clearance from 10 to 20 units everywhere would have opened 511 pairs by 5–15 units and loosened the whole face, since heads and feet all but touch in a textura this tight.
  - So the clearance is now zoned: 10 units in the x-height band, 20 above and below it (`spacing.kern` takes a second clearance for the outer zones).
  - Parts above and below the x-height are also checked by true distance between the outlines, since two parts can be clear row by row and still almost meet on a slant. That opened 45 pairs.
  - On a closer look, the "touch" in "world" was the d's own arm crossing its bowl: Pugin's design, not a spacing fault. The zoned clearance stays because it is right anyway.
- **A legibility note for Josh.** In "excelsis", Pugin's x, with its long descender and a flag at the top, reads close to an r. It is his form; whether the plain x should be more modern is his call.
- **Results.** 27 letters, all passing the outline checks; 590 kerned pairs.

## What changed
- **Updated:**
  - `tools/type/textura_letters.py` (u, w, j; `minim(before=…)`; `DERIVED`)
  - `tools/type/textura.py` (letters built from another's measurements; the zoned clearance and the true-distance check; the proof's phrases and proposal cards)
  - `tools/type/spacing.py` (`kern(…, clearance_over=…)`)
  - `fonts/pugin-textura/` (`source.json` spacing, recipes, spacing, the UFO, the README), `fonts/README.md`, `docs/roadmap.md`
- **Created:** this log

## Open threads
- The ampersand's plain form; the hairline exits at the feet; z's lower bowl.
- Pugin's x reads close to r (above).
- Medieval ſ and s use as a stylistic set.
- The flourished alternates, then plate 10's capitals.
