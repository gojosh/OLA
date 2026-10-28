# 2026-10-28 — Lombardic: G and H corrected; A, N, S, U, V, X, Y, Z and the uncial T; a steadier fit

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **Josh's corrections** ("The G is missing it's top nub, the H has a more clearly separated two-lobe foot on the right leg"; verbatim in `docs/brief/2026-10-28-lombardic-corrections-2.md`):
  - **G:** a round nub on top of the beak. The bowl's top meets it at a notch; its right side runs down into the beak's outside.
  - **H** (and every two-lobe terminal):
    - The lobes are now spaced at 1.8 to 1.97 radii, close to two, so they read as two balls with a deep cusp between them. Before, the shared terminal had settled at 1.44, nearly merged.
    - Each letter sets the direction of its second lobe; the alphabet shares the size and spacing.
    - The pocket under the first lobe now dips before rising into its neck, as Pugin drew it.
- **Nine new glyphs** (`tools/type/letters.py`):
  - **A:** a stroke bowing out on the left; a crossbar and a square counter.
  - **N:** uncial, with an arch to the two-lobe terminal.
  - **S:** two bowls and a spine. The terminals are round balls beside the flag's foot and the left stroke's head, the same build as the inner curls of O and Q. The curl primitive is shaped for a thin bar and looped under S's thick flag.
  - **U:** uncial, with a hooked foot; the hook's inside dips and rises to a sharp tip, with a notch where it meets the bowl.
  - **V** and **X:** straight arms with caps.
  - **Y:** a plain stem.
  - **Z:** a rounded point and two slits.
  - **The uncial T:** a spiral ending in a trefoil.
- **New parts:**
  - `cap_top` and `cap_bottom`: a bar with a curl at each end, flaring into a stroke at any slant, for V and X.
  - `edge_point`: where a flare turns against its arm's slant, the edge runs upright for a moment, which is an extreme.
  - Curls at the foot and head of strokes rolling either way (`foot-right`, `head-left`).
- **Stylistic sets.** The uncial T is the first alternate. The font gets an `ss01` feature that replaces T with it (decision 0008: historical forms are opt-in). The proof page renders it through the feature. Recipes for alternates say `alternate_of` and `feature` instead of a code point.
- **A steadier fit.** With 24 letters (about 900 measurements), solving for all of them at once stalled after a dozen steps. Pugin's edges are rough at the pixel scale, and the solver's step control gave up. Letters new to the build were left far from his: A was 2.45 px from his edge, against 0.98 alone.
  - The build now settles the family in three steps:
    1. Each letter is fitted alone.
    2. Each shared measurement is set to the median of what the letters want alone.
    3. Each letter is refitted with the shared measurements held there.
  - Every solve is small. The steps run in parallel and are cached.
  - Every letter now lands close to its own best fit: U 0.76 px, N 0.83, X 1.10.
  - The largest costs of sharing are A (1.93 against 0.99 alone) and Z (2.06 against 1.92). Pugin drew their curls about 12–20% larger than the alphabet's.
- **Timings:** about 70 seconds to rebuild everything, under a minute after changing one letter.

## What changed
- **Created:**
  - `docs/brief/2026-10-28-lombardic-corrections-2.md`
  - recipes for A, N, S, T.2 (uncial T), U, V, X, Y, Z
  - `fonts/pugin-lombardic/build/refined.json` (generated, not in git)
- **Updated:**
  - `tools/type/construct.py`: curl orientations, `fixed` measurements, `refine_fit`, the one-letter fit's values, features in the UFO
  - `tools/type/letters.py`: G, H's terminal, the pocket, new letters and parts
  - `tools/type/type.py`: the three-step fit, stylistic sets, proof support for alternates, specimen words
  - recipes for G and H; the family README, `docs/roadmap.md`

## Open threads
- **Still to build:** M (both forms), W (both forms), the cross with its larger curls, the dot ornament.
- **Terminal lobe sizes**, including A's and Z's larger curls: to be settled family-wide, as Josh asked.
- **Kerning**, and Q34 (the default forms of M, T and W).
