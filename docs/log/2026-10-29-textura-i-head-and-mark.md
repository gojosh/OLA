# 2026-10-29 — Pugin Textura: the i's light head and top spur, and the mark over i and j

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-i-head-and-mark.md`). Josh: "the i should use the thinner nib on the first angle of the stem, and add the top spur. Also, for the dot over the i and j, move it a bit left, and make it slightly thicker. Since we don't have dots from Pugin, see what other 15th century blackletter converted to a modern typeface you can compare to to see what a nib rotation is typically used."
- **Looking at 15th-century textura types for the mark.**
  - **Digital revivals found:**
    - Alter Littera's Gutenberg B (2012), from scans of the 42-line Bible: no longer on sale, and the foundry's site has a broken certificate;
    - Missaali (Tommi Syrjänen, 2016), from Ghotan's *Missale Aboense*, Lübeck 1488;
    - Alter Littera's Psalterium, from the Mainz Psalter (1457).
    - None could be looked at in the browser. Missaali's manual came as a file download (a save dialog Josh could dismiss).
  - **The 42-line Bible itself**, a public-domain scan of a Basel leaf on Wikimedia Commons: its i's carry a fine hairline arc over the stem, made with the corner of the nib.
  - **Josh's sample** ("vigiliae", a later textura): a short, heavy oblique stroke, about as long as the stem is wide, lying flatter than the heads, by eye about 30°. That is the nib turned a little flatter and moved a short way.
  - **Josh:** "I'd rather not do the little half circle concept - looks like we may have some freedom to invent."
- **The mark** (`i_stroke`, `nib.dab`): a touch of the full nib, turned to 30° and moved 10.5 px down the heads' diagonal.
  - It is about 17 px across (from 14) and about 48 px long (from about 60).
  - It is centred 4 px left of the stem's centre (from 4 px right) and 46 px above the x-height line (from 40), clear of the head it nearly touched.
- **The i's head, light** (`nib.Stroke` with a pressure that changes along it; `nib.ramped_region`).
  - The head keeps the light nib (80%) along its diagonal, then comes to full weight through the turn, so it meets the full stem without a step.
  - **How it's drawn:** each nib edge sweeps the ground between the paths of its two corners, as for a nib of one width. The corners' paths are traced as the nib widens and fitted with cubics within 0.05 px.
  - **First tried:** the hull of the nib at the ends of short pieces. Simplifying those pieces failed, and joining them one at a time left a node every 1.5 px (91 segments); the traced corners give 38.
- **The top spur** (`spur_into`): a 10 px hairline coming up into the head from the lower left along the nib's edge, the same length as the foot spurs. Pugin's first heads (i, n, m, r) have a small lip there; his is a little longer and rounder. It is left out under `ss01` with the other spurs.
- **Spacing held.** The target white was measured on the i's whole ink, spurs and mark included, so the new i would have moved it from 57.7 to 60.0 and respaced every letter. On the i without spurs it would be 64.7: the foot spur's tip had been setting the i's width. It is now held at 57.7 (`target_white` in `source.json`, with a note).
  - The other letters' side bearings moved by a unit at most, and no advance by more than one, since the i's pairs are part of the joint fit.
  - 71 kerning pairs changed, most with i or j. Pairs whose left letter reaches over toward the moved mark (c i, f i, h i) opened by 10–15 units.
  - The j's right side bearing grew from −12 to 15, since its mark no longer reaches past its stem.
- **The j, the same** (Josh: "Yes, give the j the same light head and top spur as the i."): i and j now share `light_head`, which writes a minim's head light, with the top spur. Only the j changed shape. e's, f's and y's side bearings moved by a unit, 29 kerning pairs changed (most with j), and the j now has a form without spurs under `ss01` (16 letters have them).
- **n, m and r** (brief `2026-10-29-textura-top-spurs.md`; Josh: "add the top spur to the first heads of n, m and r, as Pugin's have"): their first minims have the top spur (`entered`). Only they changed shape; n now measures 1.69 px from Pugin (from 1.75), r 5.18 (from 5.21), m 2.1.
- **Spacing round the top spurs.**
  - **Counted** like any part, the spur became n's, m's and r's left edge. Their left side bearings went from −27 to −39 and their advances grew by 3–4 units. 91 kerning pairs before them opened by 15–20 units, so "on", "bn" and "vn" went from 20 to 35. Some of the openings put down above to the mark were the i's top spur too.
  - **Left out:** the letters are now spaced as drawn without their top spurs (a third drawing in the build, `top_spur` off) and set with them, lined up by their right edges. n, m and r keep their side bearings to a unit.
  - **Collisions:** left out, the spur reaches about 10 units into the letter before; the nearest approach before n was 0.2 units (without spurs it is 7–9). A last check by true distance opens any pair where a top spur comes within the clearance of the letter before: about 100 pairs, before n, m and r by a median of 15 units, after f by 40–45.
  - At 4 units clear (65 pairs opened) the medians are 5–15. Allowed to touch, nothing opens. A comparison of the three, set with the font's kerning (HarfBuzz), went to Josh (`fonts/pugin-textura/proof/top-spur-clearance.png`, not in git). Josh: "4 units clear looks good". So `clearance_top_spur` is 4 in `source.json`, and the build is the B he saw: 65 pairs opened.
- **ſi and fi.** The mark's move left and its flatter angle bring it under the arm of ſ and f, so the check on parts above the x-height opens "ſi" by 60 units and "fi" by 15–30 (since the mark change, not the spurs).
- **The proof page's cards** now widen to show anything drawn outside Pugin's box; the top of the mark was cut off.
- **Results.**
  - Only i and j changed shape; all 27 pass.
  - The i measures 2.37 px from Pugin's body edge (from 2.07): its head is lighter than his, which is fuller to the upper left. It was built with `--fit none`, not refitted.
  - **Checked:** in the browser (the card, and the stroke editor with the server restarted) and set in words at display and text sizes.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-i-head-and-mark.md`, `docs/brief/2026-10-29-textura-top-spurs.md`, this log
- **Updated:**
  - `tools/type/nib.py`:
    - a pressure that changes along a stroke: `pressure_at`, `ramped`, `ramped_region`, `_trace`;
    - `dab`.
  - `tools/type/textura_letters.py`:
    - `spur_into` (and `top_spur`), `entered`, `light_head`, `i_stroke`; `i`, `j`, `n`, `m`, `r`;
    - `nib_for` uses `pressure_at`.
  - `tools/type/textura.py` (the held target white; spacing without top spurs and the check that keeps them clear; cards widen to the outline)
  - `fonts/pugin-textura/` (`source.json`'s `target_white`; the UFO, spacing, the README)

## Open threads
- **ſi and fi**: the mark now meets the arm of ſ and f, which opens those pairs widely. The mark could sit lower or further right, or ſi and fi could be ligatures, as in many blackletter types (Q38).
- **The mark's settings** (`DOT_ANGLE` 30°, `DOT_MOVE` 10.5 px, its place) are constants in `textura_letters.py`. They could be given an editor panel, as the split top's are, if Josh wants to tune them by eye.
