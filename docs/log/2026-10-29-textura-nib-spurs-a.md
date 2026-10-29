# 2026-10-29 — Pugin Textura: the nib's angle, spurs, and the a

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **Josh's corrections** (brief `2026-10-29-textura-corrections.md`): "the nib angle is too shallow - needs to be a few degrees more vertical"; spurs, with "a setting for the spur, where it can be turned on or off"; and "the top left part of the a is accomplished with a curved line".
- **The nib's angle.** The shared fit had drifted to 40°. The font now holds it at 45°, the angle measured from the edges of Pugin's heads and feet. That agrees with Josh's eye: "a few degrees more vertical".
  - It is a `held` value in `source.json`: fixed in both the fits alone and the fit together, and reported in `family.json`.
  - The letters fit Pugin's about as well as before, a little better or worse by letter (o 1.7, v 2.2, t 1.6, z 8.7 px).
- **Spurs.**
  - On the plate, where a foot is free, the pen carries on past the foot's tip in a short hairline up and to the right. It is clearest on l (about 30 px), and shorter on i and the last minims of m and n. Feet that run into another stroke have none.
  - In the font, `minim` writes the spur when the letter is written with spurs, set from the plate and not fitted, since hairlines that thin fit poorly. First 22 px at 41°; Josh: "The spurs are generally too pronounced, compared to Pugin's work." Now 10 px along the nib's own angle, so each spur is exactly the nib's hairline (Pugin's are mostly 5–12 px). The constructions mark the feet that run into another stroke (inner feet of n and m, left strokes of o, q, v and y, b's and d's bowls, w's first two). Fifteen letters have spurs.
  - The fit to Pugin is made without spurs. The build writes each letter twice: with spurs, as the default glyph, and without, as `<letter>.nospur`, in the same place and width.
  - The stylistic set `ss01` ("Without spurs", named in the font) swaps them in. Each letter and its alternate share a kerning group, so kerning holds either way. Checked in HarfBuzz.
  - The proof page sets its words both ways.
- **The a.**
  - The straight wall under the head is now a curved stroke: it starts with the nib's edge across the top, comes down, and curves round to the right. (The committed wall had in fact been a separate block, detached from the rest of the letter.)
  - My mistake: to fit the new stroke I cleared the a's saved fit, which refitted the lower bowl too, and I ran the curve on across the waist into the stem, which added ink along the bowl's top. Josh: "You changed the bottom bowl on the a, but I didn't ask for that. It was correct before."
  - The fix: the bowl's measurements are restored from the commit and held (a recipe can now hold a letter's own measurements: `held`, applied in both fits), and the curve ends exactly where the bowl begins, so it adds nothing to the bowl. Compared outline against outline, the bowl matches the committed one, apart from the slight shift every letter takes from the 45° nib.
  - Brief: `2026-10-29-textura-corrections-2.md`.
- **The a, again** (brief `2026-10-29-textura-a.md`). Josh: the upper bowl "should be a single smooth curve, much like the bottom bowl, which results in a seamless sloped top of the a where it joins the main stem"; and "the bottom bowl has a spur".
  - The upper bowl, the sloped top and the stem are now one pen stroke: from the waist up round the left, over the top, down the slope into the stem, and on down to the foot. The separate head and curve, and the join between them, are gone; the upper counter takes Pugin's rounded wedge.
  - The lower bowl's foot ends in a spur reaching up toward the stem, as Pugin's does. A new `spur_from` writes a spur at the end of any free stroke; the minim's foot uses it too, and `ss01` drops it with the rest.
  - The lower bowl's held measurements are unchanged, checked against the commit.
- **The a in three strokes** (brief `2026-10-29-textura-a-strokes.md`). Josh: "Closer. But notice you've rounded most everything and joined previously separate lines. This a would have been drawn with three strokes. The stem (which is slightly concave in the top segment), the bottom bowl, and finally the top bowl. Where each of these three strokes intersect is precise…"
  - My previous step had run the top bowl and the stem together as one path, which rounded the junction. Now the a is three strokes, each a smooth path, meeting at points: the stem from the top of the letter; the bottom bowl (held); and the top bowl from the stem's top, rising left into the sloped top, round the left and ending exactly where the bottom bowl begins.
  - The outline keeps sharp corners at the top right (sloped top against the stem's right edge), at the bottom of the upper counter, and at the waist.
  - The stem's upper part bows slightly. On the plate it sits about 2 px left of the stem's line below the waist; the fit treats that as noise, so the bow is held (the stem leaves the top at 6° off upright).
  - The README now states the rule: strokes meet, they don't merge.
- **Results.** 27 letters, all passing the outline checks. Checked in the browser.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-corrections.md`, `docs/brief/2026-10-29-textura-corrections-2.md`, `docs/brief/2026-10-29-textura-a.md`, `docs/brief/2026-10-29-textura-a-strokes.md`, this log
- **Updated:**
  - `tools/type/textura_letters.py` (spurs in `minim` and `spur_from`, which feet have none, the a)
  - `tools/type/textura.py` (held family values, and a letter's own held measurements from its recipe; writing each letter with and without spurs; the `ss01` feature, kerning groups; the proof's spur-free line)
  - `fonts/pugin-textura/` (`source.json`: `held`, `spur`; recipes, family, spacing, the UFO, the README)
  - `docs/roadmap.md`

## Open threads
- Spur length and angle are one setting for every foot; Pugin's vary (l's is much longer). Judge on the proof page; the length is one number in `source.json`.
- **A lesson for agents:** don't clear a letter's saved fit to change one part of it; hold what Josh has accepted.
- The ampersand; z's lower bowl; the x that reads close to r.
- The flourished alternates; plate 10's capitals.
