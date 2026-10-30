# 2026-10-29 — Pugin Textura: split bottoms on p and q; the p's bowl; Josh's r and p

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-split-bottoms.md`). Josh: "lets do splits on the bottom of p and q, in the same manner we did split tops on b, d, h, k, and l".
- **The split bottom** (`split_bottom`): the split top turned upside down at the descender line, with the same five held settings, so tuning one tunes both.
  - The split top's outline is now drawn by `_fork`, which `split_top` and `split_bottom` share. The bottom flips that outline about the line where its tips' bottoms stand: where the nib's bottom corner would be at the descender line, as low as the turned-out foot reached before.
  - The stem above it is a minim that stops with the nib's cut. Its lowest corner is 2 px above the notch, so the cut stays inside the shape, as the top's does.
  - It is as wide as the pen makes the stem there. By the descender line the nib has turned to its angle at the feet (50°), so the bottom is a little narrower than the tops: the stem 35 px against 37, the tips 62–63 px across against 65.
- **p and q.** p's descender and q's right stroke stop above the split instead of turning out into a foot. Nothing else in either letter moved. q's left foot still meets the right stroke at the baseline, as before.
  - Pugin's body edge from them: p 23.7 px (27.1 with the foot), q 12.2 px (12.3). His descenders run on into swashes, so these numbers are mostly his swashes.
- **Spurs.** The split took p's and q's last free feet, so neither has a spur and the build no longer makes `p.nospur` or `q.nospur` under `ss01`.
- **Checked.** Every outline other than p's and q's is identical to the build before, so the refactor left the split tops exactly as they were. All checks pass.
  - The joint spacing fit moved the other letters' side bearings by a unit at most. q's right side bearing moved from -57 to -13 units, since its foot no longer reaches out right. That changed kerning in 41 pairs, most of them after q.
- **The panel.** **Edit the split top** is now titled "The split top and bottom of b, d, h, k, l, p, q". It draws all seven, with p and q framed at their bottoms (`Workbench.GROUPS` `below`). Moving a slider redraws all seven together.
- **A stale number fixed.** The README still gave the notch as 24 px; Josh set it to 15.5 px in the panel.
- **p and r exported for Josh to draw over** (Josh: "export p and r for me to manually improve"). `references/export-p.svg` and `references/export-r.svg` are made the way `export-g.svg` was: the built outline over Pugin's letter cropped from the flattened plate, with the family's lines as guides, in plate pixels. The r's outline carries its spurs, as the font has them.
- **The p's bowl, repaired before export** (brief `2026-10-29-textura-p-bowl.md`). Josh: "you don't need to add the extra flourish on the left side of the p, but you do need to fix the bottom of the bowl - it's pretty standard - not sure why it has this weird diagonal stroke for the bottom of the bowl."
  - Before, the bowl's right stroke stopped with the nib's cut, and a second stroke closed the bowl: a long thin diagonal starting right of the right stroke and running down-left to the stem. Its first cut stood out past the bowl like a flag.
  - **A wrong turn.** I said there were no textura samples in the repository and looked to plates 11 and 12. Josh: "you've somehow lost track of @09-alphabets-no-1.deshaded.png". Plate 9's own p, the letter we are building, shows the standard form. Measured there:
    - the bowl's bottom is a foot leaving the stem, down to the right, to a point at about (1996, 3532);
    - the right stroke stops with the nib's cut;
    - the two meet in one straight edge, as on b and o.
    - His foot comes into the stem from the curl on the left.
  - A first try, with the right stroke turning in to the stem as one stroke, was fitted and dropped. The fit flattened it into a square, thick band, pulled by his curl.
  - **Now the p closes as b does.** The right stroke stops with the nib's cut. A foot leaves the stem at the baseline (`foot_from`, a minim's foot turn on its own, its first cut inside the stem). The two meet in one straight edge (`edge_below`).
    - The bowl is 76 px wide against b's 64, so the foot runs on further, as d's and q's do: 41 px, fitted to his, against the family's 27. Its point stands about 15 px left of his, since his foot comes in flatter from the curl.
    - The right stroke now stops at 3504 (it was 3481), fitted. Its range was widened by 10 px, since the fit sat on the old bound.
  - **The join at the top.** Josh: "The top of the bowl needs the spur to connect it, like other contexts." The bowl's head is now joined to the stem by a hairline (`minim`'s `after`), as the n's second minim, h's leg and k's bowl are. The counter is closed, so p is now two contours.
  - Pugin's body edge from it: 23.5 px (23.7 before), almost all of it his curl and swash.
  - Only p's outline changed. Spacing moved the other letters by a unit at most. p's right side bearing moved from -9 to 17 units and its advance from 311 to 308; 55 kerning pairs changed.
  - p's recipe lost the old diagonal's measurements (`bowl_foot.*`), which the build had kept although nothing used them. A build with nothing fitted then gives the same p.
  - `export-p.svg` was made again from the repaired p.
- **Josh's r** (brief `2026-10-29-textura-r.md`; decision 0014, amended). Josh drew his r over `export-r.svg`: "Yes, place the r".
  - **The drawing.** One shape: the top spur, the stem, the foot with its spur, and the flag with a ball curling under it.
  - **Placed** at one unit to the pixel, its top left on the built r's (`hand-drawn-r.json`). Its head stands on the other letters' heads and its foot on their feet (3321.6 and 3530.2 px).
    - He drew it at our height. Placed where it overlaps Pugin's ink best, it would stand 1.6 px lower, both at the head and at the foot (80% overlap against 79%).
  - **Built as it stands**, as the g is (`OUTLINES`; `r()` uses it first). It measures 2.3 px from Pugin's r, where the construction measured 5.2 px.
  - Only r's outline changed, and the others' spacing moved by a unit at most.
    - The ball reaches 25 px further right than the built flag, so r's advance grew from 180 to 226 units; 37 kerning pairs changed.
    - In words ("error", "mirror", "rare"), the ball sits in the white under the flag.
  - **Spurs.** Its spurs are part of the drawing, so the build makes no `r.nospur` and `ss01` leaves the r as it is. The r is spaced with its top spur counted, not set into the white before it, so the clearance check opens 58 pairs instead of 72.
- **Josh's p** (brief `2026-10-29-textura-p-drawn.md`; decision 0014, amended). Josh: "Ok - hand-drawn p is in...", drawn over the repaired p's export.
  - **What he drew.** Pugin's flourishes on the left, after all: a curl off the head, and the bowl's foot sweeping across the stem into a curl. The bowl's head is joined by the hairline, and the split bottom is as built.
  - **Placed** at one unit to the pixel, at an offset of (1891.983, 3321.564). The head's peak, the split bottom's lowest point and its two tips all give that offset to a thousandth of a pixel, so he kept them exactly.
  - **Holes, new.** It is the first drawing with a hole, and the build filled each drawn path as a solid shape, joined to the rest.
    - Now a drawing is filled even-odd, as his drawing program fills it (`textura_letters.drawn`; `nib.Shape` takes `holes`, cut from it in `nib.outline`). A path inside another is a hole: the bowl's counter.
    - A first test went by each path's first point. The curls start where they touch the stem, so they were taken for holes and left out. It now goes by most of a path's points.
    - The curls touch the stem (0.6 px² of overlap, and none) and are joined to it.
    - The r and g now go through `drawn` too, and the s, g and r outlines are exactly as before.
  - **The p as built.** Two contours: the letter with its curls, and the counter. It is 20.9 px from Pugin's p (the construction, 23.5), most of that his swash.
  - **Spacing.** Only p's outline changed, and the other letters' bearings moved by a unit at most. The curls take space on the left: p's advance grew from 308 to 331 units and its left bearing from -25 to -31.
    - 83 kerning pairs changed, most of them before p: "ap" 20 → 60, "ip" 20 → 55, "gp" 35 → 80, "fp" 55 → 90.
    - In words the white before p is wider than the rest of the rhythm. Asked whether to space the p without its curls, Josh: "Leave it as is" (Q41, answered).
  - **The split's panel** now leaves p out, since its split no longer moves with the settings: six letters, q alone framed at its bottom.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-split-bottoms.md`, `docs/brief/2026-10-29-textura-p-bowl.md`, `docs/brief/2026-10-29-textura-r.md`, `docs/brief/2026-10-29-textura-p-drawn.md`, `fonts/pugin-textura/references/hand-drawn-r.json`, `fonts/pugin-textura/references/hand-drawn-p.json`, this log, `fonts/pugin-textura/references/export-p.svg`, `fonts/pugin-textura/references/export-r.svg`
- **Edited:**
  - `tools/type/textura_letters.py`: `_fork`, `split_bottom`; `split_top` uses `_fork`; p and q; `fork_notch`'s meaning; `foot_from`; p's bowl joined at the top and closed at the bottom as b's is; r and p drawn from Josh's outlines when they exist; `drawn` and `_inside` (a drawing filled even-odd); the split's texts
  - `tools/type/textura.py`: the panel's group takes in q (and p, until Josh drew it), with `below`, and is retitled; the proof page's text
  - `tools/type/textura_editor.js`: frames q (and, until Josh drew it, p) at its bottom
  - `tools/type/nib.py`: `Shape` may have holes, cut from it in `outline`
  - `fonts/pugin-textura/`:
    - the README (split bottoms, the kit, p and q rows, the panel, the notch; the p's bowl; edges where strokes meet; the r row; spurs, top spurs and spacing);
    - `source.json` (the fork note);
    - the rebuilt UFO, OTF, recipes, spacing and proof. The recipes changed only in their build time stamps, except p's.
  - `docs/decisions/0012-textura-stroke-editor.md`: a line in the amendment on the panel's seven letters
  - `docs/decisions/0014-textura-drawn-outlines.md` and the decisions index: the r
  - `docs/roadmap.md`, `docs/open-questions.md` (Q41, asked and answered)

## Open threads
- Whether the bottoms should have settings of their own (a shorter flare, say, since the descender is shorter than the ascender), or keep sharing the top's. They share for now, as "the same manner" asked.
- h's leg still turns out into a foot at the descender line; Josh asked for p and q only.
- Pugin's swashes on p and q, as alternates, with his flourished tops.
- The r has no spurless form under `ss01` now. If wanted, Josh could draw one, or its spurs could be cut from the drawing.
