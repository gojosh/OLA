# 2026-10-29 — Pugin Textura: the baseline

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

## What changed
- **Created:** `docs/brief/2026-10-29-textura-baseline.md`, this log
- **Edited:**
  - `tools/type/textura_letters.py`: `baseline`; every construction returns it; `bottom`'s description
  - `tools/type/textura.py`: the editor's check uses it; `write_font` spaces over the band from the foot strokes' line (`band_from`); the proof's line height, padding and spacing
  - `fonts/pugin-textura/`: the README (the baseline); the rebuilt UFO, OTF, recipes (time stamps), spacing and proof

## Open threads
- The fonts' declared heights carry empty space above the letters: the textura's 950 against its tallest 724, the Lombardic's 1000 against 722. Fitting them to the letters would tighten their default line height wherever CSS leaves it to the font. Plate 10's capitals may need some of it.
- The OS/2 x-height says 470 while the heads stand at 478; it could say 478.
- The spacing band still leaves the feet's points out (they count as below the band, with the 20-unit clearance). Measuring from the new baseline instead would respace every letter a little (up to 9 units); only if Josh wants it.
