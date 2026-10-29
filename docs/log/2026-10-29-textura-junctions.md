# 2026-10-29 — Pugin Textura: where two strokes meet in one edge

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction** (brief `2026-10-29-textura-junctions.md`). Josh: "the b should align the angle of each stem seamlessly at the bottom". Then the same for the top and bottom of o, the top of q, and the bottoms of v and w.
- **What was wrong.** At each of these joins, two strokes ended in cuts at the nib's angle (45°), but one cut was set off from the other, leaving a step: at the bottom, a stroke's foot against a stroke that stops with the nib's cut; at the top, a flat-topped stroke against the head of the stroke on its right.
- **What Pugin does.** Each join is one straight edge, flatter than the nib's cut. Traced on the plate:
  - about 38° at the bottoms of b, o and v;
  - 38–39° at the top of o;
  - 28° at the top of q.
- **First attempt: lining the cuts up at 45°.** The foot ran on until its cut met the right stroke's cut end to end on one line. That was seamless and true to the pen, but it moved the strokes:
  - the right strokes' corners stood 15–19 px above Pugin's;
  - q's top-left corner stood nearly 30 px below his.

  Not kept.
- **What was kept: truing to Pugin's edge.**
  - Each stroke is drawn as before. The outline is then trued to the straight edge between two points the fit had already put where Pugin's are: the foot's point and the right stroke's corner, or the flat top's corner and the head's peak.
  - The notch is filled and the step trimmed (`nib.true_to`, from `edges` that a construction returns; `edge_below` and `edge_above` in `textura_letters.py`).
  - Shapes, compared outline against outline:
    - b, o, q, v and w change only at their joins (12–16 units, along the edge);
    - every other letter is within a font unit, which is the rounding of the recipes' measurements.
  - Spacing re-ran: a few side bearings moved by a unit, and 29 kerning pairs by 5 units.
- **A full build moves every letter.** The first rebuild shifted the shared measurements (the foot's turn by 1 px, among others) and so every letter. The cause:
  - each letter's fit alone starts from the last family, so the medians drift on every build;
  - a second try, keeping the family but refitting each letter from where it stood, still moved b's ascender arm (its arrive heading by 37°) and g by a little, where Pugin's letter gives the fit little to hold on to.

  So the build now takes `--fit`: only the letters named are fitted; the family and the other letters stay as their recipes have them. `--fit none` refits nothing. The recipes and family were restored from before the first rebuild, and this change was built with `--fit none`; no letter's measurements moved.
- **Checked** in the browser (the overlays of b, o, q, v and w on the proof page). All 27 letters pass the outline checks.
- **Then g, d and the b's bowl** (brief `2026-10-29-textura-junctions-2.md`). Josh: "true g's top like o's and q's, and close the b's counter at the top"; and "also the top of the bowl of the d".
  - **g's top** is trued like o's and q's.
  - **d's bowl top.** Its left stroke's short head and the bowl's top stroke left a V-shaped notch, with the head poking up above Pugin's edge. That edge is straight, at about 33°. It is now trued from the left stroke's top corner to the peak of the bowl's top stroke.
  - **The b's counter.** The bowl's head stopped about 1.5 px short of the stem, so the counter ran out past it. On the plate, Pugin's head starts inside the stem, about 6 px further up and to the left along its own diagonal. A minim can now start its head a little back along that diagonal (`lead`), with the rest of the stroke unchanged. The b's bowl does, by 7.7 px, the one measurement fitted for it (`--fit b:right.lead`, a new form of `--fit` that fits a single measurement).
    - The head's top edge now meets the stem at y ≈ 3344 (Pugin's ≈ 3342).
    - The counter's corner is at ≈ 3353 (his ≈ 3352).
    - The peak is at (361, 3317) (his (363, 3317)).
    - The shoulder is unchanged. The b now has its counter: two contours, where it had one.
  - **Compared with the build before:** only b, d and g changed shape. No recipe changed but b's, which gained the lead. Spacing re-ran: a few side bearings moved by 1–2 units, and 50 kerning pairs by 5 units, with 4 pairs added. All 27 letters pass; checked in the browser.
- **Then d's and g's bowls, and n and m** (brief `2026-10-29-textura-bowls-and-minims.md`). Josh: "close the d's and g's bowls at the bottom so the left foot meets the stroke on its right, as Pugin's do"; and "our m and n are malformed at the top - the connection between stems is created with the spurs at the top, not simply the angled part of the stems."
  - **d and g.** On the plate, the upper corner of each of Pugin's left feet runs right up to the stroke beside it and touches it. The bowls are wider than o's, so the family's foot stopped 9–10 px short.
    - The foot now runs on until the upper corner of its cut is half a hairline inside that stroke's ink (`foot_to_meet`, which finds where that stroke's ink begins at that height): d's to 41 px and g's to 42, against the family's 27.
    - The two join at a point; each bowl is closed (two contours, where each had one).
    - The foot's upper edge now follows Pugin's more closely. Its point stands right of his, about 10 px in d and 6 in g, since his foot's cut is steeper than the nib's 45°. The alternative, keeping the point and truing the cut on to the stroke, wouldn't be the pen's.
    - Mean distance from his edge: d 3.88 → 3.84 px, g 5.73 → 5.88 px.
  - **n and m.** Side by side with the plate, each of Pugin's following heads is an ordinary head, its peak as far from its stem as the first one's. It stands clear of the stem before it, joined to it by a thin hairline rising from that stem along the nib's edge, so the counter comes up to a point just under the next head. Ours started each following head inside the stem before it (`join`), 12 px longer than an ordinary head, so a thick wedge of it joined the stems.
    - Now `after` gives the following minim an ordinary head, with the pen coming up to it from the stem before along its own edge.
    - Mean distance from Pugin's edge: n 2.28 → 1.70 px, m 2.95 → 2.00 px; 95% within 5.3 px for both, from 7.3 and 9.6.
    - The hairline is structural, so the spur-free set keeps it.
    - No fitted letter now measures the family's `join`. u and w still use it, for a foot that runs on into the next minim; it stays at 26 px.
  - Built with `--fit none`: no recipe's measurements changed, and only d, g, n and m changed shape. Spacing re-ran, with a few side bearings ±1–2 units and 27 kerning pairs by 5. All 27 letters pass. Checked in the browser.

## What changed
- **Created:** `docs/brief/2026-10-29-textura-junctions.md`, `docs/brief/2026-10-29-textura-junctions-2.md`, `docs/brief/2026-10-29-textura-bowls-and-minims.md`, this log
- **Updated:**
  - `tools/type/nib.py` (`true_to`, and `edges` in `outline`)
  - `tools/type/textura_letters.py` (`edge_below`, `edge_above`; b, d, g, o, q, v and w return their edges; a minim's `lead` and `run`; b's bowl starts in the stem; `foot_to_meet` for d and g; n's and m's heads joined by a hairline)
  - `tools/type/textura.py` (passes the edges on; `build --fit`, by letter or by one measurement)
  - `fonts/pugin-textura/` (the UFO, spacing, recipes' summaries, the README)
  - `docs/roadmap.md`

## Open threads
- **d's and g's feet** now meet the stroke beside them, but their points stand 6–10 px right of Pugin's; his feet there are steeper than the nib's cut.
- **The first head** of n and m (and every free minim's) has a straight 45° top-left; Pugin's is rounder at the shoulder. Not raised by Josh; noticed while comparing.
- **The 45° alternative** is in this log, not in the code. Bring it back only if Josh prefers the pen's angle to Pugin's at these joins.
- From before: the ampersand; z's lower bowl; the x that reads close to r; the flourished alternates; plate 10's capitals.
