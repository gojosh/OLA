# 2026-10-28 — Lombardic: corrections to F, K, O and Q; B, G, P and R

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **Josh's corrections:** "top right corner of the F and K should be rounded a bit, similar to the bottom right of the L. The O has a curl stem on the left attached to the lobe, and the Q has the same thing up top. We should preserve those. Also, the Q arm inner curve is not right. Try again on that. Then on to the next roadmap letters."
  - **F and K:** the top-right corner is now a small arc (a new `rounded_corner` part) that the top edge and the stroke below meet along its tangents.
  - **O's floor ball and Q's top ball are curls.** The stroke flows smoothly into the ball on one side, and the ball rolls on round to a sharp notch tucked under (O) or over (Q) it.
    - Pugin's curls roll further than the curl primitive does, so these two are drawn as round balls of the alphabet's curl's ball size, with the notch's angle fitted.
    - O is no longer fully symmetric. Its outline is still mirrored; its counter is drawn whole. Symmetric letters can now mix mirrored and whole contours.
  - **Q's flag:** its inside runs nearly flat from the notch to a low point, then rises steeply to the curl. The old construction allowed only a diagonal start, so it could never make that turn.
- **B, G, P, R**, all carrying the trefoil (`trefoil_at`):
  - **P:** the bowl spirals inward to end in a trefoil in the counter.
  - **R:** the bowl's lower stroke ends in a trefoil pointing at the stem, a hair short of touching it, so the bowl is open. A leg sweeps from the notch under the bowl to a curl at its foot.
  - **B:** two bowls with a trefoil at the waist pointing at the stem. Its gap joins the two counters into one.
  - **G (uncial):** a hooked beak falling to a round bulb. The lower right rises, arches over and spirals down to a trefoil pointing down. The counter opens between the bulb and the spiral.
  - Fitted alone, their trefoils run from 17.5 to 23 px in lobe radius. The family trefoil is now fitted across B, F, G, P and R.
- **Fixes along the way.**
  - **Arc snapping.** An arc whose end falls within about a pixel of an extreme now ends on the extreme, instead of leaving a sliver that collapses when rounded to font units (K's new corner).
  - **Approach directions.** Where an edge runs into a trefoil lobe or a notch, its approach direction is bounded so it can't swing out and back. Nodes whose role depends on another's position are placed relative to it (O's floor, Q's pocket, Q's top wall).
  - **Swell tolerance.** The outline check tolerates a curve poking past its node by under 0.2 px in plate pixels and 0.5 units in font units, where that is rounding rather than drawing.

- **First full build of all fifteen letters.**
  - It was run from scratch and took over 25 minutes.
  - Fourteen letters passed. G failed on two small points, fixed after: its beak's outer edge could approach the bulb from the right, so it swelled past its node; and rounding a short handle left a 2.3° kink where the beak meets the bulb.
  - The shared trefoil settled at a 20.9 px lobe radius across B, F, G, P and R.
- **Build speed**, at Josh's request ("What does the build process actually do, and why does it take so long?", then "Yes" to the fix).
  - **Where the time went:** it was nearly all in fitting. Every trial step rebuilds every letter and measures distances against thousands of points, and the derivatives are found by nudging measurements and redrawing. Every build started over from the hand-read starting values, and refitted every letter alone for the comparison table.
  - **Warm starts.** Every fit now starts from the last build's values: each recipe's `measured` and `family.json`'s shared values.
  - **Cached one-letter fits.** Each is keyed by a fingerprint of the letter's construction, the shared parts and kit, its reference and the curl. Only changed letters are refitted, in parallel across cores (`build/alone.json`).
  - **`--fresh`** starts everything over.
  - **The font-unit check** now allows a 3° kink where a smooth join's handle is only about ten units long; rounding to whole units can't keep such a short handle exactly in line.
  - **Timings, fifteen letters:**

    | Build | Time | Notes |
    |---|---|---|
    | From scratch | over 25 min | |
    | First warm build | 1 min 36 s | all fifteen one-letter fits run in parallel, 27 s; joint fit 52 s |
    | Rebuild with nothing changed | 47 s | one-letter fits from the cache; joint fit 30 s |

    The shared values match the scratch build to within 0.02 px. All fifteen letters pass the checks. Shared: stems 79.9 and 71.6 px; curl 0.941; trefoil lobe radius 20.9 px.

## What changed
- **Created:**
  - `fonts/pugin-lombardic/recipes/B.json`, `G.json`, `P.json`, `R.json`
- **Updated:**
  - `tools/type/construct.py`: arc snapping, `ends`, `curl_ball_r`, mixed mirrored contours, swell tolerance
  - `tools/type/letters.py`: F, K, O, Q; B, G, P, R; `rounded_corner`, `trefoil_at`
  - `tools/type/type.py`: check tolerance, specimen words, warm starts, the cached and parallel one-letter fits, `--fresh`
  - recipes for F, K, O, Q; the family README

## Open threads
- **Terminal lobe sizes** (the curl ball, the balls inside O and Q, the two-lobe, the trefoil, G's bulb) to be settled together, as Josh asked.
- **Kerning.**
- **Remaining letters:** A, M (two forms), N, S, T (uncial), U, V, W (two forms), X, Y, Z, the cross, the dot ornament.
