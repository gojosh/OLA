# 2026-10-28 — Lombardic: M, W, the cross and the dot ornament

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh: "Great - go ahead and do the remaining characters". With these six, every glyph on plate 9 is built.
- **The six constructions** (`tools/type/letters.py`):
  - **M, straight (M.2).** Two splayed legs, each on a foot with a curl at both sides; a bar across their heads with a curl at each end, rising to a crest over the middle; a V hanging from the bar, its arms thinner than the legs, its point well above the baseline; a teardrop counter. Symmetric.
  - **M, uncial (M.1).** Two round bowls joined by a stem, on a thin bar with a curl at each end. Each bowl's outside comes down into the bar at a notch inside its curl. The stem rises to a pointed peak between the bowls. Tall oval counters, the right one the left's mirror image. Symmetric: Pugin's right curl sits further in than his left; here they match.
  - **W, two interlaced Vs (W.1).** The left V drawn as the V is (thick left arm, thin right arm); the right V its mirror image; the thin arms cross on the axis. Each arm has a bar with a curl at both ends, and on each side the thick arm's bar runs into the thin arm's, the two curls between them overlapping like two balls close together.
  - **W, rounded double U (W.2).** A top bar with a curl at each end over four strokes. Two bowls, each sweeping round at its foot into a pointed tail tucked under the next stroke. Two straight stems, each flicking out at its foot into a pointed hook (as U's does), with a small round heel on its left parted from the hook by a notch.
  - **The cross.** Four equal arms with hollow sides, narrow at the centre; each end a bar with a curl at both corners rolling back toward the centre. Built on half an arm, mirrored and turned through the four quarters, so it has the square's symmetry.
  - **The dot ornament.** Seventeen dots, four squares of four about a middle dot, all one size on a square grid (Pugin set his by hand). It is centred on half the cap height, as on the plate.
- **How W.1 is built.** The overlaps are worked out, not drawn by hand. Each thin arm's edges run as single curves from its bar to the far V's point and crotch. The build finds where they cross the axis and each other, and cuts them there. The two overlapping curls are cut where their balls meet, giving a notch above (on the outline) and one below (on the counter). The bars are placed inward from the axis, so the inner curls can never run into their mirror images.
- **Two glyphs take their own curl size.**
  - **The cross:** Pugin's cross curls are drawn larger than the letters'. Fitted, 1.15 of the averaged curl (the family's is 0.946).
  - **W.1:** Pugin drew eight curls along its top line and made them smaller. Fitted alone, W.1 wanted the family's lower bound (0.8). The first build gave it the family's curl (0.946). The bars then crowded: the inner curls ran into their mirror images across the axis, and two flares bulged past their nodes. W.1's curl is now fitted to W.1 alone: 0.78.
  - Both belong in the terminal-size pass Josh has asked for.
- **A cut reference.** Plate 9's frame cuts about 11 px off W.1's first curl in the reference (`extract` keeps 20 px inside the frame). Re-extracting would shift every reference and so every fit and every recorded move, so instead the fit no longer compares the construction with the reference where the construction runs past the reference's edge (`construct.fit_letters`). E's reference touches the frame on its right side too; E's fit didn't change.
- **Encodings (provisional).**
  - The straight M and the W of two Vs have the M and W keys. The uncial M and the rounded W join the uncial T under `ss01`, which is now the set of uncial forms (Q34 updated).
  - The cross is on U+2720 ✠, the dots on U+2059 ⁙. Both are new question Q35.
- **Shared parts added.**
  - `construct.py`: `mirror_copy`, a mirrored contour of its own (M.1's and W.1's second counters); `cross_x` and `crossings`, where curves cross an upright or each other; `cut`.
  - `letters.py`: `hooked_foot` (W.2's stems); `cap_top` can be placed by the construction and given a wider range for its flares' neck angles.
  - Editing these refits every letter (about two minutes). The shared values barely moved.
- **Josh's moves made on the proof page during this session** (N, O, P, Q, R, S, T.2, Y and Y.2, besides G) all still apply after the refits; none is stale.
- **Results.** All 31 glyphs pass the outline checks. Mean distance of Pugin's edge from the construction: W.2 0.74 px, W.1 1.47 px, M.2 1.72 px, M.1 2.40 px, the cross 2.93 px, the dots 2.90 px. The last three are where symmetry or the grid overrules Pugin's hand.
- **The proof page** sets M, W, the cross and the dots in its specimen line.

## What changed
- **Created:**
  - `fonts/pugin-lombardic/recipes/M_1.json`, `M_2.json`, `W_1.json`, `W_2.json`, `cross.json`, `ornament_dots.json`
  - this log
- **Updated:**
  - `tools/type/letters.py` (six constructions, `hooked_foot`, `cap_top`)
  - `tools/type/construct.py` (crossings and cuts, `mirror_copy`; the fit ignores the construction beyond a reference's edge)
  - `tools/type/type.py` (the proof's specimen line)
  - the UFO and `family.json`
  - the family README, `docs/open-questions.md` (Q34; new Q35), `docs/roadmap.md`
  - `.gitignore` (Python's `__pycache__/`, which the build leaves in `tools/type/`)

## Open threads
- **Q34:** which forms of M, T, W and Y are the defaults.
- **Q35:** code points for the cross and the dot ornament.
- **The terminal-size pass** (Josh): the curl, the balls, the two-lobe and the trefoil, and now whether the cross and W.1 keep curls of their own size.
- **Kerning**, and spacing for the cross and the dots: they are spaced as letters for now.
- The references for W.1 and E are cut by the plate's frame. Leave them unless a fit needs the missing edge.
