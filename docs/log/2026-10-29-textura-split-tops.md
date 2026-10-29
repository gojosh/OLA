# 2026-10-29 — Pugin Textura: split tops for b, d, h, k and l

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-split-tops.md`). Josh: "we need to make the simple split top for the b, d, h, k, and l. This is known convention in blackletter type. Pugin turns them highly decorative, which we will ultimately support through dynamic alternatives, but for now, we need a simple, clean split top that is consistent between the characters I listed, each spilt coming to a gentle rounded tip."
- **What was there.**
  - b, h, k and l had a fork: the head stroke from the upper left and a short arm up to the right. Each arm was fitted to Pugin's flourished top, so the forks differed from letter to letter.
  - The d had an arm leaning back over its bowl.
- **Pugin's d, looked at again on the plate.** Its stem is upright, with the same split top as the others, flourished left over the bowl and right into a loop. The plain d had taken the left flourish for an arm. It now has an upright stem with the split top.
- **The split top** (`split_top`): one shape, the same on all five.
  - The stem, as wide as the pen makes it, splits into two horns with a V notch between them.
  - Each horn's outer edge leaves the stem's edge and flares a little outward into a rounded tip; its inner edge runs straight down into the notch.
  - The tips' tops stand where the old forked tops reached.
  - It is a filled shape (`nib.Shape`, which the pip, `nib.Dot`, now is a kind of). The stem below it is a flat-topped minim whose own cut lies under the shape.
- **Its settings are the family's, held** in `source.json`, so every ascender has the same top and the fit never pulls it toward Pugin's flourishes:
  - first: notch 13 px deep; horns leaving the stem 26 px below their tops; tips standing 4 px beyond the stem's edges; tip radius 3 px; horns running into their tips at 20° from upright;
  - then, after Josh's word below: 20, 36, 9 and 3 px, and 28°;
  - now: widening from 70 px down, notch 24, tips 14 px out, 3 px round, 32°.
- **Wider, longer** (brief `2026-10-29-textura-split-tops-2.md`). Josh: "This is a good start, but too conservative - the split should be a bit wider, and the points a bit longer."
  - The notch now runs 20 px deep (from 13).
  - The horns leave the stem 36 px below their tops (from 26).
  - The tips stand 9 px beyond the stem's edges (from 4) and are met at 28° from upright (from 20°).
  - The tips are at the same height, with the same 3 px rounding.
- **Widening from lower down** (brief `2026-10-29-textura-split-tops-3.md`). Josh: "notice how Pugin's start widening out the stem gradually, so the split top is larger?"
  - **Measured on his letters' bodies:** the stems stand 37–40 px wide and begin to widen about 70 px below the top, slowly and then faster. b's runs 38, 40, 42, 45, 49, 54 and 67 px from 3300 up to 3220.
  - **Ours** now begins to widen 70 px below the tips' tops (from 36). The tips stand 14 px beyond the stem's edges (from 9), the notch is 24 px deep (from 20), and the horns are met at 32° (from 28°).
  - b's stem now runs 36, 37, 38, 40, 44, 48, 54 and 63 px over the same heights, close to his.
- **Results.**
  - Only b, d, h, k and l changed shape; all 27 pass.
  - Measured against Pugin's letters, which keep their loops, b, d and l sat about 12 px off and h 8 px at first. With each step toward his shape they came closer: now b 10.5, d 10.0, l 9.0, h 6.8 and k 2.7 px. What remains is his flourishes.
  - Checked in the browser at display and text sizes, and in the stroke editor, which draws the new d over Pugin's upright stem.

- **A panel for tuning it by hand** (brief `2026-10-29-textura-split-top-panel.md`; decision 0012, amended). Josh: "Yes, add a panel to the stroke editor for the split top's family settings, so I can tune them by hand and see all five letters change."
  - **Edit the split top**, above the letters on the proof page, opens the editor on the five settings, with sliders and their meanings, and draws b, d, h, k and l side by side over Pugin's.
  - Each letter is shown in the same window (120 × 220 plate px from its tips' tops) at the same scale, so the tops compare. The status gives each letter's distance from Pugin's edge and flags any outline check that fails.
  - **Server** (`textura.Workbench`): `GROUPS` names the group (its settings by prefix, `fork_`, and its letters); routes `GET /api/pugin-textura/family/<group>`, `POST .../family/<group>/outlines` (all five drawn in about 0.3 s) and `POST .../family/<group>/hold`.
  - Save holds the changed settings in `source.json`'s `held` and lists them in its `held_by_hand`. Save and rebuild runs the same rebuild as a letter's (`--fit none`, which still takes the family's held values).
  - **Tested in the browser:** the panel opens, the sliders redraw all five, and the e's own editor still opens normally after it. Josh used it while it was being tested: he saved the notch at 15.5 px (from 24), held by hand in `source.json`, and rebuilt from the panel (Save and rebuild, 10:50), which tested that path too.
  - **Rebuilt again** at Josh's request (`build --fit none`, then the proof). It matched his rebuild exactly: no glyph, recipe, family value or spacing changed, and all 27 pass. With the 15.5 px notch, b sits 10.44 px from Pugin's edge, d 10.07, h 6.75, k 2.84 and l 9.37.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-split-tops.md`, `docs/brief/2026-10-29-textura-split-tops-2.md`, `docs/brief/2026-10-29-textura-split-tops-3.md`, `docs/brief/2026-10-29-textura-split-top-panel.md`, this log
- **Updated:**
  - `tools/type/nib.py` (`Shape`; `Dot` is one)
  - `tools/type/textura_letters.py` (the split top's five family settings; `split_top`; `ascender` uses it; b, d, h, k, l; `ascender_arm` gone)
  - `fonts/pugin-textura/` (`source.json`: the split top held; the UFO, recipes, spacing, the README)
  - `tools/type/textura.py` (`Workbench`: family groups; the proof page's Edit the split top and its grid), `tools/type/textura_editor.js` (group mode), `tools/type/type.py` (the family routes)
  - `docs/decisions/0012-textura-stroke-editor.md` (amended)
  - `docs/roadmap.md`

## Open threads
- **The flourished tops** (Pugin's loops), as alternates: how they're reached (stylistic sets, contextual alternates) is still Josh's call.
- **The old arm measurements** (`arm.*`) are left in the five recipes as fitted; nothing reads them now. The next full build drops them.
