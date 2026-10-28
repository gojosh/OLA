# 2026-10-28 — Lombardic: two stem weights, the round letters, first spacing

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **Two stem weights.** Josh: "Give the two groups their own stem: one for the letters that are mostly stem (I, L), one for those that carry arms, shoulders or wide bars (F, H, K, T). Then continue with the round letters." Recorded as decision 0009.
  - The family now has `stem_plain` and `stem_armed`.
  - With eleven letters fitted, they settled at about 80 px and 71 px.
- **The round letters** (`tools/type/letters.py`):
  - **C:** the E's bowl and right stroke without the middle bar; its counter is an oval.
  - **O:** a symmetric oval ring with a ball hanging into the counter from the top and one rising from the floor. Pugin's lower ball is off to the left; the construction centres it.
  - **D:** a stem (armed weight) with top-left and bottom-left curls and a round bowl. Pugin's bowl has a slight point on the right; it is rounded, as every bowl is.
  - **Q:** the O's bowl with a top ball and a floor ball. The base runs past the bowl to a rounded end; a flag rises from it, parted from the bowl by a pointed notch, to a curl at its head, turned to roll out to the right (a new curl orientation, `head-right`).
- **New shared parts.**
  - `bowl_and_stroke` (E and C).
  - `oval_counter`.
  - Symmetric letters can now have several mirrored contours (O).
  - A family measurement `ball_r` for the balls inside O and Q, to be settled with the other lobes later (Josh's note).
- **Fixes along the way.**
  - **The floor of O and Q.** A node at the floor's lowest point contradicted the ball, because the floor is lowest where it meets the ball. Reverted to one curve required to descend into the ball.
  - **Arcs.** Arcs split at their extremes could leave a sliver segment next to an end, which crashed the outline check after a 15-minute fit. Arcs no longer cut within half a degree of their ends.
  - **The outline check.** It now reports degenerate segments instead of crashing.
- **Spacing**, at Josh's request, while the build ran ("Can we work on a basic spacing while that runs? So the letter spacing is more natural?").
  - **The method:** area-based side bearings, after HT Letterspacer.
    - Along each side, on every line from baseline to cap height, measure the white between the letter's outermost point and its edge, counting no deeper than 120 units.
    - The side bearing is 130 units less that mean depth, between 35 and 75 units.
    - The upper limit is for T, whose white sits inside the letter under its arms, where the profile can't see it.
  - **How the values were chosen:** compared by eye on test words against the flat 50 units, at three settings.
  - **Where it lives:**
    - `spacing` in `source.json`;
    - `construct.side_bearings` and `respace`;
    - a new `space` command that respaces and rewrites the font without fitting again;
    - `build` now spaces as its last step.
  - **Results:** in `spacing.json`. There is no kerning yet. Left and right side bearings in units:

    | C | D | E | F | H | I | K | L | O | Q | T |
    |---|---|---|---|---|---|---|---|---|---|---|
    | 64, 38 | 35, 66 | 65, 38 | 35, 72 | 35, 75 | 35, 35 | 35, 35 | 42, 47 | 68, 68 | 69, 55 | 75, 75 |

- **Results.** All eleven letters pass the outline checks.
  - **Shared values:** stems 79.9 px (plain) and 71.2 px (armed); curl 0.943; balls 25.4 px.
  - **Means from Pugin's edges:** C 0.75, D 1.00, E 0.82, F 1.38, H 1.49, I 1.11, K 1.21, L 1.65, O 1.69, Q 1.35, T 2.03 px.
  - **I** came back toward Pugin's with its own stem weight (1.32 → 1.11 px). The proof's words are now THE, COLLECT, OFFICE, CLOCK, FIELD, HOLD.

## What changed
- **Created:**
  - `docs/decisions/0009-lombardic-stem-weights.md`
  - `fonts/pugin-lombardic/recipes/C.json`, `D.json`, `O.json`, `Q.json`
  - `fonts/pugin-lombardic/spacing.json`
- **Updated:**
  - `tools/type/construct.py`: two stems, `ball_r`, the `head-right` curl, multi-contour symmetry, spacing, sturdier arcs and checks
  - `tools/type/letters.py`: C, D, O, Q, shared parts
  - `tools/type/type.py`: `write_font`, the `space` command, the proof's stem column and specimen words
  - `fonts/pugin-lombardic/source.json` (spacing)
  - the UFO, `family.json`, the family README, `docs/decisions/README.md`, `docs/roadmap.md`

## Open threads
- **Kerning:** T, L and F beside round letters will want pairs.
- **Terminal lobe sizes:** the curl ball, `ball_r`, the two-lobe and the trefoil, to be settled together once more letters are in (Josh).
- **Next letters:** B, G, P, R, which carry the trefoil (refit it from all its instances).
