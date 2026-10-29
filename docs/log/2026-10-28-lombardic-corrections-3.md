# 2026-10-28 — Lombardic: third round of corrections; a modern Y

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
Josh's notes (verbatim in `docs/brief/2026-10-28-lombardic-corrections-3.md`). Each was checked against Pugin's letter before changing anything:

- **B, "the bottom left lobe should dip further down."** Pugin's bar between the bottom-left curl and the bowl rises to a high point, so the curl hangs below it. B's bar had been one flat curve; it now has the high point.
- **F, "the inner lobe should curve inward further."** The stroke's inside may now leave the trefoil's inner lobe as far round as the lobe's top. The lobe curls in toward the counter, and the stroke reads as sweeping outward.
- **G, "the top has more curvature, and the stem is thinner where it joins the lobes."** Read as the inner spiral: a tighter hook, thinning to a neck at the trefoil.
  - A new option for the trefoil, `trefoil_at(..., neck=...)`, sets the stem's width where it meets the lobes. The stem's edges join the side lobes where two lines that far apart cross them.
  - G's neck is 12–26 px.
- **K, "a dip in the top of the initial line."** Pugin's top edge dips over the stem; the fit's low point had sat out near the corner. Starting it over the stem found the dip.
  - In the process the arm's outside could swell below the rounded corner. The corner now ends at the arm's rightmost point, turned straight down.
- **L, "the right tip is actually two lobes close together."** Measured:
  - a broad crown, about 36 px in radius, which the arm runs up into;
  - a ball the size of the two-lobe terminal's on its lower right, meeting the crown in a shallow waist;
  - a notch on the left, where the arm's outside comes up.

  The two-lobe part now takes unequal radii. L's tip is 1.04 px from Pugin's, against 3.98 with equal lobes.
- **Q, "a perfectly smooth transition into the lobe."** The curl primitive forced the flag's inside upright where it met the ball, a visible step.
  - The flag's head is now a round ball the flag runs into while still leaning, as with S's balls.
  - "The bottom lobe ... more rounded, instead of like a ledge": the base now ends in a round ball, with a notch where the flag's outside meets it.
- **Uncial T, "the stem should be thinner where it connects to the center lobes ... the bottom of the primary T line should be a seamless curve."**
  - The bar's underside now flows into the stroke in one curve on each side. The notches are gone.
  - On the left, a node sits where the curve turns from climbing to running left.
  - The spiral thins to a neck at the trefoil, as in G.
- **Z, "the curve on the bottom was incorrectly turned into a straight line."**
  - Measured, the underside is a wave: from the point it rises to a crest (about 15 px up, 80 px in), falls to its lowest under the right half, and rises into the curl.
  - Both earlier versions were wrong: the first flattened it into a line, the second only sagged. It now has the crest and the low point.
  - While there: the diagonal's right side had a bump where a middle node's handles had run to their limits. It is now one convex sweep, leaving the top-right curl's neck more steeply.
- **Y.2, "our own modern Y using the V as a model."** Built as proposed: V's arms and capped tops, meeting in a stem (armed weight) that comes down to a foot like the I's.
  - **How it is built.** It is the first glyph Pugin didn't draw. The build now supports such glyphs: a recipe names the letter it is `derived_from`, the glyph takes that letter's fitted measurements, and its own measurements take their starting values. It is checked, spaced and compiled like the rest, but not fitted.
  - **The joins.** Its arm-to-stem joins have their own handle lengths, so each turn sits at the stem and the arms run straight to their caps. With V's handles, the bend spread up the arm and dented the left one.
  - **Access.** It is reached through the stylistic set `ss02`; Q34 now asks about Y as well as M, T and W. The proof page shows it over Pugin's V, and has a specimen line with `ss01` and `ss02` on.
- **Results.** All 25 glyphs pass the outline checks. Means from Pugin's edges (shared): B 1.02, F 1.50, G 0.95, K 1.12, L 1.19, Q 1.01, uncial T 1.44, Z 1.98 px. A full rebuild took a minute.

## What changed
- **Created:**
  - `docs/brief/2026-10-28-lombardic-corrections-3.md`
  - `fonts/pugin-lombardic/recipes/Y_2.json`
- **Updated:**
  - `tools/type/letters.py`: B, F, G, K, L, Q, T.2, Z; Y.2; `trefoil_at`'s neck
  - `tools/type/construct.py`: the two-lobe part's unequal radii; `Params(fill=...)` for glyphs built from another's values
  - `tools/type/type.py`: derived glyphs in the build and on the proof page; the stylistic-set specimen
  - recipes, the UFO, the family README, `docs/roadmap.md`, `docs/open-questions.md` (Q34)

## Decided
- **Kept as Pugin drew it: P's spiral.** It ends in a trefoil like G's and the uncial T's but doesn't thin to a neck. Asked whether to thin it for consistency, Josh said: "Leave P's spiral as Pugin drew it."

## Open threads
- **Still to build:** M (both forms), W (both forms), the cross, the dot ornament.
- **Terminal sizes, family-wide** (Josh): L's crown is a new kind of lobe to include.
- **Kerning;** Q34 (defaults for M, T, W and now Y).
