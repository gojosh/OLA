# 2026-10-28 — Flattening the Pugin plates (fonts, step one)

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh wants to recover Pugin's alphabets (plates 9–12) as fonts. Step one: flatten each page so it is a true rectangle. He also asked for:
  - a 3D grid over the photograph, adjustable by hand;
  - all positioning and curvature data saved, so it can be revisited.

  Shading correction, using the 3D surface, is part 2.
- **What the photographs show.**
  - The pages lie flat against a glass platen; its edge is visible at the gutter.
  - They curve away into the gutter: the printed frame pinches in about 20 px top and bottom.
  - The vertical rules bow by about ±2 px in opposite directions on left and right. That is lens barrel distortion, not the page.
- **Built `tools/flatten`.**
  - Frame-rule detection: a line-segment detector seeds the rules, and centroid tracing follows them to sub-pixel accuracy.
  - A 3D model: a pinhole camera with radial distortion, plus a generalized-cylinder sheet whose depth is a spline that can't pass through the glass.
  - Robust least-squares fitting and arc-length unrolling.
  - Checks that re-measure the frame in the output.
  - A browser editor with the projected grid, sliders, a draggable depth profile, draggable page edges, preview and full render, and save.
- **Key finding: focal length.** One plate can't determine it, and it controls how much to widen letters near the gutter (3–65 px on plate 9 across plausible values). Solved by calibrating the lens jointly on plates 9, 11 and 12: f = 9,234 px, k1 = −0.0596, known to about ±15%.
- **Plate 10.** Its printed top rule is about 0.35° out of square. The other three rules fit to 0.57 px without it, and the letter row beneath it is level. It is excluded from the fit, with a note in the plate's file.
- **Results.** All four plates are rendered flat. The frame rules are straight to ≤ 2.3 px and square to ≤ 0.08°; RMS is 0.3–0.6 px.
- **Provenance.** The JPEG 2000 files were encoded with Kakadu v5.2.1. Together with the glass platen and cradle, that points to an Internet Archive scan. Added to Q19.

## What changed
- **Created:**
  - `tools/flatten/` (`flatten.py`, `editor.html`, `README.md`)
  - `reference/pugin-glossary/flatten/` (per-plate JSON and `_camera.json`)
  - `reference/pugin-glossary/flattened/` (previews in git; full-resolution PNGs ignored)
  - `.claude/launch.json` (starts the editor)
  - decision 0007 (proposed: tools in Python with uv)
- **Plate 8 added:** dark-ink detection, `flatten/08-principal-figures-of-shapes.json`, and its flattened previews.
- **Part 2 added:** `shade` command, shading model and editor panel; `flattened/*.deshaded.png` (ignored) and `*.deshaded.preview.jpg`.
- **Updated:** `.gitignore`, `AGENTS.md` (repo map), `reference/pugin-glossary/README.md`, `docs/open-questions.md` (Q18, Q19).

## Part 2: the gutter shading (same day)
- **Measured on the flattened pages.**
  - The gutter is 12–18% darker and warmer than the open page: blue drops most.
  - About 6% of the darkening starts on the flat part of the sheet, because the opposite page and the binding cut off light. So shading isn't a function of tilt alone.
  - Margins at the top, middle and bottom show nearly the same profile across the page.
- **Model.** In the flat (u, y) coordinates the fitted surface provides, the light is modeled per channel as log L = c + g0(u) + y·g1(u) + p(y). It is fitted robustly to bare-paper pixels, which lets it be removed under the letters as well.
- **Fixes along the way.**
  - Anchoring the light field at a page corner tinted the whole page. It now normalizes to the well-lit paper inside the frame.
  - Control points 45 px apart missed the narrow band the glass edge brightens. They are now 12 px apart at the gutter edge.
- **Results.** Paper evenness across the page went from 15–16.5% spread to 0.5–1.3%. The gutter-side quarter went from 87.5–89.5% of the open page to 99.8–100.1%. The gutter paper now matches the open page's color.
- **Added to the tool:**
  - a `shade` command
  - `<plate>.deshaded.png` outputs and previews
  - a `shading` block in each plate's file
  - an editor panel with a plot of the light, a strength control, a refit button, and previews with or without the correction

## Plate 8, the shapes catalog (same day)
- Josh: "This was an excellent effort. We got exactly what we needed out of the process. Let's do image 8 as well, with our shapes catalog."
- **Detection for hairline frames.**
  - Plate 8's frame is a thin dark hairline, about a tenth as strong as the red rules, so the detector gained a "dark" ink measured against the local paper.
  - Candidate rules must have plain paper on both sides, which rejects page edges and the fore-edge stack.
  - Traces may jump small gaps but not sudden sideways steps; that keeps them off Pugin's signature.
  - The output check now looks for each rule where the fit puts it, since the glass edge's line had been mistaken for the frame's left rule.
  - Plates 9–12 still detect unchanged.
- **Plate 8 results.** Fitted with the shared lens: 0.98 px RMS. Rules are straight to ≤ 2.9 px and square to 0.09°. Paper brightness spread went from 13.5% to 0.15%.
- **Lens.** Plate 8 was left out of the lens calibration: joining it drove the solver to an implausible focal length without improving the other plates.
- **What the figures showed.** Plate 8's squares and circles give the first check on width. The gutter-side square's width-to-height ratio went from 0.967 to 0.991 against 1.008–1.010 for its neighbours, and the gutter-side circle is about 1.2% narrower than its neighbours. So the gutter correction is roughly 1–2% too gentle on every plate. The likely cause is that the focal length is short within its ±15% band.

## Refining with plate 8's figures (same day)
- Josh: "Use plate 8's squares and circles to refine the lens calibration, then re-render plates 8–12 and show me the before/after widths."
- **Figures in the fit.** Measured each figure's four extreme points in the photograph and stored them as `shapes` in plate 8's file. Fixed a measurement bug along the way: the shaded gutter side of a square was too faint for a global threshold.
  - The fit back-projects the points onto the sheet and requires each family to share one width-to-height proportion.
  - Circles get ±0.3 px tolerance and squares ±2 px.
  - Robust down-weighting was moved from a global loss to the frame points only, because it had been discounting the figures.
  - Calibrated on plates 8, 9, 11 and 12 (frames plus figures): f = 9,456 px, k1 = −0.0649.
  - Re-rendered and re-shaded plates 8–12.
- **Plate 8 is fixed.** The gutter square went 0.991 → 1.005 width ÷ height (family 0.998–1.010) and the gutter circle 0.990 → 1.000 (family 1.002–1.003). The other six figures are unchanged within 0.1%.
- **Plates 9–12 barely change** (−0.09% to +0.14% in the band nearest the gutter). The diagnosis is that the frame rules alone can't resolve how sharply the sheet bends about 300–400 px from the gutter. The figures supplied that for plate 8 only. Neither the lens, less smoothing, nor a fuller lens model transfers it. Plates 9–12 likely keep a shortfall of about 1% in the first letter column.
- **Editor.** It now shows the figures (magenta) and lets them be switched in or out of the fit.

## Open threads
- **Width references for plates 9–12:** set aside. Josh: "Leave plates 9–12 as they are." They keep a possible shortfall of about 1% in the first letter column. Textura stem widths on 11–12 remain the candidate if it ever matters.
- **Next font step:** separate the inks on the evened pages and isolate each letter for vectorizing.
- **More plates in the lens calibration** would narrow f. That needs frame detection for non-red rules.
- **Decision 0007** awaits Josh. **Q18** now also covers whether the full-resolution flattened PNGs go into Git LFS.
