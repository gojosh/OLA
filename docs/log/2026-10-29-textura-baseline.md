# 2026-10-29 — Pugin Textura: the baseline; Josh's f and t

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-baseline.md`). Josh: "Can we fix the baseline alignment with the lombard caps? Not sure which one is off (the textura or lombard) but needs fixing."
- **The textura was off.** Measured in the two fonts:
  - The Lombardic capitals stand on their baseline (yMin 0, a few curls a little below). They were right.
  - Every textura letter went 44 units below its baseline (yMin -44), and the heads peaked at 434 against a declared x-height of 470.
  - The font's baseline was `bottom`, the line the foot strokes end on, at the middle of the nib's cut. But the x-height is measured on the plate from the points of the heads to the points of the feet. So under a Lombardic initial the textura sat 44 units low.
- **The fix.** The baseline is now where the points of the feet stand (`textura_letters.baseline`: `bottom` plus the nib's lowest corner there, 19.3 px). Every construction, and the drawn letters, return it.
  - z and j set their baseline from a local name and were missed at first, so they still hung low; caught when the spacing band read 0, and fixed.
  - Now every letter stands on 0 and the heads peak at 478. Every outline moved up by the same 44.3 units, rounded to whole units point by point; no shape changed.
- **The spacing kept.** The spacing measured a fixed band, 0 to 470 units. Left there, it would have taken in the feet's points and left out the heads' tips: up to 9 units of side bearing and 365 kerning pairs changed.
  - So the band now runs from the line the foot strokes end on, up by the x-height (`write_font`'s `band_from`; 44.3 to 514.3 units), as it always did on the letters. The build prints it.
  - Left: the re-rounding. f's left bearing moved by a unit, and 34 kerning pairs moved by one step of 5, either way.
- **Metrics.** Every descender now lies within the font's descent of 250 units (h, j, p and q reached -276 before). The declared x-height stays 470 (it sets the scale: Pugin's 205 px); the built heads stand at 478.
- **Checked** set large with Lombardic initials ("Dominus", "Salve", "Agnus"), before and after, with the baseline drawn in (`proof/baseline.png`, not in git): the feet's points now sit on the line with the capitals.
- **Line height** (Josh: "Do we have a particularly large lineheight set in the css, or is a large lineheight baked into the font?", then "Set the lineheight tighter").
  - **Measured at 80 px.** The font's own line height is 96 px (1.2 em: 950 above the baseline, 250 below), though its tallest letters reach only 724. The proof's `line-height: 1.3` gave 104 px. The Lombardic initials inherited it at 1.12 em with their 1000-unit ascent, so lines with an initial grew to 117–118 px.
  - **Now** the proof sets `.set` at `line-height: 1.1`, and the initials at `line-height: 0`, so they no longer push lines apart: 88 px baseline to baseline at 80 px, 44 at 40 px.
  - **Clearances.** The textura reaches 58 px above its baseline and 19 below, so descender to ascender is at least 11 px. The tallest initial under the deepest descender still clears by 4 px.
- **The proof page's room** (Josh: "Let's give the page some significant more padding, and a bit more space between text blocks", "(at the top)").
  - The page now has 120 px of padding at the top, 56 at the sides and 128 at the bottom (at phone width, 56, 16 and 80).
  - Paragraphs are 1.4 em apart, the set lines have 32 px above and below, and headings have 72 px above them.
- **A stale description fixed.** The pen table on the proof called `bottom` "the baseline". It now says it is where a minim's foot stroke ends, with the baseline below it at the points of the feet.
- **f, a and t exported for Josh to draw over** (Josh: "Export the f a t, so I can fix them up as well."). `references/export-f.svg`, `export-a.svg` and `export-t.svg` are made as the g's, p's and r's were: the built outline over Pugin's letter, in plate pixels.
  - Their guides now mark the baseline where it stands since the fix, at the points of the feet, in place of the line the foot strokes end on.
  - The f's canvas is wide (561 px): it takes in Pugin's f, whose loop and swash reach far past the plain one.
- **Josh's f** (brief `2026-10-29-textura-f.md`; decision 0014, amended). Josh: "t is ready", then "sorry - f, not t".
  - **What he changed.** He kept the stem below the crossbar and the tail. The top folds over and comes down on the right in a long arm, with a narrow slot open below it. The crossbar is lower and shorter on the left. One shape.
  - **Placed** at one unit to the pixel, at (706.968, 3228.210). The tail's lowest and leftmost points lie the same distance apart in both, to a thousandth of a pixel; the stem's edges below the crossbar then fall on the built stem's to a pixel.
  - **Built as it stands** (`f()` uses `OUTLINES`). It is 35.5 px from Pugin's f, against the construction's 31.3; neither has his loop and swash.
  - **Spacing.** The pairs after f close up, since the construction's arm reached far over the next letter: "fb", "fh", "fk", "fl" 125 → 40 units, "fi" 70 → 45, "ft" 70 → 30. f's right side bearing went from -122 to -44.
    - The closest any letter after f now comes is 10 units ("fi", "ff").
    - The other letters' side bearings moved by up to 3 units through the joint fit; 120 kerning pairs changed.
    - In words ("of fifty after", "soft left half") the f sits in the rhythm.
- **Josh's t** (brief `2026-10-29-textura-t.md`; decision 0014, amended). Josh: "t is ready".
  - **What he changed.** He kept the stem and the foot with its spur. The crossbar now ends on the right in a small curled flag, as Pugin's does, and on the left in a short point. The top has a small notch on its left.
  - **Placed** at one unit to the pixel, at (2448.241, 3255.923). The foot's point and the end of its spur lie the same distance apart in both, to a thousandth of a pixel, and the stem's edges then fall on the built stem's row by row.
  - **Built as it stands** (`t()` uses `OUTLINES`). It is 1.14 px from Pugin's t, against the construction's 1.51; it overlaps his ink 93%.
  - **Spurs.** Its spur is part of the drawing, so there is no `t.nospur`: 12 letters now have spurs under `ss01`.
  - **Spacing.** t's side bearings moved by up to 4 units and the others' by a unit at most; 42 kerning pairs changed, most by 5. The crossbar's new left point meets the c's top and the r's flag, so the clearance check opened "ct" 40 → 60 and "rt" 30 → 55. In words, "act" and "art" sit a little more open than before.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-baseline.md`, `docs/brief/2026-10-29-textura-f.md`, `fonts/pugin-textura/references/hand-drawn-f.json`, `docs/brief/2026-10-29-textura-t.md`, `fonts/pugin-textura/references/hand-drawn-t.json`, this log, `fonts/pugin-textura/references/export-f.svg`, `export-a.svg`, `export-t.svg`
- **Edited:**
  - `tools/type/textura_letters.py`: `baseline`; every construction returns it; `bottom`'s description; f and t drawn from Josh's outlines
  - `docs/decisions/0014-textura-drawn-outlines.md` and the decisions index, `docs/roadmap.md`: the f and the t
  - `tools/type/textura.py`: the editor's check uses it; `write_font` spaces over the band from the foot strokes' line (`band_from`); the proof's line height, padding and spacing
  - `fonts/pugin-textura/`: the README (the baseline; the f and t rows; spurs); the rebuilt UFO, OTF, recipes (time stamps), spacing and proof

## Open threads
- The fonts' declared heights carry empty space above the letters: the textura's 950 against its tallest 724, the Lombardic's 1000 against 722. Fitting them to the letters would tighten their default line height wherever CSS leaves it to the font. Plate 10's capitals may need some of it.
- The OS/2 x-height says 470 while the heads stand at 478; it could say 478.
- The spacing band still leaves the feet's points out (they count as below the band, with the 20-unit clearance). Measuring from the new baseline instead would respace every letter a little (up to 9 units); only if Josh wants it.
