# 2026-10-28 — The first Lombardic glyph: I, built from primitives

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh: "Build the I end to end from primitives (stem, bars, four curls), with nodes at extremes, and show it overlaid on Pugin's plate."
- **Nodes at extremes.** A new fitter (`tools/type/geom.py`) puts nodes where a type designer would:
  - at the curve's horizontal and vertical extremes, with flat or upright handles;
  - at true corners;
  - elsewhere only where a span can't be matched, and then at an inflection if there is one.

  It replaces the earlier fitter, which put nodes where the error was largest.
- **The curl as four nodes.** The 71-instance average is now drawn with four nodes (`primitives/curl.model.json`):
  - the stroke's outer edge, and the ball's back and crown, each an extreme;
  - the neck, a corner where the ball comes back to its stroke.

  It is within 0.10 px of the average. The angle at which a stroke leaves the neck turned out to belong to the glyph, not the curl: the average across the alphabet is 19°, but the I's bars leave flat. Fixing it at 19° made the flares 50% worse.
- **The construction kit** (`tools/type/construct.py`): glyph recipes (`fonts/pugin-lombardic/recipes/`) name a construction. The construction builds the left half of a symmetric glyph from primitives, and its measurements are fitted to Pugin's letter:
  - the fit runs both ways (the outline onto his edge, and his edge onto the outline);
  - a robust loss keeps his accidents from pulling the whole letter.

  Checks confirm no curve swells past its nodes, handles at extremes are exact, and corners occur only where intended.
- **The I** (`stem-bars-curls`): a straight stem, flares into two bars with concave edges, and the one curl placed four times, mirrored. There are 20 fitted measurements.
  - **Outline:** 22 segments, against 162 for a direct trace of the same edge.
  - **Fit:** Pugin's edge lies 0.9 px from it on average, 95% within 2.2 px, and 3.9 px at worst. His edge wobbles 0.29 px about itself.
  - **Where it differs:** his four curls vary by up to 10% in size, and he drew the flares about a pixel off-center. His stem is upright to within 0.04°.
- **Shapes tried along the way:**
  - A waisted stem as a single curve per side (1.12 px mean).
  - A straight stem between two flares (1.03 px).
  - The same with a per-glyph neck angle (0.87–0.90 px), which was kept.
  - Letting the curl's size float gave 1.02×, so the averaged curl is used at its own size.
- **A real font.** `build` writes the UFO source (`fonts/pugin-lombardic/source/PuginLombardicDraft-Regular.ufo`) and compiles it with ufo2ft to `build/PuginLombardicDraft-Regular.otf` (1.4 KB: .notdef, space, I).
  - Coordinates are rounded and mirrored on a whole unit, so the glyph stays exactly symmetric.
  - The outer contour runs counter-clockwise, as PostScript outlines require.
  - The font name is a placeholder (Q33). Side bearings are a provisional 50 units.
- **Proof page.** It now opens with the built I over Pugin's I on the flattened plate. Layers:
  - the outline;
  - nodes and handles (circles smooth, squares corners);
  - the compiled font rendered in place;
  - a shape difference.

  Below it: Pugin, the font, and the difference side by side; a specimen; the fitted measurements. The difference compares shapes (inside his 0.5 edge), not ink, so speckled ink inside the letter doesn't show as error.

## What changed
- **Created:**
  - `tools/type/geom.py`, `tools/type/construct.py`
  - `fonts/pugin-lombardic/recipes/I.json`
  - `fonts/pugin-lombardic/primitives/curl.model.json`, `curl.model.svg`
  - `fonts/pugin-lombardic/source/PuginLombardicDraft-Regular.ufo`
- **Updated:**
  - `tools/type/type.py`: new `build` command, the extremes fitter, proof sections
  - `fonts/pugin-lombardic/source.json`: font names and metrics
  - `fonts/pugin-lombardic/primitives/curl.json` and `curl.fitted.svg`: refitted with nodes at extremes
  - the family README, `fonts/README.md`, `docs/roadmap.md`, `.gitignore` (`fonts/*/build/`)

## Open threads
- **Family-wide values.** The I's stem is 79.7 px across its straight; the plate's median stem is 70.6 px. Stems, curls, and bar edges should settle to shared values once several letters are fitted together.
- **More primitives:** the trefoil, the cross's larger curl, G's hooked terminal, the crescent bowl, hairline joins.
- **Next letters:** those that reuse this construction or extend it (L, E, F, T), then the round letters, which need overshoot.
- **Spacing, features, and automated font checks** (fontbakery) once there are enough glyphs to space.
- Q31–Q34 still open.
