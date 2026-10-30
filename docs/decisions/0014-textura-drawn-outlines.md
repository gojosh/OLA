# 0014 — The textura's s, g, r, p, f, t, archaic x and z are Josh's own outlines, drawn in a drawing program over Pugin's

- **Status:** accepted
- **Date:** 2026-10-29
- **Decided by:** Josh Goforth

## Context
The s was modelled as one stroke of a turning, pressing pen, fitted to Pugin's letter and to Josh's painting of its main stroke, then given a pen editor for Josh to draw it point by point (decision 0013). Josh: "Ok - that ended up not being useful for the s. I drew it myself, and dropped it as an SVG in the references folder." ([brief](../brief/2026-10-29-textura-s-outline.md))

## Decision
Josh: "I drew it myself, and dropped it as an SVG in the references folder."

- **The s is his outline.** `fonts/pugin-textura/references/hand-drawn-s.svg`, as he drew it: the main stroke, and each fine stem with its pip, three closed paths.
- **Placed on the plate** by the scale and offset that overlap it best with Pugin's ink: one unit to the plate's pixel (1.0017), its corner at plate (2350.6, 3321.4), 80% overlap. Kept beside it, `hand-drawn-s.json`.
- **Built as it stands.** Wherever such a drawing exists (`references/hand-drawn-<g>.svg` with its `.json`), the build, the fit and the editors draw the letter from it (`textura_letters.OUTLINES`), ahead of a pen editor's drawing (decision 0013) or the construction. Its paths are filled and joined, and the outline is tidied as every other is (a node at each extreme, near nodes merged), which keeps it within 0.35 px of his curves, less than a font unit. Nothing of it is fitted. It is spaced and kerned as every letter is.

## Stems and pips, on or off
Josh: "And you have the stems able to enabled and disabled (however this type of customization works with opentype)?" The s's fine stems and pips (the drawing's two smaller paths) are on by default; the stylistic set `ss02`, "Without stems and pips", swaps in `s.nopips`, the drawing's main stroke alone, in the same place and width and kerned as the s is, as `ss01` does for the spurs.

## The y, drawn the same way
Josh: "Good. I just added hand-drawn-y." He traced it over Pugin's y, which stands on the plate's second line, shorter than the first line's letters (its body about 72% of their x-height). Its stems are as wide as theirs (36–37 px against 35–36): Pugin drew it with the same pen, shorter.

- Stretched upright to full height (Josh's first choice: "Stretch it all vertically"), its heads and diagonals were drawn out with it. Josh: "Vertical stretch didn't work - maybe scale up?" Scaled up evenly, its stems would be half again as heavy as the rest. Lengthening only the straight middle of its stems, with or without its tail, kept its weight. Shown all four: "hmm - I think it's none of those actually. What if we use it actual size that pugin provides, and align the top with the rest of the characters?"
- **So the y is at its own size**, its top lifted level with the other letters' heads. Josh, of his traced y placed so: "Yeah, that's not quite it either - I just saved a version I modified - try that one, same way - top aligned." His modified y (`hand-drawn-y-2.svg`, 24 units taller) is placed the same way, in the first's units (0.9945 to the plate's pixel), its top at the heads (`hand-drawn-y-2.json`). Its tail turns about 30 px below the baseline. The first drawing is kept beside it, unused (the build reads a drawing only with a placement beside it). `on_plate` moves it back onto Pugin's y for the proof card.
- **And it is an alternate.** Josh: "Ok - good enough for now - lets add this as an alternate to the y that you made." ([brief](../brief/2026-10-29-textura-y.md)) The y is again the construction: v's two strokes, the right running on into a tail, fitted to Pugin's y (4.3 px), exactly as it was before the drawing. Josh's is `y.alt`, reached through the stylistic set `ss03`, "Alternate y". A placement says so (`"glyph": "y.alt"` and an `alternate`: the set and its name, in `hand-drawn-y-2.json`), and the build draws the glyph from the drawing as it stands, beside its letter rather than for it (`textura_letters.ALTERNATES`). It is a different shape, not the y less a part as the `ss01` and `ss02` alternates are, so it is spaced and kerned in its own right: its side bearings are fitted against the letters, which keep theirs (`spacing.fit_more`), and it has its own kerning group. Nothing else moved.

## The g, drawn over the built one
Josh: "can you export g as an svg, so I can improve it?" Given the built g over Pugin's, one unit to the plate's pixel (`references/export-g.svg`), he drew his own: "Ok - I dropped in hand-drawn-g" ([brief](../brief/2026-10-29-textura-g.md)).

- **Two shapes, as Pugin's two strokes:** the left stroke with the arm and ear, and the right stroke with the tail. They don't touch: at the top of the right stroke and at the left stroke's foot they stand 6 and 8.5 px apart, where Pugin's ink also leaves a hairline of white.
- **Placed** at one unit to the pixel, where it overlaps Pugin's ink best: 92%, against 65% for the built g (`hand-drawn-g.json`). Its box is the box of his ink.
- **It is the g**, as the s's drawing is the s; the construction stays in the code, unused while the drawing exists. It measures 1.25 px from Pugin's g, 95% within 3.5 px, where the construction measured 6.5 px, 95% within 21.

## The r, drawn over the built one
Josh: "export p and r for me to manually improve". Given the built r over Pugin's (`references/export-r.svg`), he drew his own, and then: "Yes, place the r" ([brief](../brief/2026-10-29-textura-r.md)). The p's export waited on a repair to its bowl ([brief](../brief/2026-10-29-textura-p-bowl.md)).

- **One shape:** the top spur leading into the head, the stem, the foot with its spur, and the flag with a ball curling under it, as Pugin hangs a hairline and a ball from his flag.
- **Placed** at one unit to the pixel, with its top left on the built r's (`hand-drawn-r.json`), so its head stands on the other letters' heads and its foot on their feet, to a tenth of a pixel. He drew it over the built r at its height. Placed where it overlaps Pugin's ink best, it would stand 1.6 px lower (80% overlap against 79%).
- **It is the r**, as the g's drawing is the g. It measures 2.3 px from Pugin's r, 95% within 6.5 px, where the construction measured 5.2 px.
- **Its spurs are part of the drawing.** So `ss01` leaves the r as it is (there is no `r.nospur`), and the r is spaced with its top spur counted rather than set into the white before it: the pairs before r no longer need opening for the spur's clearance (72 such pairs → 58). Its ball reaches 25 px further right than the built r's flag, so its advance grew from 180 to 226 units; in words the ball sits in the white under the flag.

## The p, drawn over the repaired one
Josh: "Ok - hand-drawn p is in..." ([brief](../brief/2026-10-29-textura-p-drawn.md)), drawn over `export-p.svg` after its bowl was repaired ([brief](../brief/2026-10-29-textura-p-bowl.md)).

- **Pugin's flourishes, after all.** A curl off the head and the bowl's foot sweeping across the stem into a curl, which the plain p had left out at Josh's word; the bowl's head joined by the hairline; the split bottom as it was built.
- **Placed** at one unit to the pixel where the parts he kept stand where they did: the head's peak, the split bottom's lowest point and its two tips all give the same offset, to a thousandth of a pixel (`hand-drawn-p.json`).
- **Holes.** It is the first drawing with a hole. Its four paths are filled as his drawing program fills them, even-odd: a path lying inside another (by most of its points) is a hole cut from it, here the bowl's counter (`textura_letters.drawn`, `nib.Shape`'s `holes`). The two curls only touch the stem (0.6 px² of overlap, and none), so they are shapes of their own, joined to it. The s, g and r, with no holes, are built exactly as before.
- **It is the p.** It measures 20.9 px from Pugin's p, most of that his swash (the construction, 23.5). Its split no longer moves with the split's settings, so the panel for them (decision 0012) leaves it out.
- **The white before it.** The curls take space on its left: the p's advance grew from 308 to 331 units, and the pairs before it opened ("ap" 20 → 60, "ip" 20 → 55, "gp" 35 → 80). In words the white before p is wider than the rest of the rhythm. Asked whether to space the p without its curls, letting them tuck into the white before it, Josh: "Leave it as is" (Q41).

## The f, drawn over the built one
Josh: "Export the f a t, so I can fix them up as well." Then, of the f: "t is ready", "sorry - f, not t" ([brief](../brief/2026-10-29-textura-f.md)).

- **What he changed.** He kept the stem below the crossbar and the tail. The top now folds over and comes down on the right in a long arm, with a narrow slot open below it, nearer the way Pugin's f turns over before its loop. The crossbar is lower and shorter on the left. One shape.
- **Placed** at one unit to the pixel, where the tail's end stands where it did (its lowest and leftmost points give the offset to a thousandth of a pixel; `hand-drawn-f.json`). The stem's edges below the crossbar then fall on the built stem's to a pixel.
- **It is the f.** It measures 35.5 px from Pugin's f (the construction, 31.3). Neither has his loop or swash, which is most of the distance.
- **Spacing.** The construction's arm reached far out over the next letter, so the pairs after f were opened wide ("fb", "fh", "fk", "fl" 125 units). Josh's arm comes down within the letter, so they close up: "fb", "fh", "fk", "fl" 40, "fi" 70 → 45, "ft" 70 → 30. f's right side bearing went from -122 to -44 units.
  - The closest any letter after f now comes is 10 units ("fi", "ff").
  - Through the joint fit, the other letters' side bearings moved by up to 3 units, and 120 kerning pairs changed in all.

## The t, drawn over the built one
Josh: "t is ready" ([brief](../brief/2026-10-29-textura-t.md)), drawn over `export-t.svg`.

- **What he changed.** He kept the stem and the foot with its spur. The crossbar now ends on the right in a small curled flag, as Pugin's does, and on the left in a short point. The top has a small notch on its left. One shape.
- **Placed** at one unit to the pixel, where the foot stands where it did: the foot's point and the end of its spur give the offset to a thousandth of a pixel (`hand-drawn-t.json`). The stem's edges then fall on the built stem's row by row.
- **It is the t.** It measures 1.14 px from Pugin's t (the construction, 1.51), and overlaps his ink 93% (89%).
- **Spurs.** Its foot's spur is part of the drawing, so `ss01` leaves it as it is, as the r.
- **Spacing.** t's side bearings moved by up to 4 units and the others' by a unit at most; 42 kerning pairs changed, most by 5 units. The crossbar's new left point meets the c's top and the r's flag, so the clearance check opened "ct" (40 → 60 units) and "rt" (30 → 55).

## The archaic x, drawn over the built one
Josh: "My hand-drawn x is ready for import" ([brief](../brief/2026-10-30-textura-x-default.md)), drawn over `export-x.svg`. It is Pugin's x, the archaic form, which is now `x.archaic` under `ss04`; the x is a modern one (decision 0015).

- **What he changed.** He kept the head and the upper stem. The flag curls down into a ball, the stroke down to the right from the middle ends in a spur, and the tail curls round into a ball, as Pugin's do. One shape.
- **Placed** at one unit to the pixel, where the head stands where it did: 19 of the drawing's nodes fall on the built outline's at one offset, to half a thousandth of a pixel (`hand-drawn-x.json`).
- **Pugin's x.** It measures 1.78 px from his x (the construction, 4.66), and overlaps his ink 85% (72%).
- **Spurs.** Its spur is part of the drawing, so `ss01` leaves it as it is.

## The z, drawn over Pugin's stretched to full height
Josh: "Also export the z, which I will hand-draw" ([brief](../brief/2026-10-30-textura-x-z.md)), then "the hand-drawn z is ready to go" and "It's there now" ([brief](../brief/2026-10-30-textura-z.md)). Pugin drew the z on the plate's second line, squeezed; the export put the built z at the font's full height over his z stretched up to it by the built z's fit (`second_line`), with his z as it stands beside it.

- **What he drew.** A new z, nothing kept from the built one: the upper stroke rising to a peak at the left and sweeping over to the right, the diagonal, and the lower bowl turning back along the baseline into a tail sweeping away down to the left. One shape.
- **Placed** at one unit to the pixel where it overlaps the stretched z best: 91% (free to scale, it stays at 0.997). Since none of its points stand where the built z's did, that overlap is the only measure of where he drew it (`hand-drawn-z.json`).
- **Its height.** So placed, its peak stood 44 units above the other letters' heads (522 against 478). On the plate Pugin's z rises only a little above his y's heads: 6.5 px on a line about 72% the height of the first, so 9.0 px, about 21 units, at ours. The stretch in the export, from the built z's fit, made his look taller, and the drawing followed it.
- **Scaled down.** Josh: "We actually need to scale it down - fix the bottom in place, and scale it down to the point it should be lowered to - we're slightly oversized." ([brief](../brief/2026-10-30-textura-z-scale.md)) It is scaled by 0.957 about its lowest point, the tail's point, which stays where it was, until its peak stands 21 units above the heads (499). Its lower bowl stands 8 units below the baseline, its tail's point 18.
- **Pugin's z.** Still compared with his through `second_line`: 3.66 px from his body's edge (as traced, 1.12; the construction, 8.73). The fit that maps it onto his makes his taller than he drew it, so the smaller z lies further off.
- **Spacing.** It is 263 units wide (the construction, 218). Pairs before it close, since the built z's lower stroke reached under the letter before ("cz" 100 → 30, "ez" 85 → 20); "zf" opens 0 → 30, where its peak meets the f's arm. The other letters moved by up to 2 units through the joint fit.

- The s's shape is Josh's. It measures 0.96 px from Pugin's whole letter, 95% within 2.25 px, nearer than any construction came.
- The s has no measurements, spurs or construction in play while its drawing exists; to change it, Josh changes the SVG. The construction (one stroke of a turning pen with twisted ends) stays in the code, unused.
- The pen editor (decision 0013) stays in the code but offers no letter (`PENNABLE` is empty).
- Another letter can be drawn the same way by putting its SVG and placement beside the s's and letting its construction use `OUTLINES`, as the s's does. Or it can stand beside its letter, as the y's does: a placement naming the glyph `<g>.alt` with an `alternate` (its stylistic set and that set's name) needs no change to the code.
- The g is Josh's, too: it has no measurements in play, and its tail, longer than the construction's, sweeps under the letter before as Pugin's does. Pairs with a descender before the g open to keep it clear ("gg" 40 → 80 units). The other letters' side bearings moved by a unit or two through the joint fit.
- Josh's y, as an alternate, leaves the default y as it was: after h and q it opens widely again ("hy" 145, "qy" 150, "gy" 65 units; with `ss03`, 75, 80 and 55). Q40.
