# 2026-10-29 — Pugin Textura: finer features, starting with the e

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-e-member.md`). Josh: "time to add some finer features. Starting with the e, for the crossing member, there is a thin cradling stem with a pip at each end, crafted with the tip of the nib."
- **Pugin's member, read from the plate.** A thin S.
  - It starts in a pip about 18 px across, just above the arm's end. It curls right and down round that end.
  - It runs down to the left at about 45° under the arm's tip, touches the stem's right edge low in the eye, and curls down into a second pip about 20 px across.
  - It is thin all along, a little fuller at the turns.
- **The nib's tip.** A stroke drawn with the tip is a `nib.Stroke` with the nib narrowed to its own thickness, a small square a hairline across (`textura_letters.tip`). It is a hairline wide moving along the nib's edge, and up to about 1.4 times that across it, which gives the member its slightly fuller turns.
- **Pips.** `nib.Dot`: a filled circle that the outline takes as it is, not as ground a nib covers. `pips` puts one at each end of a fine stroke, each with its own fitted size.
- **The member** replaces the straight hairline.
  - It is a free stroke of the tip through five nodes, with a pip at each end: top, turn, cross, low, end.
  - Its lowest turn is pinned half a hairline out from the stem's edge (`path` now takes `at` for a node whose x is set), so its ink meets the stem and closes the eye. Fitted freely, it stopped about 3 px short and the eye opened.
  - Only the member's measurements were fitted (`--fit 'e:member.*'`): both pips came out about 21 px across, close to Pugin's (about 18 above, 20 below).
- **Result.** The e's mean distance from Pugin's edge fell from 3.73 to 2.40 px. The eye is closed. Only the e changed shape, and all 27 pass. Checked in the browser, at display and text sizes.
- **Plain and flourished.** In the plan (decision 0008), Pugin's hairlines and balls were left to the flourished forms, and the plain e had a straight hairline. Josh now wants these finer features in the letters, so the member and its pips are part of the e as it stands. The flourished alternates still to come are the swashes and loops.
- **The e's top stroke** (brief `2026-10-29-textura-e-arm.md`). Josh: "Notice the angle of our line at the top of the e - it should point much more directly downward, instead of swooping up - we're pretty far off."
  - The arm left the stem heading 43° down and flattened to 16° by its end, so its upper edge dipped and then swooped up into the curl.
  - Pugin's is a straight wedge, like his c's top: its upper edge runs steadily down from the peak into the curl.
  - A first try curved the arm the other way (55° at its end). It pointed down, but it left a notch under the curl and fitted worse (3.01 px).
  - The arm is now a straight light stroke, from the stem's top down to the right at about 39°, refitted with the member (`--fit 'e:arm.*,e:member.*'`). Its start is where it was, so the concave top is unchanged.
  - Mean distance from Pugin's edge: 2.40 → 2.03 px. The eye is still closed. Only the e changed; all 27 pass; checked in the browser.
- **The member's S and its pips** (brief `2026-10-29-textura-e-cradle.md`). Josh: "we need to calculate properly to have gentle sweeping S curve for the crossmember, and and properly aligned cradling of the pips. (the turn into the bottom pip in particular is quite harsh"; then the top pip "should originate a bit more from the top"; then "The bottom pip should be cradled from the bottom, whereas now, we punch into the right side."
  - **What was wrong.** The member was five free nodes with independent headings and tensions (0.24 to 0.93 after fitting), so its curvature was uneven. It ended in a tight hook aimed at the bottom pip's centre.
  - **Cradling, worked out** (`cradle`). The stroke meets a pip tangent to a circle one tip's half-breadth inside the pip's edge. The tip's half-breadth depends on the stroke's heading, since the tip is a small square at the nib's angle (`tip_half`). There the stroke's outer edge runs on into the pip's edge with no kink, and the pip lies in the stroke's curl. Where round the pip the stroke meets it is a measurement.
  - **The member now has three parts:**
    - a curl from the top pip down to its rightmost point;
    - the S, one cubic heading straight down at both ends, from there to where it touches the stem (still half a hairline out from the stem's edge);
    - a turn under the bottom pip.
  - **The pips' angles are held** at Josh's direction: the top pip met at -65°, near its top (the fit put it at -33°, where the stroke left the pip's side); the bottom pip at 100°, from beneath.
  - **On the way.**
    - An angle started at exactly 0° never moved in the fit, as its test step was too small to feel.
    - A single cubic from the top pip to the stem couldn't wrap over the pip: it left it as a short stalk and exposed the arm's square end.
    - The curl as a part of its own fixed both.
  - Mean distance from Pugin's edge: 2.03 → 1.98 px. Eye closed; only the e changed; all 27 pass; checked in the browser.
- **Blending into the pips** (brief `2026-10-29-textura-e-pip-blend.md`). Josh: "look at the right edge off the top - not a smooth and seamless blend into the pip", then "the outside edge of the s should curve both with tangency and curvature scale into the pips."
  - **The tip was square.** Leaving the top pip, the outline followed the pip's circle, broke into a short straight 45° facet (the square tip's flat side), then took up the curl. A square tip can't run tangentially into a round pip.
  - **A round tip.** A 24-sided point, tried first, made each stroke hundreds of overlapping pieces. pathops' one-pass clean-up silently dropped the member's body, the same failure as the h's stem at 50°.
  - **Offsets instead.** The tip stroke is now built directly as its path offset by the tip's radius to either side, as cubics (each control-polygon edge moved over and re-met, Tiller and Hanson, halved until within a tenth of a pixel), with round ends (`nib.tip_region`, `nib.offset`). Its edges are true parallels of its path.
  - **Curvature too.** Matching only direction left a sudden change of bend where the stroke left each pip.
    - `cradle` now also gives the bend of the circle the stroke's centre must follow at a pip: a radius one tip-radius inside the pip's edge, so its outer edge bends exactly as the pip's edge does.
    - `g2` builds a cubic with given directions and bends at both ends, solving its two handle lengths.
    - The S keeps its handle lengths as its only shape setting; the curl and the turn are solved to match the pip at one end and the S at the other. The bends are continuous all along the member.
  - **The arm's end.** With the S passing a little higher, the arm's square end stood out about 4 px below it as a corner. The member is written over the arm, so what of the arm's end stands past the member's far edge is trimmed to that edge (`under`; `true_to` now takes a run of cubics). The S's edge runs on unbroken.
  - Mean distance from Pugin's edge: 2.22 px (from 1.98), because the trim removes a sliver his ink has. Eye closed; only the e changed; all 27 pass; checked in the browser.
- **The turn into the bottom pip** (brief `2026-10-29-textura-e-turn.md`). Josh: "the final turn toward the bottom pip it too sudden", and then "The bottom pip is too large in that render".
  - **Measured along the member,** the solve for matching bends had failed at both ends and fallen back to plain handles. The turn bent at a 6 px radius right where it left the stem, almost a corner, and was nearly straight by the pip. A single cubic can't ease from the S's bend (radius 44 px) to the pip's (6 px) in the room it has.
  - **Spirals.** The curl and the turn are now spirals (`spiral`): the bend runs from the S's to the pip's along the stroke, never jumping. An even change (an Euler spiral) made the turn only about 15 px long, so the pip sat hard against the stem. The change is now progressive, staying gentle for longer and tightening mostly near the pip, by a fitted setting each: the turn's came out strong (4.4), the curl's mild (1.8).
  - **Where things land.**
    - Where the curl comes out fixes where the S starts, and so its bend there; a few rounds settle the two.
    - The bottom pip's place follows from where the turn ends.
  - **The bottom pip's size.** Left free, the fit grew it to about 26 px across, filling Pugin's ink along the stem. It is now held at his size, about 20 px across.
  - **The arm's trim.** It had guessed which side of the S was the outside from where the arm's end lay. With the S moved, it guessed wrong and cut the arm away, opening the eye. It now takes the side as given: the member's outside is its lower right.
  - **The bend along the member,** from the top pip to the bottom one, now runs from a radius of 7 px at the pip, out through 44 px in the S, and back in to 8 px at the bottom pip, changing steadily.
  - Mean distance from Pugin's edge: 2.43 px. Eye closed; only the e changed; all 27 pass; checked in the browser.
- **Josh asked whether he should adjust these detail lines by hand.** The textura has no editor yet; the Lombardic's point editor (decision 0010) moves outline points, which here would fight the pen. A textura editor should move a stroke's nodes and settings, saved in the recipe as the build already keeps held values. Offered as a next step.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-e-member.md`, `docs/brief/2026-10-29-textura-e-arm.md`, `docs/brief/2026-10-29-textura-e-cradle.md`, `docs/brief/2026-10-29-textura-e-pip-blend.md`, `docs/brief/2026-10-29-textura-e-turn.md`, this log
- **Updated:**
  - `tools/type/nib.py` (`Dot`; tip strokes drawn as offset curves with round ends, `tip_region`, `offset`; `true_to` takes a run of cubics)
  - `tools/type/textura_letters.py` (`tip`, `cradle` with the pip's bend, `spiral`, `under`; `path` takes `at`; the e's crossing member as a curl, an S and a turn, matched in direction and bend to its pips; its arm made straight, its end under the member)
  - `fonts/pugin-textura/` (the UFO, recipes, spacing, the README; the e's recipe holds where the member meets its pips)

## Open threads
- **Which other letters have tip strokes and pips.** On the plate: c and r hang a hairline and ball from their arms, s from its arm and spine, d's arm ends in a ball, y's and x's tails end in balls. Next in Josh's list of finer features, at his direction.
- **What counts as plain now.** Whether these features belong to every form, or some only to the flourished ones, is Josh's call as more are added (decision 0008's split between plain and flourished forms).
