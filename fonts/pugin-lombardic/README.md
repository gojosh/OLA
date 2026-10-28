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
| Glyphs | **C, D, E, F, H, I, K, L, O, Q, T** (the straight T) built, spaced and compiled into a draft font. See below. |
| Primitive: the trefoil | Drawn as an exact, regularized shape (below). Sized from F so far; the other trefoils (B, G, P, R, uncial T) join when their letters are built. |
| Primitive: the two-lobe terminal | Drawn as an exact, regularized shape (below), sized from H and K. |
| Other primitives (the cross's larger curl, G's hook) | Next, with their letters |
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

Pugin's trefoils (on B, F, G, P, R and the uncial T) are drawn freehand and vary. The revival's is exact: three equal round lobes on the arms of a cross, the tip on the trefoil's axis and one lobe at each side, square to it. It is the same wherever it is placed. Its arcs are split at their extremes after placing, so the nodes stay at extremes whatever way it faces. Cusps between lobes, and the joins to the stroke, are corners. Its size comes from F so far (lobe radius 17.5 px, 22.4 px from the centre).

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
| O | A symmetric oval ring with a ball hanging into the counter from the top and one rising from the floor. Pugin's lower ball sits off to the left; the construction centres it. |
| Q | The O's bowl with a top ball and a floor ball. The base runs past the bowl to a rounded end, and a flag rises from it, parted from the bowl by a pointed notch, to a curl at its head rolling out to the right. |
| E (uncial) | A round bowl closed by a right stroke with top-right and bottom-right curls, notches where the bowl meets the stroke, and a middle bar. Two counters. |

**Fitted together.** All eleven letters are fitted to Pugin's in one solve. They share two stem weights (decision 0009), one curl size, one ball size, one trefoil and one two-lobe terminal; everything else is per letter. Each is also fitted alone, to show how far his letters disagree (`family.json`):

| | stem width (px) | curl size | Pugin's edge from it, alone (mean px) | sharing |
|---|---|---|---|---|
| C | — | 0.90 | 0.69 | 0.75 |
| D | 67.4 (armed) | 0.95 | 0.73 | 1.00 |
| E | — | 0.94 | 0.89 | 0.82 |
| F | 70.7 (armed) | 0.93 | 1.27 | 1.38 |
| H | 73.2 (armed) | 0.84 | 1.05 | 1.49 |
| I | 79.6 (plain) | 1.01 | 0.89 | 1.11 |
| K | 72.1 (armed) | 0.89 | 1.07 | 1.21 |
| L | 80.2 (plain) | 1.05 | 1.54 | 1.65 |
| O | — | — | 1.64 | 1.69 |
| Q | — | 1.06 | 1.23 | 1.35 |
| T | 74.6 (armed) | 0.86 | 1.90 | 2.03 |
| **Shared** | **79.9 plain, 71.2 armed** | **0.943** | | |

Pugin's stems fall into two groups: about 80 px in I and L, the letters that are mostly stem, and 67–75 px in the letters that carry arms, a shoulder, a bowl or a wide bar. That looks like optical compensation, a lighter stem where the letter has more black elsewhere, and the family keeps it as two stem weights (decision 0009).

His curls run from 0.84 (H) to 1.06 (Q) of the averaged curl, and the balls inside O and Q from 23 to 27 px in radius (shared: 25.4). His two-lobe terminals differ in kind as well as size: on H the lobes are as far apart as they can be while still overlapping, on K they are merged, and they point in different directions (26° and 70°). The shared terminal sits between. This is the inconsistency Josh has asked to settle across all terminals later.

**Corrections from Josh** ([brief](../../docs/brief/2026-10-28-lombardic-corrections.md)), now in the constructions:
- L's top edges seemed not to meet the stems tangentially. The fit had left a stub of a handle where each edge leaves its ball, which reads as a kink, and had fitted the two sides differently. The top is now symmetric, each edge has a node where it is steepest, and no handle is shorter than a fifth of its reach.
- L's foot comes to a rounded point (an 8 px arc), not a sharp one.
- F's lower counter has a sharp point at its top right, where the stroke meets the middle bar.
- T's arm curls keep at least Pugin's clear space above the foot curls.

**Outlines.** Every node is at an extreme, every handle there is flat or upright, and corners occur only where intended (necks, notches, the arch's point, trefoil cusps). The build checks all of this, in plate pixels and again in whole font units; there, a smooth join on a slant may kink by up to 2° where a short handle is rounded. The outlines have 16–39 segments; direct traces of the same edges need 160–250.

**In the font.** Cap height 700 units equals the plate's median letter height (1.639 units per plate pixel). The baseline is the bottom curls' outer edge. The straight T has the T key until Q34 is answered.

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
uv run tools/type/type.py build pugin-lombardic
uv run tools/type/type.py proof pugin-lombardic
```

`build` (about fifteen minutes with eleven letters) fits the curl's model, fits each letter alone and then all of them together, checks the outlines, spaces the letters, writes the UFO, and compiles `build/PuginLombardicDraft-Regular.otf`. `space` does only the last three steps. The proof page is self-contained and opens with the built glyphs over Pugin's letters, with layers to show the outline, its nodes and handles, the compiled font in place, and the difference. To view it in the app, start the `font-proofs` server (in `.claude/launch.json`) and open `http://localhost:8766/pugin-lombardic/proof/`.

Extraction needs the flattened plate, `reference/pugin-glossary/flattened/09-alphabets-no-1.deshaded.png`, which is not in git. Make it with `uv run tools/flatten/flatten.py render 09`.
