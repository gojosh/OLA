# Pugin Textura (working name)

A revival of the small alphabet on plate 9 of A. W. N. Pugin's *Glossary of Ecclesiastical Ornament* (1844), "Alphabets No. 1", the book's Plate X. Pugin dates it to "the latter part of the fifteenth century" (Glossary, *Inscriptions*; see [`reference/pugin-glossary`](../../reference/pugin-glossary/README.md#the-alphabet-plates-in-pugins-words)). It is a textura minuscule written with a broad nib, and on the plate every letter carries hairline flourishes: loops on the ascenders, swashes on the descenders.

How it is made follows decisions [0008](../../docs/decisions/0008-font-approach.md) and [0011](../../docs/decisions/0011-textura-capitals.md):
- **Rebuilt with a simulated broad nib**, fitted to Pugin's letters and checked against them, never traced.
- **Plain forms are the defaults.** Josh: "these will need to have plain versions, as well as these highly decorated versions" ([brief](../../docs/brief/2026-10-28-textura-start.md)). Pugin's flourished forms become alternates, built on the same strokes.
- **No capitals yet.** It is set with the Lombardic capitals as initials for now. Plate 10's fifteenth-century Gothic capitals, the capitals of its own period, come after the minuscule.

## Status (2026-10-28)

| Step | State |
|---|---|
| References | Done for all 25 glyphs on the plate: a–z without j, u and w, with long s (ſ) and an ampersand (`references/`). See below. |
| Measurements | Done (`measurements.json`). |
| The nib | Done (`tools/type/nib.py`). See below. |
| Plain letters | **All 24 letters on the plate** (a–z without j, u and w, with ſ) fitted, spaced, kerned and compiled into a draft font. All pass the outline checks. |
| Still to build | u, w and j (Pugin drew none) and the ampersand's plain form; the hairline exits at the feet; then the flourished alternates; then plate 10's capitals. |

## The references

The letters on the plate run into each other through their flourishes, so they can't be cut apart by boxes. They are separated by weight. An opening 13 px wide removes the hairlines (about 7 px) and leaves the nib's strokes (33 px and more). The larger pieces left seed the letters (one box per letter in `source.json`). Every other piece of ink, hairlines and swashes included, goes to the letter it is joined to by the shortest way along the ink. `references/<letter>.png` is a letter's ink coverage with all its flourishes; `references/<letter>.body.png` is what the opening left; `references/overview.jpg` shows which ink went to which letter.

## The hand

Measured from the references (`measurements.json`, plate pixels):

| | |
|---|---|
| x-height | 205 px, from the points of the minims' heads to the points of their feet |
| Ascenders | 320 px above the baseline (1.56 × the x-height) |
| Descenders | 105 px below it (0.52 × the x-height) |
| Upright stems | 33 px |
| The nib's edge | 45°, from 31 edges on the heads and feet that rise to the right |
| The nib's width | about 47 px (an upright stem is the nib's width times the cosine of its angle) |
| Hairlines | 8 px |

## The nib

`tools/type/nib.py` simulates the pen. The nib is a thin rectangle held at a fixed angle and never turned. A stroke is the ground it covers moving along a path: the path's Minkowski sum with the nib. The outline is exact. For each edge of the nib the path is cut wherever it runs parallel to that edge, and along each piece the edge sweeps a ribbon whose sides are the path's own curves, shifted to the edge's two ends. The ribbons, and the nib at each node of the path, are joined into one outline with skia-pathops. The outline is then cleaned: straight runs become single lines, every extreme gets a node, nodes closer than about a font unit are merged, and outlines run clockwise with their counters anticlockwise.

**The minim**, the textura's basic stroke (`textura_letters.minim`): the pen comes down the nib's diagonal into the head, turns down the stem, and turns out into the foot. The nib leaves the diamond-pointed head and foot by itself; the turns leave the hollows under the head and over the foot. A minim that follows another in the same letter starts its head against the stem before it, so n's and m's minims join at the top, as Pugin's do.

**Fitting.** Each letter's measurements are fitted to Pugin's letter: the outline onto his edge, and his letter's body edge onto the outline. A robust loss keeps the hairlines that join his strokes from pulling. As for the Lombardic, each letter is fitted alone, each shared measurement is set to the median of what the letters want alone, and each letter is fitted again with those held (`family.json`). With four letters the shared values are provisional. The nib's thickness isn't settled yet: no hairline is fitted until the flourishes are.

## The letters built so far

**The kit** (`tools/type/textura_letters.py`):
- **The minim** and its variants: a given head length, or none (a stem cut flat by the nib at the top); a stroke that stops with the nib's cut instead of turning out into a foot; stems running up to the ascender line or down to the descender line.
- **Free strokes** of the same pen through named points and headings, for arms, bars, bowls and tails.
- **The forked ascender** (l's): a minim to the ascender line with a short spur up to the right. b, h and k use it too.
- **The broken bowl** (o's): a flat-topped stem on the left, and on the right a stroke whose long head starts inside the left one and which stops with the nib's cut, in line with the left stroke's foot. q and g use it too.
- **The second line.** Pugin squeezed y and z onto a second line, at about 0.7 of the first line's height, written with the same pen. Their plain forms stand at the full x-height; only the comparison with his letters is squeezed (`fit_affine`).

Every letter's starting positions were measured from its reference (the ink runs across it at fixed heights), and the fit took it from there.

| Letter | Built from | Pugin's body edge from it (mean) |
|---|---|---|
| a | A stem whose long head starts well to the left; a short wall down the left under it; a lower bowl leaving the stem at the waist and turning out into a foot | 2.4 px |
| b | l's ascender, and a bowl's second stroke stopping against the stem's foot | 9.5 px (his looped top) |
| c | A stem whose head stroke carries on past it as one thick wedge across the top, as Pugin's does. That wedge is what tells c from r: drawn as a head with an arm, c read as r. | 3.4 px |
| d | The uncial d: a bowl's left stroke, and a stem whose top leans back over the bowl as a thick arm, stopped by the nib (his ends in a ball and runs on into a flourish) | 3.9 px |
| e | A minim with an arm, and a hairline closing the eye (his ends in a ball) | 4.5 px |
| f | As ſ, with a crossbar (his loops over at the top and runs on into a swash) | 32 px (his loop and swash) |
| g | o's two strokes, the right one sweeping round under the letter; a small ear at the top | 5.4 px |
| h | l's ascender, and a leg running down to turn out at the descender line (his ends in a hairline loop) | 5.5 px |
| i | A minim, and a hairline stroke over it. Pugin's i on plate 9 has none, but in a textura spaced like his the i can't otherwise be told from the minims beside it. Proposed, and kept by Josh ("Keep the i stroke and the short l spur", 2026-10-28). | 2.0 px |
| k | l's ascender, a small closed loop at the x-height, and a leg with its own head | 2.4 px |
| l | A minim to the ascender line, its top forked: the head stroke from the upper left and a short spur up to the right. On the plate the spur runs on as a thick arm into a hairline flourish; an arm reaching over the next letter is what marks a long s, so the plain l keeps only its start. Proposed, and kept by Josh. | 7.9 px (his arm) |
| m, n | Three and two minims, each head starting against the stem before it | 2.8, 2.2 px |
| o | The broken bowl | 1.5 px |
| p | A stem running down to the descender line, and a bowl turning back in to the stem at the baseline (his bowl crosses the stem into a curl, and his descender runs into a long swash) | 27 px (his swash) |
| q | The broken bowl, the right stroke running down to the descender line (his splays into a swash) | 12 px (his swash) |
| r | A minim, and a small flag off the top right of its head, set apart by a notch, as Pugin's is (his hangs a hairline and a ball from it) | 5.4 px |
| s | An upper stroke with a head and an arm, a spine, a lower stroke stopped by the nib, and a foot under the left (his hangs a hairline and a ball from the arm and another under the spine) | 5.5 px |
| ſ | An arm at the top curving over to a point, the stem, a tail turning left at the descender line, and a spur on the left at the x-height (his tail is a swash) | 2.4 px |
| t | A stem cut to a point a little above the x-height, and a crossbar | 1.8 px |
| v | A minim, and a stroke with its own head stopping against the minim's foot | 2.5 px |
| x | A stem running down past the baseline and turning left, a flag at the top right, and a short stroke down to the right from the middle (his tail ends in a ball) | 4.9 px |
| y | v's strokes, the right one sweeping round to the left under the letter (his tail ends in a ball). Stands at the full x-height. | 4.8 px |
| z | A level bar at the top, a diagonal down to the left, and a lower stroke turning back along the baseline (his tail is a hairline swash). Stands at the full x-height. The weakest: its lower bowl is more angular than his. | 9.4 px |

Where the number is large, it is mostly the flourish: Pugin's heavy swashes and loops count as body, and the plain form leaves them out on purpose. All the letters pass the outline checks.

**Spacing.** A textura is spaced like a fence: the white between two letters is the white between a letter's own minims. So the target white is set to put two i's one minim's pitch apart (the pitch of n's stems), and the side bearings are fitted to it over every pair (`tools/type/spacing.py`, as for the Lombardic). Pairs still more than 15 units off are kerned. Nothing may come closer than 10 units over the whole height, ascenders and descenders included. Pugin's plate is spaced the same way.

## The flourished forms (plan)

On the plate every letter is flourished. Each flourish will be built as further strokes on the plain letter's strokes: the l's spur runs on into its arm and the hairline loop; descenders run on into their swashes. So a flourished form and its plain form share their strokes, and a fix to one is a fix to both. How they are reached (a stylistic set, the `swsh` feature, or contextual alternates at the start and end of lines) is for Josh to decide when the first ones can be seen.

## Files

| Path | What |
|---|---|
| `source.json` | The plate, the zone of the lowercase rows, one box per letter, and the font's names, metrics and spacing settings |
| `references/` | Each letter's ink with its flourishes, its body, an overview, and `references.json` |
| `measurements.json` | The hand's measurements |
| `recipes/` | One file per built letter: its construction, its fitted measurements, and the fit's summary |
| `family.json` | The measurements every letter shares, and what each letter would take alone |
| `spacing.json` | Side bearings and kerning |
| `source/` | The font source, generated from the recipes |
| `build/`, `proof/` | The compiled font, a report per letter, and the proof page (generated; not in git) |

## Run

```bash
uv run tools/type/textura.py extract pugin-textura
uv run tools/type/textura.py measure pugin-textura
uv run tools/type/textura.py build pugin-textura
uv run tools/type/textura.py proof pugin-textura
```

The proof page is served with the Lombardic's by `uv run tools/type/type.py serve pugin-lombardic`, at `http://localhost:8766/pugin-textura/proof/`. It sets the letters built so far under Lombardic initials, shows Pugin's alphabet, and draws each letter over his with the nib's path, the outline and its nodes.
