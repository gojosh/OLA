# 2026-10-29 — Pugin Textura: the pen turns

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-pen-turns.md`). Josh: "we need to push the standard nib angle to 50 degrees. We're still too shallow." Then, while that was under way: "There is nib rotation going on in Pugin's original. The top connecting spurs are at 45°, but the feet are nearly all at 50°."
- **50° throughout, tried first.** Three ways, each keeping every letter's own measurements:
  - A: only the angle changed;
  - B: the shared measurements refitted to suit (`--fit family`, new);
  - C: the nib widened so upright stems keep their width.

  All three fit Pugin a little worse than 45° did. Mean distance from his edge, over the letters without heavy flourishes: 45° 3.42 px; A 3.60; B 3.53; C 3.65. Each costs something:
  - A thins the stems to 34 px from 36.5;
  - B thickens the hairlines to 9.7 px from 7.3;
  - C makes the heads heavier.
- **A pen that turns** (`nib.Pen`).
  - The nib is at 45° at the heads (on the x-height line and above) and at 50° at the feet (on the baseline and below), turned evenly between. Both are held in `source.json` (`nib_angle`, `nib_angle_foot`).
  - How each part of a stroke is drawn:
    - where a segment keeps nearly one angle, it is drawn exactly as before at its mean angle;
    - a straight stem turning on its way down covers the hull of the nib at its two ends;
    - a curve turning further is cut into pieces that turn no more than a degree;
    - the nib at every node is set at that node's own angle, so the cuts at a stroke's ends are exact.
  - The spur now follows the pen (along the nib's edge at the foot, 50°), so `source.json`'s spur has no angle of its own.
  - The nib's width and hairline are unchanged, so a stem narrows a little, from 36.5 px under the head to 34 over the foot.
  - Mean distance from Pugin's edge: 3.47 px, against 3.42 at 45° and 3.53–3.65 at 50° throughout. a, i, h, t, v and x fit him better than at 45°; d and g a little worse.
- **What the turn changed.**
  - With the feet at 50°, a foot's corner reaches about 1.2 px less far, and the stroke beside it starts about 1.2 px further right. q's bowl opened at the bottom, and y's two strokes came apart. Their left feet now run on to meet the stroke on their right (`foot_to_meet`, now never shorter than the family's foot), as d's and g's do.
  - e's hairline now reaches the arm and closes the eye, as its description always said it should.
  - Every other letter keeps its contours. Outlines have more nodes (n 38 → 55 segments) where the turning stem meets the head and foot; all 27 letters pass the outline checks.
- **A fault found on the way.** At 50°, the union of h's strokes silently dropped most of its stem: joining every piece of every stroke in one pathops pass mis-resolved the windings. `nib.outline` now cleans each stroke on its own and joins them one at a time. At 45° that gives the same area for every letter, in the same time.
- **`--fit family`**, new: refits the shared measurements alone, the letters keeping theirs. A shared value no letter Pugin drew measures (`join`, used by u and w) now carries over instead of dropping out.
- Built with `--fit none` (the family as it was, plus the two held angles); no recipe's measurements changed. Checked in the browser.
- **Then, lighter strokes** (brief `2026-10-29-textura-light-strokes.md`). Josh: "I think we need to introduce a narrower nib - perhaps for Pugin the was accomplished with less pressure? But take the top stroke of the c, for example - it should be about 20% thinner. Same with the e and top bowl on the a", meaning the e's top stroke, not the whole letter.
  - A stroke can now be written with less pressure (`nib.Stroke`): the nib is narrowed to a share of its width, and its hairline is kept. The share is a held family value, `nib_light`, at 0.8.
  - The c's top stroke, the e's arm and the a's top bowl are light. Each keeps its path, so both its edges move in.
  - Mean distance from Pugin's edge: a 2.63 → 2.29 px, its top bowl now on his edges inside and out; c 3.32 → 3.67; e 4.20 → 4.38. For c and e his hanging hairline and ball under the stroke count as ink, which favours a heavier stroke; side by side with the plate, the lighter strokes look right.
  - **The a's join.** The stem and the top bowl both start at the stem's top. With the bowl lighter, the stem's full-width corner stood about 4 px proud of the sloped top, a small tooth. The sloped top now runs straight on into the stem's right edge (an `edges` trim), so the two still meet seamlessly at a point.
  - Only a, c and e changed; all 27 pass.
- **Then the concave tops** (brief `2026-10-29-textura-concave-tops.md`). Josh: "the top of the c, d, e, g, and s all have a concave curve on the top left where the primary stem and top line intersect. We need to retain this. It's one of many fine features accomplished by subtle nib rotation."
  - **Measured on the plate.** From the stem's top corner, Pugin's edge rises at 13° in c, 24° in d, 19° in e, 4° in g and 13° in s, and meets the peak at 39–52°, along the nib's own edge. It sags 3–6 px below a straight line.
  - **Built** as the curve the nib's edge sweeps as the pen turns (`concave_top`): a cubic from the stem's top corner, leaving at 13° (the median; `top_leave`, held), to the top stroke's peak, arriving along the nib's edge.
    - The outline is trued to it: the gap below filled, the corner above trimmed. `nib.true_to` now takes a curved edge as well as a straight one.
    - Simulating the turning nib itself (an edge sliding along itself as it turns) would need the edge's envelope, not just its corners' paths. The curve is that envelope's shape.
    - d's and g's straight top edges became curves. o and q keep theirs, as Pugin's are straight.
  - **e and s:** their minim heads stood up and out to the left of Pugin's, with a V between head and top stroke. His e and s tops are single sweeps, as his c's is. Both are now flat-topped stems meeting the top stroke in the concave curve.
  - **Refitting.**
    - c, e and s refitted only the stem's top and the start of the top stroke (`--fit c:stem_top,c:top.from.*,…`; `--fit` now takes a trailing `*`). A first try that let the e's whole arm move lifted its far end 3 px and opened the eye.
    - c's wedge start is at the edge of its range.
    - Under the curve, the fill now reaches to the top stroke's lower corner, not its centre: from the centre, a sliver poked into g's counter.
  - **Mean distance from Pugin's edge:** c 3.67 → 3.55 px, d 4.07 → 3.90, e 4.38 → 3.73, s 5.67 → 5.09; g 6.28 → 6.50 (his g peaks in a flourish).
  - Only c, d, e, g and s changed; all 27 pass; checked in the browser.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-pen-turns.md`, `docs/brief/2026-10-29-textura-light-strokes.md`, `docs/brief/2026-10-29-textura-concave-tops.md`, this log
- **Updated:**
  - `tools/type/nib.py` (`Pen`; strokes drawn with a turning nib; strokes joined one at a time; `Stroke`, written with less pressure; `true_to` takes curved edges)
  - `tools/type/textura_letters.py` (`nib_angle_foot`; `pen_of`, `nib_at`; the junction helpers and the spur take the nib at their height; q's and y's feet meet; `nib_light` and `light`; c's top, e's arm and a's top bowl light; the a's sloped top trimmed into the stem; `top_leave`, `concave_top` for c, d, e, g, s; e and s flat-topped)
  - `tools/type/textura.py` (the pen; `--fit family`; unmeasured shared values carry over; `--fit` patterns)
  - `fonts/pugin-textura/` (`source.json`: the held angles, `nib_light`, `top_leave`, the spur; the UFO, recipes, family, spacing, the README)
  - `docs/roadmap.md`

## Open threads
- **Which other strokes are light.** Only the three Josh named. Others may be: the d's bowl top, the s's arm, r's flag. For Josh's eye.
- **How the pen turns.** It turns evenly by height between the x-height line and the baseline. Whether Pugin's turns the same way, or mostly near the foot, is for Josh's eye. The two angles and the lines between which it turns are the whole setting.
- **Stems narrow** about 2.5 px from head to foot. If that reads as wrong, widening the nib a little toward the foot would hold them even.
- From before: the first heads' straight 45° shoulder (Pugin's is rounder); d's and g's foot points stand right of his; the ampersand; z's lower bowl; the x that reads close to r; the flourished alternates; plate 10's capitals.
