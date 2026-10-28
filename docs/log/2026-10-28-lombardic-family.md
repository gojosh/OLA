# 2026-10-28 — Lombardic E, F, L and T, fitted together

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh: "Build the next letters that share the I's parts (L, E, F, T), fitted together so the stem and curl settle to shared values." Partway through: "We should probably improve the two lobe and three lobe stems - some of them look quite sloppy in Pugin's original, FYI."
- **What the plate's forms turned out to be.**
  - **T** (the straight form, T.1) and **L** share the I's stem, bars and curls, and add tapering arms.
  - **E** is the uncial form: a round bowl closed by a right stroke, with notches top and bottom. It shares only the curls.
  - **F** has a closed upper counter and a trefoil.

  The roadmap's earlier grouping of E with the stem letters was wrong; it is fixed.
- **One kit, one fit.**
  - `tools/type/construct.py` now holds the parts:
    - cubics with tensions that keep each curve within its nodes;
    - circular arcs split at their extremes;
    - the curl placed in any orientation, including turned to the foot of a stroke;
    - a round knob;
    - the trefoil.
  - `tools/type/letters.py` holds one construction per letter, each naming its measurements with starting values and bounds.
  - `fit_letters` fits all the letters in one solve. One stem width, one curl size and one trefoil are shared by every letter; everything else is per letter.
- **Each letter is also fitted alone**, with its own stem, curl and trefoil, to show where Pugin's letters disagree:

  | | stem (px) | curl | mean from Pugin alone | sharing |
  |---|---|---|---|---|
  | E | — | 0.93 | 0.82 | 0.79 |
  | F | 70.8 | 0.93 | 1.30 | 1.62 |
  | I | 79.6 | 1.01 | 0.89 | 1.00 |
  | L | 80.3 | 1.05 | 1.51 | 1.66 |
  | T | 74.8 | 0.87 | 1.89 | 2.08 |
  | **Shared** | **77.7** | **0.975** | | |

  Pugin's stems run from 71 to 80 px. Sharing costs F the most, because his F is the lightest.
- **Lobed terminals, per Josh's note.**
  - **The trefoil** is drawn as three equal round lobes on the arms of a cross: the tip on its axis, one lobe at each side square to it. It is the same wherever it is placed. Its arcs are split at their extremes after placing, so nodes stay at extremes whatever way it faces. Sized from F for now: lobe radius 17.5 px, 22.4 px from the centre. Pugin's (B, F, G) share the cross layout but vary freely.
  - **L's top-right terminal** looks two-lobed but is a single curl drawn lumpily. It is built as the alphabet's curl.
  - **The genuine two-lobe terminal** (a curl with a second ball, on H) is not in these letters; it comes with H.
- **Nodes at extremes, enforced.**
  - The fit penalizes any curve that swells past its nodes.
  - Each place where it wanted to swell turned out to be a real extreme that needed a node: F's top edge sags, F's right stroke narrows above the trefoil, the underside of E's middle bar rises to the left, and T's arms have a narrowest point.
  - A free heading within 2° of flat or upright is snapped to it.
  - All five letters pass the checks.
- **Fixes along the way.**
  - Arcs change segment count as they turn, so the fit samples a fixed number of points per contour.
  - The default finite-difference step was far below a pixel, so the fit stalled; steps are now about a tenth of a pixel, with restarts.
  - Compass headings now come out exactly flat or upright, instead of a float hair off.
  - The extremes fitter's wrap-around split could recurse forever; fixed.
- **The draft font** now has E, F, I, L and T (the straight T provisionally on the T key, Q34). The proof page opens with the shared values, the per-letter table, and words set in the font (LIFE, FILET, TILE, LEFT, FELT, FILLET), then each letter over Pugin's.

- **Josh's corrections** (verbatim in `docs/brief/2026-10-28-lombardic-corrections.md`), each traced and fixed in the constructions:
  - **L, top: "the curves aren't tangent where the stems meet the top."**
    - Cause: the joins were mathematically tangent, but the fit had left a stub of a handle (tension 0.05) where each top edge leaves its ball, and had fitted the two sides of the top differently (one flare leaving its neck at 40°, the other near flat). A curve that turns that fast at a smooth node reads as a kink.
    - Fix: L's top is symmetric about the stem; each top edge has a node where it is steepest; and, for every letter, no handle is shorter than a fifth of its reach.
  - **L, foot: "a rounded point, not a sharp point."** The foot of the arm is now a small arc (8.4 px radius), met tangentially by the arm's outside and the base's underside.
  - **F: a sharp point at the top right of the lower counter.** The stroke's inside now climbs from the trefoil to a corner under the middle bar.
    - It leaves the lower lobe no further round than the lobe's leftmost point, so the edge doesn't swing out and back.
  - **T: "too close together."** Pugin leaves 16.3 px of clear space between each arm's curl and the foot's curl (his left arm; his right is tighter). The construction placed the alphabet's curl, which is larger than his there, only 7 px clear. The arm curl is now positioned from that clear space, with Pugin's 16.3 px as the minimum. The fit holds it at the minimum.
  - **New bounds:** the extra nodes and bounds came with a few new limits so curves can't swell past them (F's point, E's upper counter).
  - **A lesson about the fit.** With T's arm curl moved up, the first full build failed T's outline check while a test run had passed. The build fits the letters in a different order, which landed on a slightly different solution in which the arm's "narrowest point" fell left of the curl's neck. The node is now placed relative to the neck, so it can't fall on the wrong side whatever the solve does.
    - Where a node's role depends on where it sits relative to another (an extreme must be the furthest point), place it relative to that node rather than relying on the penalty.
    - The build reports FAIL when a check fails, and that is what caught this one.

## What changed
- **Created:**
  - `tools/type/letters.py`
  - `fonts/pugin-lombardic/family.json`
  - `fonts/pugin-lombardic/recipes/E.json`, `F.json`, `L.json`, `T_1.json`
  - `docs/brief/2026-10-28-lombardic-corrections.md`
- **Rewritten:** `tools/type/construct.py` (the parts, the joint fit, multi-contour checks and font output).
- **Updated:**
  - `tools/type/type.py` (build and proof)
  - `tools/type/geom.py` (recursion fix)
  - `recipes/I.json`
  - the UFO source
  - the family README, `fonts/README.md`, `docs/roadmap.md`, `docs/open-questions.md` (Q34 note)

## Open threads
- **Stem weight.** One shared stem (77.7 px) makes F and T heavier than Pugin drew them. That is the regularization Josh asked for; if he prefers Pugin's lighter F and T, the stem can be shared per class instead.
- **Curls that differ from the family curl.** T's arm-end curls, F's bottom-right curl and L's arm terminal are larger in Pugin's drawing. These are the largest remaining differences, up to 21 px at worst (T's, since its arm curls are now held at Pugin's clear space from the foot curls).
- **The trefoil** is sized from one instance. Refit it when B, G, P, R and the uncial T are built.
- **Spacing** is a flat 50 units a side; the words on the proof show it needs doing.
- **Next letters:** H (with the two-lobe terminal), K, and the round letters C, D, O, Q, which can use E's bowl.
