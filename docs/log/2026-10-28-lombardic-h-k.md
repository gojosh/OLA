# 2026-10-28 — Lombardic H and K, and the two-lobe terminal

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** After the five-letter commit, Josh: "Good. Onward." Per the roadmap: H and K, with the two-lobe terminal.
- **Mid-session, Josh:** a family-wide look at terminal lobe sizes ("in all varieties - one to three") comes later, once more letters are in, because Pugin's are inconsistent. Brief: `docs/brief/2026-10-28-terminal-lobe-sizes.md`. For now each terminal keeps its own fitted size.
- **The two-lobe terminal** (`two_lobe` in `tools/type/construct.py`).
  - Measured: Pugin's H lobes are equal circles (radius 18.2 px) set 2.5 radii apart. K's second lobe is a bump merged into the first.
  - Built as two equal round lobes overlapping (spacing under two radii), so the cusp is crisp. Arcs are split at their extremes.
  - The stroke's outside meets the first lobe at a sharp neck; its underside leaves the second at a corner.
  - Radius, spacing and direction are family measurements shared by H and K.
  - K's lumpy terminal is read as a sloppy two-lobe and built as H's (noted in its recipe). If K should end in a plain curl instead, that is a one-line change.
- **H.** The I's stem, top-left and bottom curls; a long top bar dipping over the stem to a top-right curl; a shoulder springing from the stem under the bar, arching over and down to a foot sweeping into the two-lobe terminal. A sliver of space between bar and shoulder comes to a point on the stem.
- **K.** The I's stem, top-left and bottom curls; a top bar to a square corner dropping as an arm to a crotch; a leg sweeping from there to the two-lobe terminal; a pointed upper counter closed against the stem; a lower counter pointed under the arm, open at the bottom right.
- **New shared parts in `letters.py`:** `left_side` (stem, bottom-left and top-left curls), `bottom_right` (bar to the bottom-right curl and back), `lobed_foot`.
- **Results.** All seven letters pass the outline checks. Means from Pugin's edges (shared / alone):

  | Letter | Shared | Alone |
  |---|---|---|
  | E | 0.85 | 0.82 |
  | F | 1.56 | 1.30 |
  | H | 1.50 | 1.05 |
  | I | 1.32 | 0.89 |
  | K | 1.41 | 1.46 |
  | L | 1.75 | 1.51 |
  | T | 2.01 | 1.89 |

- **The stems fall into two groups.** I and L, mostly stem, are about 80 px; F, H, K and T, which carry arms, a shoulder or a wide bar, are 71–75 px. That looks like optical compensation. The shared stem is now 76.1 px, which is why I moved furthest (0.89 → 1.32 px). Put to Josh: one stem, or one per group.
- **Curls** run from 0.84 (H) to 1.05 (L) of the averaged curl; shared 0.942. **Two-lobe terminals** fitted alone differ in spacing (H 1.95 radii, K 1.41) and direction (26° and 68°); shared 1.54 radii, 40°.

## What changed
- **Created:**
  - `fonts/pugin-lombardic/recipes/H.json`, `K.json`
  - `docs/brief/2026-10-28-terminal-lobe-sizes.md`
- **Updated:**
  - `tools/type/construct.py` (the two-lobe part and its family measurements)
  - `tools/type/letters.py` (H, K, shared parts)
  - `tools/type/type.py` (proof: two-lobe column, new specimen words)
  - the UFO source, `family.json`, all recipes' fitted measurements
  - the family README, `docs/roadmap.md`

## Open threads
- **Stems:** one shared stem, or one for the mostly-stem letters (I, L) and one for the rest? (asked)
- **Terminal lobe sizes:** the curl ball, the two-lobe and the trefoil to be settled together once more letters are in (Josh).
- **K's terminal:** built as the two-lobe; confirm, or use a plain curl.
- **Next letters:** the round letters from E's bowl (C, D, O, Q), then B, G, P, R with the trefoil. Spacing after that.
