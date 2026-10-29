# 0012 — The textura's adjustments by hand: held stroke measurements, set in a stroke editor

- **Status:** accepted
- **Date:** 2026-10-29
- **Decided by:** Josh Goforth

## Context
Working on the e's crossing member, Josh asked: "Do you want to me me manually adjust these detail lines?" Then he asked for the means: "Yes, build a stroke editor for the textura proof page: drag a stroke's nodes and settings, saved into the recipe so the build keeps them." ([brief](../brief/2026-10-29-textura-stroke-editor.md))

The Lombardic's adjustments by hand are recorded moves of outline points (decision 0010). The textura is different: each letter is the strokes of a simulated pen, through its own named measurements (decision 0008). Moving its outline points would fight the pen: the next build draws the pen again.

## Decision
Josh: "build a stroke editor for the textura proof page: drag a stroke's nodes and settings, saved into the recipe so the build keeps them."

- **What is adjusted.** A letter's own measurements: the nodes of its strokes (a pair of measurements, `name.x` and `name.y`, in plate pixels) and their settings (handle lengths, headings, a pip's size, how a spiral tightens). The family's shared measurements are not; those stay in `source.json` and `family.json`.
- **Where.** On the textura proof page, served by `tools/type/type.py serve` (the `font-proofs` entry in `.claude/launch.json`).
  - Each letter Pugin drew has **Edit strokes**.
  - In the editor, drag a node, or nudge it with the arrow keys (Shift for more); set the rest with sliders.
  - As they move, the server draws the letter again with the same code as the build. It shows the outline over Pugin's, how far his edge lies from it, and whether it passes the outline checks.
  - Undo and Back to saved are there. The letters Pugin didn't draw (u, w, j) take their measurements from others and are not edited.
- **How it is kept.** Save holds the changed measurements in the letter's recipe (`held`), which every fit keeps as it is. They are also listed in `held_by_hand`, so they can be told from measurements held at Josh's word. A held measurement can be let go; on the next Save and rebuild the fit sets just those again.
- **Rebuilding.** Save and rebuild runs `textura.py build pugin-textura --fit none` (no letter refitted, except measurements just let go) and the proof, then reloads the page.

## Amendment, 2026-10-29: the split top's settings
Josh: "Yes, add a panel to the stroke editor for the split top's family settings, so I can tune them by hand and see all five letters change." ([brief](../brief/2026-10-29-textura-split-top-panel.md))

- **Edit the split top** on the proof page opens the five settings that b, d, h, k and l share (`fork_notch`, `fork_flare`, `fork_out`, `fork_tip`, `fork_lean`), with sliders, and draws all five letters as they move.
- Save holds them in `source.json`'s `held`, as Josh's earlier corrections were, and lists them in `held_by_hand` there. So the rule above that the family's shared measurements are not adjusted now has this one exception. Other groups of family settings can be added the same way (`Workbench.GROUPS`) if Josh asks for them.

## Consequences
- Adjustments survive every rebuild and refit, since the fit never moves a held measurement, and they are reviewable in git as part of the recipe.
- They stay inside the pen's model. An adjustment can't make a shape the strokes can't make, so a change that needs a new stroke or a new kind of join is still a change to the construction.
- If a construction is changed and a measurement renamed, its held value no longer applies; the editor lists only the letter's current measurements.
- Point moves on the outline, as for the Lombardic (decision 0010), are not offered for the textura. If a final optical touch ever needs one, it would be a new decision.
