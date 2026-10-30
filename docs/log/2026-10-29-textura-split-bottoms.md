# 2026-10-29 — Pugin Textura: split bottoms on p and q

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

## What changed
- **Created:** `docs/brief/2026-10-29-textura-split-bottoms.md`, this log
- **Edited:**
  - `tools/type/textura_letters.py`: `_fork`, `split_bottom`; `split_top` uses `_fork`; p and q; `fork_notch`'s meaning
  - `tools/type/textura.py`: the panel's group takes in p and q, with `below`, and is retitled; the proof page's text
  - `tools/type/textura_editor.js`: frames p and q at their bottoms
  - `fonts/pugin-textura/`:
    - the README (split bottoms, the kit, p and q rows, the panel, the notch);
    - `source.json` (the fork note);
    - the rebuilt UFO, OTF, recipes, spacing and proof. The recipes changed only in their build time stamps.
  - `docs/decisions/0012-textura-stroke-editor.md`: a line in the amendment on the panel's seven letters
  - `docs/roadmap.md`

## Open threads
- Whether the bottoms should have settings of their own (a shorter flare, say, since the descender is shorter than the ascender), or keep sharing the top's. They share for now, as "the same manner" asked.
- h's leg still turns out into a foot at the descender line; Josh asked for p and q only.
- Pugin's swashes on p and q, as alternates, with his flourished tops.
