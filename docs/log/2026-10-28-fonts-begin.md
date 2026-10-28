# 2026-10-28 — Font creation begins: Pugin Lombardic

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh opened font creation: how to build "ultra-high quality Pugin fonts" with "clean refined lines everywhere", handle antiquated forms as contextual alternates, use repeating primitives, and use bespoke software. Brief: `docs/brief/2026-10-28-fonts-kickoff.md`.
- **The approach**, proposed and accepted ("Outstanding approach. Completely agree."), recorded as decision 0008:
  - the plates are references, never sources;
  - the target is a regularized revival;
  - primitives are averaged across every instance and fitted with clean curves, and glyphs are recipes built from them, with per-glyph corrections kept separately;
  - historical forms are encoded characters plus opt-in alternates;
  - the tooling lives in the repository.
- **First family.** Josh chose the Lombardic capitals of plate 9 ("the harder of the two").
- **`tools/type/type.py`** has four commands:
  - `extract`: cuts each glyph from the flattened, evened plate. Each pixel is unmixed into paper plus pure red or blue ink, giving sub-pixel coverage. Neighbors separate cleanly because the plate alternates red and blue.
  - `measure`: stroke widths from summed coverage along scanlines.
  - `curls`: finds a primitive in four orientations, with a range of rotations and sizes, then aligns, normalizes, averages, and fits Béziers.
  - `proof`: a self-contained proof page.
- **References.** 30 glyphs: the cross, A–Z without J, U and V both, and alternates for M, T and W, plus a dot ornament.
- **Proportions.**

  | Measure | Median | Ratio |
  |---|---|---|
  | Height with curls | 427 px | |
  | Stem | 70.6 px | |
  | Bowl | 93.2 px | 1.32 × stem |
  | Hairline | 32.0 px | 0.45 × stem |

- **The curl terminal.** 71 instances in 22 glyphs. The consensus is fitted with 11 cubic segments, within 0.29 px on average.
- **Fixes along the way.**
  - Blue ink was first misread as black.
  - Candidates were centered inconsistently, and rotation was undone the wrong way for mirrored candidates.
  - The first template included too much of the stem, so only 24 curls were found.
- **Viewing.** Proof pages are served by a new `font-proofs` entry in `.claude/launch.json`, because the app's browser wouldn't open the 1 MB file directly.

## What changed
- **Created:**
  - `docs/brief/2026-10-28-fonts-kickoff.md`
  - `docs/decisions/0008-font-approach.md`
  - `fonts/README.md`
  - `fonts/pugin-lombardic/`: `README.md`, `source.json`, `references/`, `measurements.json`, `primitives/`
  - `tools/type/type.py`
- **Updated:** `.gitignore` (proof pages), `.claude/launch.json`, `AGENTS.md` (repository map), `docs/decisions/README.md`, `docs/roadmap.md`, `docs/open-questions.md` (Q31–Q34).

## Open threads
- **Node placement.** Fitted outlines should put nodes at curve extremes with horizontal and vertical tangents, as type designers do. This applies to the curl and every later primitive.
- **More primitives:** the trefoil (B, F, G, P, R, rounded T), the cross's larger curl, G's hooked terminal, the crescent bowl, the waisted stem, and hairline joins.
- **Construction kit.** Glyph recipes from primitives, then the first glyph (I is the simplest: a stem, two bars, four curls), checked against the plate by overlay.
- **Q31–Q34** for Josh: uses, editors and a type designer, names and licenses, and the Lombardic defaults for M, T and W.
