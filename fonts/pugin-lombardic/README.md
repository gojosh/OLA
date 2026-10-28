# Pugin Lombardic (working name)

A revival of the Lombardic capitals on plate 9 of A. W. N. Pugin's *Glossary of Ecclesiastical Ornament* (1844), "Alphabets No. 1". It is the first of the Pugin fonts. How they are made is set out in decision [0008](../../docs/decisions/0008-font-approach.md): the plate is a reference, never a source; glyphs are rebuilt from clean construction and checked against it.

## What's on the plate

There are 30 glyphs (see `source.json`):
- the cross,
- the alphabet without J (as usual in medieval alphabets), with **U and V as separate letters**,
- **three pairs of alternates:**
  - M: uncial (rounded, closed with a hairline) and straight-sided
  - T: straight and uncial (rounded, with a curl in the counter)
  - W: two interlaced Vs and a rounded double U
- a dot ornament.

Letters alternate red and blue on the plate. Which form of M, T, and W is the default is undecided (Q34).

## Status (2026-10-28)

| Step | State |
|---|---|
| References | Done. Each glyph is cut from the flattened, evened plate and separated from the paper by ink. `references/<glyph>.png` is ink coverage (0–255, measured to a fraction of a pixel); `references/<glyph>.svg` is its outline. `references/references.json` gives positions on the plate, ink, and size. |
| Proportions | Done, in `measurements.json`. Height with curls is 427 px. Stems are 70.6 px (0.165 of the height). Bowls are 93.2 px (1.32 × stem). Hairlines are 32.0 px (0.45 × stem). |
| Primitive: the curl | Done (`primitives/curl.*`). Averaged from 71 instances, then drawn as four nodes (`curl.model.json`). See below. |
| Construction kit | Working: the parts (stem, flares, bars, curl, knob, trefoil, fitted curves) in `tools/type/construct.py`, one construction per letter in `tools/type/letters.py`, and a joint fit across letters. |
| Glyphs | **A–Z without J and W** (U and V separate; M not yet), with both Ts: 24 glyphs, built, spaced and compiled into a draft font. The uncial T is reached through the stylistic set `ss01`. See below. |
| Primitive: the trefoil | Drawn as an exact, regularized shape (below), sized from all five letters that carry it (B, F, G, P, R); the uncial T's joins when it is built. |
| Primitive: the two-lobe terminal | Drawn as an exact, regularized shape (below), sized from H and K. |
| Still to build | M (both forms), W (both forms), the cross (with its larger curls), the dot ornament |
| Spacing | First pass: area-based side bearings (below). No kerning yet. |
| More glyphs, kerning, features, automated font checks | Later |

### The curl terminal

The scroll terminal, a stroke end that rolls into a ball, is the alphabet's signature. The search found **71 curls in 22 glyphs**, evenly split among the four orientations. Each was turned to one orientation, aligned, normalized for ink density, and averaged.

The average is drawn as a type designer would draw it, with **four nodes**:
- the stroke's outer edge under the ball, the ball's back, and its crown, each at an extreme with a flat or upright handle;
- the **neck**, a corner where the ball comes back to its stroke. The ball's side arrives there upright.

It follows the average within 0.10 px (0.52 px at worst). Averaging blurs the notch at the neck, so the fit leaves out 3 px either side of it and puts the corner where the ball's side and the stroke's edge meet.

The angle at which a stroke leaves the neck belongs to the glyph, not the curl. The average across the alphabet is 19°; the I's bars leave flat.

- **Where the instances disagree:** mostly at the ink edges, where the lithograph's ink spread varies. The shape itself is consistent.
- **Not yet found:** the curls at the ends of the cross's arms, which are larger, and the hooked terminal of G. These need their own templates.

### The trefoil

Pugin's trefoils (on B, F, G, P, R and the uncial T) are drawn freehand and vary. The revival's is exact: three equal round lobes on the arms of a cross, the tip on the trefoil's axis and one lobe at each side, square to it. It is the same wherever it is placed. Its arcs are split at their extremes after placing, so the nodes stay at extremes whatever way it faces. Cusps between lobes, and the joins to the stroke, are corners. Its size is fitted across B, F, G, P and R together; their trefoils, fitted alone, run from 17.5 to 23 px in lobe radius.

### The two-lobe terminal

At the foot of H's shoulder and K's leg, the stroke sweeps right and ends in a curl with a second ball beyond it. Pugin draws it unevenly: on H the two balls are the same size but set well apart, and on K the second is a bump merged into the first. The revival's is exact: two equal round lobes, overlapping so the cusp between them is crisp, the same wherever it is placed. The stroke's outside meets the first lobe at a sharp neck; its underside leaves the second at a corner. Its size, spacing and direction are shared by every letter that uses it (`family.json`).

Josh has asked for a family-wide look at terminal lobe sizes (the curl's ball, the two-lobe and the trefoil), since Pugin's are inconsistent, once more letters are built ([brief](../../docs/brief/2026-10-28-terminal-lobe-sizes.md)). Until then each keeps its own fitted size.

### The letters built so far

Each letter is drawn by a construction in `tools/type/letters.py` from the kit's parts: the stem and its flares, bar edges, the curl, the knob, the trefoil, and fitted curves where a letter has a stroke of its own (T's and L's arms, E's bowl, F's counters). Recipes (`recipes/*.json`) name the construction and keep the fitted measurements.

| Letter | Built from |
|---|---|
| I | Straight stem flaring into two bars; four curls, mirrored. |
| T (straight) | The I's stem, bottom bar and curls. A bar arched up to the axis whose ends turn down into tapering arms; a round knob on each arm's outer top corner, and a curl at each arm's foot, turned to roll outward. Each arm's curl keeps at least Pugin's clear space (16.3 px) above the foot's curl, which keeps the letter legible small. |
| L | The I's top, symmetric about the stem, with a node where each top edge is steepest so it leaves its ball smoothly; the stem and its bottom-left curl. The base runs right into an arm that tapers as it rises and turns over into a curl, and comes to a rounded point at its foot. Pugin's curl on the arm looks two-lobed but is one curl drawn lumpily; the construction uses the alphabet's curl. |
| F | Stem with top-left and bottom-left curls; a square-ended top bar dropping as a stroke that closes the upper counter and ends in the trefoil; a sharp point where that stroke meets the middle bar in the lower counter; a foot running right into a bottom-right curl. |
| H (uncial) | A stem with the I's top-left and bottom curls; a long top bar, dipping a little over the stem, out to a top-right curl; a shoulder springing from the stem under the bar, arching over and down to a foot that sweeps right into the two-lobe terminal. A sliver of space between bar and shoulder comes to a point on the stem. |
| K | A stem with the I's top-left and bottom curls; a top bar out to a square corner, dropping as an arm to a crotch; a leg sweeping from there out, down and right into the two-lobe terminal. A pointed upper counter is closed against the stem; the lower counter comes to a point under the arm and opens at the bottom right. |
| C (uncial) | The E's bowl and right stroke without the middle bar; the counter is an oval, the stroke straight outside and swelling inside. |
| D | A stem (armed weight) with top-left and bottom-left curls and a round bowl. Pugin's bowl comes to a slight point on the right; it is rounded, as every bowl is. |
| O | An oval ring with a round ball hanging into the counter from the top, on the axis, and a curl rising from the floor: the floor runs smoothly up into its ball on the left, and the ball rolls on round to a sharp notch tucked under it. |
| Q | The O's bowl with a curl hanging from the top (smooth into the top wall on the left, a sharp notch on the right) and a ball on the floor. The base runs past the bowl to a rounded end, and a flag rises from it, parted from the bowl by a pointed notch: its inside runs nearly flat, then rises steeply to a curl at its head rolling out to the right. |
| B | A stem with top-left and bottom-left curls; two bowls, the lower the larger, with a notch between them outside; at the waist a trefoil points back at the stem, leaving a gap, so the counters are one. |
| G (uncial) | A round bowl whose top runs into a hooked beak, with a round nub on top, falling to a round bulb; the lower right rises, arches over and spirals down to a trefoil pointing down. The counter opens between the bulb and the spiral. |
| P | A stem with top-left and bottom curls, the bottom bar out to a bottom-right curl; the bowl spirals inward to end in a trefoil in the middle of the counter, which is open below the bowl. |
| R | A stem with top-left and bottom curls; the bowl's lower stroke ends in a trefoil pointing at the stem, a hair short of touching; a leg sweeps from the notch under the bowl to a curl at its foot. |
| A | A top bar with a curl at each end; a stem on the right with curls either side of its foot; a stroke on the left that bows out and sweeps in to a curl; a crossbar closing a squarish counter. |
| N (uncial) | The I's stem with a top-left curl and curls either side of its foot; an arch from the stem's top over and down to the two-lobe terminal. |
| S | Upper and lower bowls joined by a spine; a flag at the top right with a rounded head and a round ball at its foot, and the same turned over at the bottom left. |
| T (uncial) | A top bar with a curl at each end; a stroke from under it sweeping left into a round bowl that curls over at the top into a spiral ending in a trefoil. Reached through `ss01`. |
| U (uncial) | A round bowl meeting a top bar at a notch; a stem on the right flicking out at its foot into a pointed hook, parted from the bowl by a notch. |
| V | Two straight arms meeting at a point, the left thick and the right thin, each headed by a bar with a curl at both ends. |
| X | A thick stroke and a thin one crossing, each of the four arms ending in a bar with a curl at both ends. |
| Y | A stem (plain weight) with top-left and bottom-left curls; a top bar to a top-right curl; a right side curving down and round into the foot. |
| Z | A top bar with a curl at each end; a thick diagonal down to a rounded point; a bottom bar springing from a slit beside it, arching up and running right to a curl. |
| E (uncial) | A round bowl closed by a right stroke with top-right and bottom-right curls, notches where the bowl meets the stroke, and a middle bar. Two counters. |

**Fitted together.** The letters share two stem weights (decision 0009), one curl size, one ball size, one trefoil and one two-lobe terminal; everything else is per letter. The build settles them in three steps:
1. Each letter is fitted alone, with its own stem, curl and terminals.
2. Each shared measurement is set to the median of what the letters that use it want alone: where Pugin's letters agree.
3. Each letter is fitted again with the shared measurements held there.

(Until 2026-10-28 the build solved for every letter at once; with 24 letters, about 900 measurements, that solve stalled.) The values, and what each letter wants alone, are in `family.json`:

| | stem width (px) | curl size | Pugin's edge from it, alone (mean px) | sharing |
|---|---|---|---|---|
| A | 75.5 (armed) | 1.13 | 0.99 | 1.93 |
| B | 72.7 (armed) | 0.98 | 1.01 | 1.14 |
| C | — | 0.90 | 0.69 | 0.70 |
| D | 67.4 (armed) | 0.95 | 0.75 | 1.03 |
| E | — | 0.93 | 0.77 | 0.77 |
| F | 70.7 (armed) | 0.93 | 1.23 | 1.48 |
| G | — | — | 0.89 | 0.90 |
| H | 72.8 (armed) | 0.84 | 0.95 | 1.12 |
| I | 79.6 (plain) | 1.01 | 0.89 | 1.08 |
| K | 72.0 (armed) | 0.89 | 1.05 | 1.15 |
| L | 80.1 (plain) | 1.04 | 1.50 | 1.61 |
| N | 69.5 (armed) | 0.88 | 0.61 | 0.83 |
| O | — | 1.02 | 0.82 | 0.87 |
| P | 71.0 (armed) | 0.93 | 1.07 | 1.10 |
| Q | — | 1.02 | 1.03 | 1.16 |
| R | 71.0 (armed) | 0.91 | 0.82 | 1.04 |
| S | — | 0.95 | 0.96 | 0.99 |
| T | 74.6 (armed) | 0.87 | 1.89 | 1.98 |
| T (uncial) | — | 0.97 | 1.51 | 1.63 |
| U | 71.9 (armed) | 1.01 | 0.72 | 0.76 |
| V | — | 0.85 | 0.93 | 1.13 |
| X | — | 0.91 | 1.07 | 1.10 |
| Y | 80.5 (plain) | 1.02 | 1.31 | 1.38 |
| Z | — | 1.11 | 1.92 | 2.06 |
| **Shared** | **80.1 plain, 71.9 armed** | **0.946** | | |

Pugin's stems fall into two groups: about 80 px in I and L, the letters that are mostly stem, and 67–75 px in the letters that carry arms, a shoulder, a bowl or a wide bar. That looks like optical compensation, a lighter stem where the letter has more black elsewhere, and the family keeps it as two stem weights (decision 0009).

His curls run from 0.84 (H) to 1.05 (L) of the averaged curl. His trefoils, fitted alone, run from 17.5 to 23.1 px in lobe radius (shared: 20.9). The ball hanging in O and the ball on Q's floor share one size (27.3 px). His two-lobe terminals differ in kind as well as size: on H the lobes are as far apart as they can be while still overlapping, on K they are merged, and they point in different directions (26° and 70°). The shared terminal sits between. This is the inconsistency Josh has asked to settle across all terminals later.

**Corrections from Josh** ([brief](../../docs/brief/2026-10-28-lombardic-corrections.md)), now in the constructions:
- L's top edges seemed not to meet the stems tangentially. The fit had left a stub of a handle where each edge leaves its ball, which reads as a kink, and had fitted the two sides differently. The top is now symmetric, each edge has a node where it is steepest, and no handle is shorter than a fifth of its reach.
- L's foot comes to a rounded point (an 8 px arc), not a sharp one.
- F's lower counter has a sharp point at its top right, where the stroke meets the middle bar.
- T's arm curls keep at least Pugin's clear space above the foot curls.
- F's and K's top-right corners are rounded a little, like the foot of L's arm.
- O's floor ball and Q's top ball are curls, as Pugin drew them: the stroke flows smoothly into the ball on one side and the ball rolls on to a sharp notch on the other. They take the alphabet's curl's ball size. (They had been built as loose balls, and O's centred.)
- Q's flag: its inside runs nearly flat from the notch to a low point, then rises steeply to the curl. (It had been a single diagonal.)

**Outlines.** Every node is at an extreme, every handle there is flat or upright, and corners occur only where intended (necks, notches, the arch's point, trefoil cusps). The build checks all of this, in plate pixels and again in whole font units; there, a smooth join on a slant may kink by up to 2° where a short handle is rounded. The outlines have 16–39 segments; direct traces of the same edges need 160–250.

**In the font.** Cap height 700 units equals the plate's median letter height (1.639 units per plate pixel). The baseline is the bottom curls' outer edge. The straight T has the T key until Q34 is answered; the uncial T replaces it under the stylistic set `ss01`.

**Spacing** (first pass, `spacing` in `source.json`; the results are in `spacing.json`). Side bearings are set by area, after the method of HT Letterspacer:
- Along each side of a letter, on every line from the baseline to the cap height, the build measures the white between the letter's outermost point and its edge on that line, counting no deeper than 120 units.
- The side bearing is 130 units less that mean depth. A flat side gets the full 130; a side its curls or bowl stand out from gets less. So each letter carries about the same white beside it.
- No side bearing goes below 35 units, so curls never crowd. None goes above 75 units: T's white is inside the letter, under its arms, where the profile can't see it.
- Symmetric letters keep equal side bearings. The word space is 250 units.

There is no kerning yet. Pairs where the profiles don't tell the whole story (T and L next to round letters, for example) will want it. `uv run tools/type/type.py space pugin-lombardic` respaces and rewrites the font without fitting again.

## Files

| Path | What |
|---|---|
| `source.json` | The plate, the glyph names row by row, the alternate forms, primitive templates, and the font's names and metrics |
| `references/` | One coverage image and outline per glyph, plus `references.json` |
| `measurements.json` | Heights and stroke widths per glyph, with the medians |
| `primitives/` | For each primitive: the template, every instance aligned (`.instances.png`), the consensus, the spread, a free fit of the consensus (`.fitted.svg`), the clean model (`.model.json`, `.model.svg`), and a report (`.json`) |
| `recipes/` | One file per glyph: its construction, the primitives it uses, its measurements fitted to the plate, the fit's summary, and any recorded corrections |
| `family.json` | The measurements every letter shares (stem, curl, trefoil), what each letter would take alone, and the fit's cost of sharing |
| `source/` | The font source, `PuginLombardicDraft-Regular.ufo`. It is generated from the recipes; change recipes, not the UFO. |
| `build/` | The compiled font and a report per glyph (generated; not in git) |
| `proof/index.html` | The proof page (generated; not in git) |

## Run

```bash
uv run tools/type/type.py extract pugin-lombardic
uv run tools/type/type.py measure pugin-lombardic
uv run tools/type/type.py curls pugin-lombardic
uv run tools/type/type.py build pugin-lombardic           # add --fresh to start every fit from scratch
uv run tools/type/type.py proof pugin-lombardic
```

`build` does these steps:
- fits the curl's model;
- fits each letter alone (for the comparison in `family.json`), then all of them together;
- checks the outlines;
- spaces the letters, writes the UFO, and compiles `build/PuginLombardicDraft-Regular.otf`.

How long it takes:
- **Each fit starts where the last build finished** (each recipe's `measured` values and `family.json`), so letters that haven't changed settle almost at once.
- **The fits are cached and parallel.** Each letter's fit alone is keyed by a fingerprint of its construction, the shared parts, the kit, its reference and the curl; its refit is keyed by that and the shared values it uses. Only what changed is refitted, in parallel. A rebuild after changing one letter takes under a minute; after changing everything, about 70 seconds.
- **`--fresh` starts from scratch**, from the constructions' own starting values, as the first build of a letter does. That takes twenty minutes or more with fifteen letters.

`space` does only the last three steps. The proof page is self-contained and opens with the built glyphs over Pugin's letters, with layers to show the outline, its nodes and handles, the compiled font in place, and the difference. To view it in the app, start the `font-proofs` server (in `.claude/launch.json`) and open `http://localhost:8766/pugin-lombardic/proof/`.

Extraction needs the flattened plate, `reference/pugin-glossary/flattened/09-alphabets-no-1.deshaded.png`, which is not in git. Make it with `uv run tools/flatten/flatten.py render 09`.
