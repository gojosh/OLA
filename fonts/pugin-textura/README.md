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
| Plain letters | **All 24 letters on the plate** (a–z without j, u and w, with ſ) fitted, spaced, kerned and compiled into a draft font, with u, w and j below. All pass the outline checks. |
| Letters Pugin didn't draw | **u, w and j**, drafted in his idiom as proposals and built from the fitted measurements of n, v and i (decision 0008). |
| Still to build | The ampersand's plain form; the hairline exits at the feet; then the flourished alternates; then plate 10's capitals. |

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
| The nib's edge | 45° on average, from 31 edges on the heads and feet that rise to the right. Pugin's pen turns: "The top connecting spurs are at 45°, but the feet are nearly all at 50°" (Josh, 2026-10-29). The font holds the nib at 45° at the heads and 50° at the feet (below). |
| The nib's width | about 47 px (an upright stem is the nib's width times the cosine of its angle) |
| Hairlines | 8 px |

## The nib

`tools/type/nib.py` simulates the pen. The nib is a thin rectangle. A stroke is the ground it covers moving along a path: the path's Minkowski sum with the nib. The outline is exact. For each edge of the nib the path is cut wherever it runs parallel to that edge, and along each piece the edge sweeps a ribbon whose sides are the path's own curves, shifted to the edge's two ends. The ribbons, and the nib at each node of the path, are joined into one outline with skia-pathops, each stroke cleaned on its own and then joined to the others one at a time. (Joining every piece of every stroke in one pass can silently drop part of a letter: at a 50° nib it lost most of h's stem.) The outline is then cleaned: straight runs become single lines, every extreme gets a node, nodes closer than about a font unit are merged, and outlines run clockwise with their counters anticlockwise.

**The pen turns** as it goes down the letter, as Pugin's does: the nib is at 45° at the heads, on the x-height line and above, and at 50° at the feet, on the baseline and below, turned evenly between the two lines (`Pen`; `nib_angle` and `nib_angle_foot`, held in `source.json`). Josh first asked for 50° throughout ("we need to push the standard nib angle to 50 degrees. We're still too shallow"), then saw where Pugin's pen turns: "The top connecting spurs are at 45°, but the feet are nearly all at 50°" (2026-10-29). So the heads, and the hairlines joining n's and m's heads to the stem before, keep 45°, and every foot is cut at 50°, its spur along the same edge. A stroke that keeps nearly one angle is drawn exactly as before at its mean angle. A straight stem turning on its way down covers the hull of the nib at its two ends, so it narrows a little, from 36.5 px under the head to 34 px over the foot. A curve that turns further is cut into pieces that turn no more than a degree each. The nib's width and hairline stayed as they were. Against Pugin, the turning pen fits about as well as 45° throughout (a mean of 3.47 px from his edge over the letters without heavy flourishes, against 3.42) and better than 50° throughout (3.60, or 3.53 with the shared measurements refitted to suit). With the feet at 50°, the corners of q's and y's left feet no longer reached the stroke beside them, so their feet now run on to meet it, as d's and g's do. And e's hairline now closes its eye, as it was meant to.

**Concave tops.** At the upper left of c, d, e, g and s, where the primary stem meets the top stroke, Pugin's edge is concave (Josh: "a concave curve on the top left where the primary stem and top line intersect. We need to retain this. It's one of many fine features accomplished by subtle nib rotation", 2026-10-29). Measured on the plate, it leaves the stem's top corner nearly flat (4–24°, median 13°) and steepens until it meets the peak along the nib's own edge (39–52°), sagging 3–6 px below a straight line. That is the sweep of the nib's edge as the pen turns from flat to its working angle. The outline is trued to that curve (`concave_top`): from the stem's top corner, leaving at 13° (`top_leave`, held in `source.json`), to the top stroke's peak, arriving along the nib's edge, the gap below filled and the corner above trimmed. In c, e and s only the stem's top and the start of the top stroke were fitted again, so the far ends of their top strokes, and the e's eye, are as they were. o and q keep their straight edge, as Pugin's are straight there.

**Lighter strokes.** Some strokes are written with less pressure, so with a narrower nib: its width 80% of the full nib's, its hairline unchanged (`nib_light`, held in `source.json`; `textura_letters.light`, `nib.Stroke`). They are the c's top stroke, the e's top stroke (its arm) and the a's top bowl (Josh: "take the top stroke of the c, for example - it should be about 20% thinner. Same with the e and top bowl on the a", 2026-10-29). Each keeps its path, so both its edges move in. Against Pugin, the a's top bowl now lies on his edges (the a from 2.6 to 2.3 px). The c and e measure a little further from his (3.3 to 3.7, 4.2 to 4.4 px), but there his hanging hairline and ball under the stroke count as ink, which pulls the measure toward a heavier stroke.

**The minim**, the textura's basic stroke (`textura_letters.minim`): the pen comes down the nib's diagonal into the head, turns down the stem, and turns out into the foot. The nib leaves the diamond-pointed head and foot by itself; the turns leave the hollows under the head and over the foot. A minim that follows another in the same letter has an ordinary head, standing clear of the stem before it. The pen comes up to that head from the stem along its own edge, which leaves a hairline joining the two at the top, as Pugin's n and m do (Josh: "the connection between stems is created with the spurs at the top, not simply the angled part of the stems", 2026-10-29). Until then each following head had started inside the stem before it, 12 px longer than an ordinary head, so a thick wedge of the head joined the two; against Pugin's n and m the hairline brings the mean distance from his edge from 2.3 to 1.7 px and from 3.0 to 2.0 px. The hairline is part of the letter, not a spur, so `ss01` keeps it: without it the minims would come apart.

**Fitting.** Each letter's measurements are fitted to Pugin's letter: the outline onto his edge, and his letter's body edge onto the outline. A robust loss keeps the hairlines that join his strokes from pulling. As for the Lombardic, each letter is fitted alone, each shared measurement is set to the median of what the letters want alone, and each letter is fitted again with those held (`family.json`). With four letters the shared values are provisional. The nib's thickness isn't settled yet: no hairline is fitted until the flourishes are. A full build moves every letter a little: each letter's fit alone starts from the last family, so the medians drift, and a fit restarted where it stopped wanders where Pugin's letter gives it little to hold on to. So a correction to some letters is built with `--fit` naming just those letters, or a single measurement (`b:right.lead`), or `none` to rebuild every letter from its measurements as they stand. The family and the other letters stay put. `--fit family` refits the shared measurements alone, the letters keeping theirs (for a change to the pen); a shared value no letter Pugin drew measures, like `join`, carries over.

## The letters built so far

**The kit** (`tools/type/textura_letters.py`):
- **The minim** and its variants: a given head length, or none (a stem cut flat by the nib at the top); a head that starts a little back along its own diagonal (b's bowl); a head joined to the stem before it by a hairline (n, m); a foot that runs on to meet the stroke on its right (d's and g's bowls, `foot_to_meet`); a stroke that stops with the nib's cut instead of turning out into a foot; stems running up to the ascender line or down to the descender line.
- **Free strokes** of the same pen through named points and headings, for arms, bars, bowls and tails.
- **The forked ascender** (l's): a minim to the ascender line with a short spur up to the right. b, h and k use it too.
- **The broken bowl** (o's): a flat-topped stem on the left, and on the right a stroke whose long head starts inside the left one and which stops with the nib's cut, meeting the left stroke's foot. q and g use it too.
- **Edges where strokes meet** (`edge_below`, `edge_above`): see below.
- **The second line.** Pugin squeezed y and z onto a second line, at about 0.7 of the first line's height, written with the same pen. Their plain forms stand at the full x-height; only the comparison with his letters is squeezed (`fit_affine`).

**Strokes meet; they don't merge.** A letter is built from the strokes the pen made, each a smooth path, and where two strokes meet they meet at a point, so the union keeps a sharp corner there. Running two strokes together into one rounded path loses "the sharper aspects of the otherwise flowing penmanship" (Josh, on the a).

**Where two strokes meet in one edge.** At the bottom of b, o, v and w, a stroke's foot meets a stroke that stops with the nib's cut; at the top of o, q and g, a flat-topped stroke meets the head of the stroke on its right, and at the top of d's bowl, its left stroke's short head meets the bowl's top stroke. Pugin draws each of these joins as one straight edge. Our two cuts each lay at the nib's angle, but one was set off from the other, which left a step (Josh, 2026-10-29: "the b should align the angle of each stem seamlessly at the bottom", and the same for the top and bottom of o, the top of q, and the bottoms of v and w; then g's top, and "the top of the bowl of the d"). His edge is flatter than the nib's cut: measured on the plate, about 38° at the bottoms of b, o and v and the top of o, 33° at the top of d's bowl, and 28° at the top of q, against the nib's 45°. So a pen held at one angle can't cut it, and lining the two cuts up at 45° (tried first) left the right strokes' corners 15–19 px above his, and q's top-left corner nearly 30 px below his. Instead, each stroke is drawn as before, and the outline is trued to the straight edge between the two points the fit had already put where Pugin's are: the foot's point and the right stroke's corner, or the flat top's corner and the head's peak (`nib.true_to`). The notch is filled and the step trimmed. Nothing else in the letter moves.

Every letter's starting positions were measured from its reference (the ink runs across it at fixed heights), and the fit took it from there.

| Letter | Built from | Pugin's body edge from it (mean) |
|---|---|---|
| a | Three strokes, as Pugin's pen drew it (Josh: "This a would have been drawn with three strokes"): the stem, from the top of the letter, its upper part bowing slightly in (held at 6° off upright; about 2 px on the plate), then straight on down to its foot; the bottom bowl, from the waist down the left into a foot ending in a spur that reaches up toward the stem (held as committed: "It was correct before"); and the top bowl, one smooth curve from the stem's top, rising left to make the sloped top, over and down the left side, ending exactly where the bottom bowl begins. Each stroke flows; they meet at points, so the outline keeps sharp corners there ("where each of these three strokes intersect is precise"). The top bowl is a lighter stroke; where it leaves the stem, its sloped top runs straight on into the stem's right edge, so the stem's full-width corner doesn't stand proud of it | 2.3 px |
| b | l's ascender, and a bowl's second stroke stopping against the stem's foot. The two meet in one straight edge at the bottom. The bowl's head starts a little back along its own diagonal, inside the stem (7.7 px, the one measurement fitted for it), so the bowl closes against the stem at the top, meeting it where Pugin's does; before, the head stopped about 1.5 px short of the stem and the counter ran out past it (Josh: "close the b's counter at the top"). | 9.8 px (his looped top) |
| c | A stem whose head stroke carries on past it as one thick wedge across the top, as Pugin's does. That wedge is what tells c from r: drawn as a head with an arm, c read as r. The wedge is a lighter stroke. Stem and wedge meet in a concave curve at the upper left. | 3.6 px |
| d | The uncial d: a bowl's left stroke, and a stem whose top leans back over the bowl as a thick arm, stopped by the nib (his ends in a ball and runs on into a flourish). The bowl's left stroke and its top meet in a concave curve at the upper left. The bowl is wider than o's, so the left stroke's foot runs on (41 px against the family's 27) until the upper corner of its cut is half a hairline inside the stem: the two join at a point, as Pugin's do, and the bowl is closed (Josh, 2026-10-29). Its point stands about 10 px right of his, since his foot's cut is steeper than the nib's. | 4.1 px |
| e | A stem with a flat top, an arm leaving its top to the right (a lighter stroke), the two meeting in a concave curve at the upper left as in c, and a hairline closing the eye (his ends in a ball). Until 2026-10-29 it had a minim's head, which stood up and out to the left of Pugin's and left a V between it and the arm; his e's top is one sweep, as his c's is. | 3.7 px |
| f | As ſ, with a crossbar (his loops over at the top and runs on into a swash) | 31 px (his loop and swash) |
| g | o's two strokes, meeting in a concave curve at the upper left, the right one sweeping round under the letter; a small ear at the top. As in d, the left foot runs on (42 px) to meet the right stroke at a point, closing the bowl; its point stands about 6 px right of Pugin's. | 6.5 px |
| h | l's ascender, and a leg running down to turn out at the descender line (his ends in a hairline loop) | 5.6 px |
| i | A minim, and a hairline stroke over it. Pugin's i on plate 9 has none, but in a textura spaced like his the i can't otherwise be told from the minims beside it. Proposed, and kept by Josh ("Keep the i stroke and the short l spur", 2026-10-28). | 2.1 px |
| k | l's ascender, a small closed loop at the x-height, and a leg with its own head | 2.5 px |
| l | A minim to the ascender line, its top forked: the head stroke from the upper left and a short spur up to the right. On the plate the spur runs on as a thick arm into a hairline flourish; an arm reaching over the next letter is what marks a long s, so the plain l keeps only its start. Proposed, and kept by Josh. | 8.0 px (his arm) |
| m, n | Three and two minims, each following head an ordinary head, joined to the stem before it by a hairline | 2.1, 1.8 px |
| o | The broken bowl, its two strokes meeting in one straight edge at the upper left and at the lower right | 1.6 px |
| p | A stem running down to the descender line, and a bowl turning back in to the stem at the baseline (his bowl crosses the stem into a curl, and his descender runs into a long swash) | 27 px (his swash) |
| q | The broken bowl, meeting in one straight edge at the upper left, the right stroke running down to the descender line (his splays into a swash); the left foot runs on to meet it | 12 px (his swash) |
| r | A minim, and a small flag off the top right of its head, set apart by a notch, as Pugin's is (his hangs a hairline and a ball from it) | 5.2 px |
| s | An upper stroke with a flat top and an arm, meeting in a concave curve at the upper left (until 2026-10-29 the upper stroke had a minim's head, standing up and out to the left of Pugin's), a spine, a lower stroke stopped by the nib, and a foot under the left (his hangs a hairline and a ball from the arm and another under the spine) | 5.1 px |
| ſ | An arm at the top curving over to a point, the stem, a tail turning left at the descender line, and a spur on the left at the x-height (his tail is a swash) | 2.9 px |
| t | A stem cut to a point a little above the x-height, and a crossbar | 1.5 px |
| v | A minim, and a stroke with its own head stopping against the minim's foot, the two meeting in one straight edge | 2.2 px |
| x | A stem running down past the baseline and turning left, a flag at the top right, and a short stroke down to the right from the middle (his tail ends in a ball) | 4.7 px |
| y | v's strokes, the right one sweeping round to the left under the letter (his tail ends in a ball); the left foot runs on to meet it. Stands at the full x-height. | 4.3 px |
| z | A level bar at the top, a diagonal down to the left, and a lower stroke turning back along the baseline (his tail is a hairline swash). Stands at the full x-height. The weakest: its lower bowl is more angular than his. | 8.7 px |
| u *(proposal)* | n turned over: two minims, the first's foot running on to end against the second's stem, each with its own head. Built from n's measurements. | — |
| w *(proposal)* | u followed by v's second stroke, which stops with the nib's cut against the second minim's foot, the two meeting in one straight edge as v's do. Built from v's measurements. | — |
| j *(proposal)* | i running on past the baseline and turning left at the descender line, as ſ's tail does, with i's hairline stroke above. Built from i's measurements. | — |

Where the number is large, it is mostly the flourish: Pugin's heavy swashes and loops count as body, and the plain form leaves them out on purpose. All the letters pass the outline checks.

**Spurs.** Where a foot is free (nothing of the letter follows it), Pugin's pen carries on past the foot's tip in a short hairline up and to the right: the spur. Free feet are written with one: 10 px along the nib's own angle, so it is exactly the nib's hairline (`spur` in `source.json`; set from the plate, not fitted). Pugin's are mostly 5–12 px; l's runs to about 30, tapering. A first setting of 22 px at 41° was "too pronounced, compared to Pugin's work" (Josh, 2026-10-29). The a's lower bowl, which ends in a free foot, has one too. Feet that run into another stroke have none, as his don't: the inner feet of n and m, the left strokes of o, q, v and y, b's and d's bowls, w's first two. Fifteen letters have them. They are on by default; the stylistic set `ss01` ("Without spurs") swaps in each letter without its spur, in the same place and width, kerned as the letter is (Josh: "it would be cool to have a setting for the spur, where it can be turned on or off", 2026-10-29). The fit to Pugin is made without spurs.

**Spacing.** A textura is spaced like a fence: the white between two letters is the white between a letter's own minims. So the target white is set to put two i's one minim's pitch apart (the pitch of n's stems), and the side bearings are fitted to it over every pair (`tools/type/spacing.py`, as for the Lombardic). Pairs still more than 15 units off are kerned. Within the x-height band nothing may come closer than 10 units (heads and feet all but touch in a textura this tight); above it and below the baseline, 20 units, checked by true distance between the outlines, since an ascender's arm and the next letter's spur can be clear row by row and still almost meet on a slant. Pugin's plate is spaced the same way.

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
uv run tools/type/textura.py build pugin-textura --fit none     # or --fit b,o: refit only those
uv run tools/type/textura.py proof pugin-textura
```

The proof page is served with the Lombardic's by `uv run tools/type/type.py serve pugin-lombardic`, at `http://localhost:8766/pugin-textura/proof/`. It sets the letters built so far under Lombardic initials, shows Pugin's alphabet, and draws each letter over his with the nib's path, the outline and its nodes.
