# Plate flattener

Unrolls the photographed Pugin plates (`reference/pugin-glossary/plates/`) onto true rectangles and removes the shading into the gutter. Done so far: plates 8 (principal figures of shapes) and 9–12 (the alphabets), the first step in recovering Pugin's alphabets as fonts.

The plates were photographed in their binding, behind a glass platen. Across most of each page the sheet lies flat against the glass. Toward the spine it falls away into the gutter, so the printed frame pinches in by about 20 px top and bottom, and letters near the gutter are compressed sideways. This tool models each photograph in 3D, fits the model to lines known to be straight on the printed page, and resamples the page flat.

## Run it

From the repository root. [uv](https://docs.astral.sh/uv/) installs the dependencies on first run.

```bash
uv run tools/flatten/flatten.py all 09 10 11 12      # detect, fit, and render
uv run tools/flatten/flatten.py serve                 # the grid editor, at http://127.0.0.1:8765
```

Other commands: `detect`, `fit [--fresh] [--free-camera] [--lock …]`, `render [--scale] [--auto-page]`, `shade`, and `calibrate <plates> [--sweep]`. Plates can be named by number prefix (`09`) or full id. `all` runs detect, fit, render and shade.

## The model

- **Camera.** A pinhole camera at distance f from the page, with:
  - one radial lens-distortion term (k1),
  - the principal point at the image center,
  - three rotations (tilt x, tilt y, turn).

  World units are photograph pixels on the flat part of the page, so a render at scale 1 keeps the original resolution.
- **Surface.** A *generalized cylinder*: the sheet bends only across its width, which is how paper bends.
  - Depth z(X) is a natural cubic spline through 12 knots, packed closely toward the gutter.
  - Two knots on the flat side are **anchors** fixed at z = 0. They define the plane of the glass.
  - The sheet may fall away from the glass but never through it (z ≥ 0).
- **Unrolling.** Each output column corresponds to an arc length *u* across the sheet. Letters near the gutter therefore regain their true width, not only their straight lines.
- **Fit.** Robust least squares on the printed frame's four rules, about 1,400 points per plate traced to sub-pixel accuracy. Every point also gets its own position along its line, so each residual is the point's distance from the model's line.

### Rule detection

Two inks are supported:
- **Red** (`redness`): the red rules of plates 9–12.
- **Dark** (`darkness`): hairline frames such as plate 8. It measures against the local paper level, so the shaded gutter isn't read as ink.

`auto` tries red, then dark; the ink found is recorded on each detected line.

Candidate rules come from a line-segment detector and must have plain paper on both sides. That rejects the page's own edges (dark board on one side) and the striped stack of leaves at the fore-edge. Tracing then follows each rule to sub-pixel accuracy. It jumps small gaps in a faint hairline, but refuses any step that moves more than 2 px sideways; on plate 8 that keeps it off Pugin's signature, whose "P" nearly touches the bottom rule. When checking a flattened page, the detector looks for each rule where the fit says it is, so the glass edge's line can't be taken for the frame.

## The lens is calibrated across plates

A single plate cannot tell a long lens with a deep gutter from a short lens with a shallow one: both straighten the rules equally well. They differ in how much to widen the letters next to the gutter, which can be anywhere from 3 to 65 px on plate 9. So f and k1 are fitted jointly on plates 9, 11, and 12, which were photographed with one lens. The result is stored in [`reference/pugin-glossary/flatten/_camera.json`](../../reference/pugin-glossary/flatten/_camera.json), and per-plate fits then hold it fixed.

- **Result (first calibration, frames of plates 9, 11, 12):** f = 9,234 px and k1 = −0.0596, consistent with roughly a 59 mm lens on a 21-megapixel full-frame camera. *Since refined with plate 8's figures: f = 9,456 px, k1 = −0.0649 (see below).*
- **Plate 10 left out:** its printed top rule is slightly out of square (see below).
- **Uncertainty:** the fit is shallow around the minimum, so treat f as known to roughly ±15% (`sweep` in the camera file). That is the main remaining uncertainty in the width correction near the gutter: on plate 12 it is about ±5 px over the 800 px nearest the gutter.
- **Lens terms tried and dropped:** a second distortion term (k2) and an off-center principal point are supported (`calibrate --full-lens`). On these plates they made the fit unstable for little gain, so they are off by default.

## Results (2026-10-28)

Measured by re-detecting the frame in each flattened page:

| Plate | Fit RMS | Rules straight to (max) | Frame square to |
|---|---|---|---|
| 09 | 0.92 px | 2.3 px | 0.08° |
| 10 | 0.57 px | 2.0 px (bottom, left, right) | 0.002° |
| 11 | 0.66 px | 1.5 px | 0.05° |
| 12 | 0.64 px | 2.0 px | 0.04° |
| 08 | 0.98 px | 2.9 px | 0.09° |

- **Plate 10's top rule** is excluded from its fit (`"weight": 0` in its file, with a note). With it, the fit is 2.4 px RMS; without it, the other three rules fit to 0.57 px. The first row of letters beneath it is level, so the rule itself was printed about 0.35° out of square. The flattened page shows it as printed.
- **A shared residual** of about 1.5 px remains at the fore-edge end of the horizontal rules on every plate. Its shape is the same on each sheet, which suggests the printed border (probably one stone for the whole series) rather than the paper. It is too small to matter for letterforms.

## Removing the gutter shading (part 2)

Paper falling into the gutter receives less light, and the light it does get is warmer, probably reflected off the cream page.
- **Size:** on plates 9–12 the gutter side of the page is 12–18% darker than the open page.
- **Color:** blue drops most (to about 0.80), red least.
- **Extent:** about 6% of the darkening begins on the *flat* part of the sheet. The opposite page and the binding cut off part of the light before the paper starts to curve, so shading isn't a function of tilt alone.

**Where the 3D model comes in.** The fitted surface gives the coordinate system in which the shading becomes simple. In flat coordinates the sheet bends only across its width, so the light it receives is close to a function of position across the sheet. The darkening can then be measured from *all* the bare paper in a column, including margins and gaps between letters, and divided out under the letters as well.

**The model**, per color channel, in logarithms:

    log L(u, y) = c + g0(u) + y·g1(u) + p(y)

| Term | What it is |
|---|---|
| g0 | The darkening across the sheet. Its control points are 12 px apart at the gutter edge, 30 px over the curved part, and 160 px over the flat part. |
| g1 | Lets that darkening grow toward the bottom of the page; on plate 9 the bottom is about 2% darker. |
| p | The gentle top-to-bottom falloff of the lights. |

- **Fitting:** robust, reweighted least squares on bare-paper pixels, which are found by color and by being as bright as the paper nearby.
- **Normalizing:** the field is normalized so the well-lit paper keeps its own color and exposure; only the unevenness is removed. Anchoring to a page corner instead tinted the whole page.

| Plate | Paper brightness across the page, 5–95% spread | Gutter-side quarter, as a share of the open page |
|---|---|---|
| 09 | 15.1% → 0.98% | 89.1% → 99.8% |
| 10 | 15.5% → 0.72% | 89.5% → 100.1% |
| 11 | 15.3% → 0.46% | 88.3% → 100.0% |
| 12 | 16.5% → 1.28% | 87.5% → 100.0% |
| 08 | 13.5% → 0.15% | 90.4% → 100.0% |

After correction, the paper beside the gutter has the same color as the open page (plate 9: BGR 195/218/224 against 196/218/224).

**What it does not touch:** the thin line of the glass platen's edge, about 40 px from the gutter. It's an object in the photograph, not shading, and it lies outside the frame.

In the editor, the shading panel:
- plots the fitted light across the page for each channel,
- has a **strength** control (1 = remove all of it), stored with the plate,
- refits with **Fit shading** (at half size, which is plenty for a smooth field),
- shows previews with or without the correction.

`render` re-applies the saved shading; `shade` measures it again.

## Pugin's figures as a measure of width (plate 8)

The frame proves the rules are straight, but straight lines carry no measure of length, so they can't show whether the width near the gutter has been fully restored. Plate 8's construction figures can. Row 2 is five squares drawn alike, and row 5 has three compass circles. In each family the leftmost sits near the gutter.

**How they enter the fit.** Each figure's four extreme points (left and right on its middle row, top and bottom on its middle column) are measured in the photograph and saved in the plate's file under `shapes`. In the fit they are traced back through the camera onto the sheet, and their width is measured along the paper. Each family shares one width-to-height proportion, solved for, so the figures need only agree with one another. That allows for Pugin's hand and for paper that shrank slightly more one way than the other.

**Tolerances.** Each family has its own tolerance:
- circles ±0.3 px (the two away from the gutter agree to 0.1%)
- squares ±2 px (the four away from the gutter vary by up to 1%)

Frame points are down-weighted robustly when they stray, for example where ink touches a rule. Figures always count in full.

**Calibration.** The lens is calibrated on plates 8, 9, 11 and 12: their frame rules plus plate 8's figures. The command first sweeps the focal length, then refines from the best point. Result: **f = 9,456 px, k1 = −0.0649**.

**Result on plate 8** (width ÷ height, measured on the images themselves):

| Figure | Photograph | Before (frames only) | After (with figures) | Same figures away from the gutter |
|---|---|---|---|---|
| Gutter square | 0.967 | 0.991 | **1.005** | 0.998–1.010 |
| Gutter circle | 0.970 | 0.990 | **1.000** | 1.002–1.003 |

The gutter square gained 4.8 px of width and the circle 5.0 px. The other six figures moved by 0.1% or less.

**What carries over to plates 9–12: almost nothing.** Taking the same 400 px band of photograph next to each frame's left rule through the old and new models:

| Plate | Change in width |
|---|---|
| 8 | +0.79% |
| 9 | +0.14% |
| 10 | +0.01% |
| 11 | −0.01% |
| 12 | −0.09% |

Mid-page control bands are unchanged. Diagnosis:
- **Not the lens.** Plate 8 refitted from its frame alone with the new lens still gives 0.994 for the gutter square.
- **Not smoothing.** Less smoothing of the profile doesn't help (0.997 at none, and the profile goes wild).
- **Not a fuller lens model.** An off-center principal point and a k2 term overfit and make it worse.

The figures fix plate 8 by reshaping *its own* depth profile into a sharper bend about 300–400 px from the gutter. The four frame rules can't resolve that bend. **So plates 9–12 likely keep a shortfall of about 1% in the band nearest the gutter**, roughly the first letter column: about 4 px across a 400 px letter. Fixing it would need width references on those plates themselves. One candidate: the stems of the textura letters on plates 11–12, drawn with one pen width.

## Files## Files

| Path | What | In git? |
|---|---|---|
| `reference/pugin-glossary/flatten/<plate>.json` | Everything for one plate: camera, surface knots, page and frame rectangles, the detected rule points, any figures (`shapes`), shading, and fit and render reports | Yes |
| `reference/pugin-glossary/flatten/_camera.json` | The shared lens calibration, with its focal-length sweep | Yes |
| `reference/pugin-glossary/flattened/<plate>.png` | The flattened page at full resolution (about 10 MB) | No (see Q18) |
| `reference/pugin-glossary/flattened/<plate>.preview.jpg` | A 1,200 px preview | Yes |
| `reference/pugin-glossary/flattened/<plate>.deshaded.png` | The flattened page with the gutter shading removed: the one to use for the letters | No (see Q18) |
| `reference/pugin-glossary/flattened/<plate>.deshaded.preview.jpg` | Its 1,200 px preview | Yes |
| `build/flatten-cache/` | Decoded photographs and editor previews | No |

### Plate file fields

- `camera`: `f`, `k1`, `k2`, `cx`, `cy` (the lens), and `rot_deg` [tilt x, tilt y, turn] (the pose). R = Rz·Ry·Rx.
- `surface`: `x_knots`, `z_knots`, and `anchors` (knot indices held at 0). z is positive away from the camera.
- `frame`, `page`: rectangles in flat coordinates (`u0`, `u1`, `y0`, `y1`). `page.auto` is false once someone has set it by hand, and `render` then keeps it.
- `features`: lines known to be straight on the printed page.
  - `dir` is `h` or `v`.
  - `pts` are photograph pixels.
  - `weight` 0 excludes a line from the fit.
  - New kinds of line, such as hand-traced ones, can be added with `source` other than `auto`; re-detection keeps them.
- `shading`: the light-field coefficients per channel (`coef.b/g/r`), knot positions, the normalization (`ref_log`), `strength`, and `check` (paper evenness before and after).
- `fit`, `render`: reports. `render.check` holds the straightness measured in the output.

## The editor

`serve` opens a browser editor for the same files.

- **The grid.** The 3D grid is drawn over the photograph, along with the detected rules, the fitted frame, and the page rectangle.
- **Reading the page.** Scroll to zoom and drag to pan. The readout gives the page coordinates and depth under the cursor.
- **Adjusting.**
  - Camera and pose: sliders.
  - Depth profile: drag its knots.
  - Page rectangle: type the numbers or drag its red edges on the photograph.
  - Rules: switch individual lines in or out of the fit.
- **Auto-fit** refits from the current values, with the shared lens held fixed unless "fit lens too" is checked.
- **Preview / Render full size.** Preview shows the flattened page at quarter size with straightness measured. Render full size writes the PNG.
- **Save** (⌘S) writes the plate's JSON. Git keeps the history.

## Next

- **Letters.** Separate the inks (red, blue, black) from the paper on the evened pages and cut out each letter for vectorizing.
- **The glass-edge line** could be painted out if it ever matters; it's outside the frames.
- **Plates beyond 9–12.** Most plates have a ruled frame, but in other colors. Detection is tuned for red rules; other colors need a small change to `redness()`. More plates would also tighten the lens calibration.
