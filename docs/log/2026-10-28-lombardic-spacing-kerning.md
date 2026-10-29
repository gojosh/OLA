# 2026-10-28 — Lombardic: tighter spacing, and kerning

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The request.** Josh: "Great. Now, let's get the spacing tighter, and handle the common kerning cases." Brief: `docs/brief/2026-10-28-spacing-and-kerning.md`.
- **What was wrong with the first pass.** It set each letter's side bearings alone, as if its neighbour had a flat side. Nearly every Lombardic capital has curls at its corners, so that assumption fails. A round side beside a curled one (I–E, O–I, L–O) set loose, and open shapes left holes (P–A, T–A, Z–O).
- **The new method** (`tools/type/spacing.py`): spacing is judged a pair at a time.
  - **A pair's white.** On each line from the baseline to the cap height, the build measures the gap between the left letter's right edge and the right letter's left edge. It counts each gap no further than 200 units beyond the pair's closest approach, so a deep bay reads about as open as a shallow one, and takes the mean.
  - **Side bearings** are fitted so that every pair of letters (841 of them, alternates included) comes as near as it can to one target white. The fit is robust (Huber), so the few pairs far off, which kerning takes care of, don't drag the rest. Symmetric letters keep equal side bearings.
  - **How tight** is one setting: the side bearing a letter carries on average, both sides together. The first pass averaged about 103 units; it is now 60. Compared by eye on liturgical lines at 75, 60 and 45. At 45, curls on neighbouring letters start to crowd (E–L–E, T–S).
  - **Kerning.** Pairs the side bearings leave more than 15 units off the target are kerned to it, in steps of 5. No pair comes closer than 30 units at its closest approach, so curls never touch.
  - **The cross and the ornament** take the letters' median side bearing and no kerning.
  - **The word space** is 200 units (was 250).
- **How the depth was chosen.** Fits at depths of 120, 200 and 300 units, with the same tightness, were compared on test words.
  - At 120 the side bearings explain the pairs least well: 551 pairs needed kerning, Q–V as much as −150.
  - At 300 the method approaches plain area, which crowds round letters against T and D.
  - 200 sets evenly and needs about 400 pairs.
- **Checked in HarfBuzz:** the compiled kerning is applied as computed, including to the uncial forms under `ss01` and the modern Y under `ss02`.
- **The proof page** sets its specimen with kerning, then again without, for comparison. Its CSS had added 0.3 em to every word space; that is gone, so the page shows the font's own word space.
- **Also fixed:** `type.py space` failed after the fit caches were added to `build/`; it now reads only the glyph reports.
- **Results.** All 31 glyphs pass the outline checks; none of Josh's moves went stale. A letter now carries 63 units of side bearing on average (was about 103). 400 pairs are kerned.
  - **186 closed** (median 30 units, up to 125): round letters into the open middles of Z, X and the modern Y, and round sides beside curled corners (I–E, O–I, R–V).
  - **214 opened** (median 20, up to 70): diagonals beside diagonals (V–V, W–Y), whose capped tops would otherwise meet given the diagonals' negative side bearings; and round sides facing each other (D–O, O–C), which side bearings set for round-beside-straight leave too close.
  - The clearance floor didn't have to act on any pair at this setting; it stays as a guarantee.

## What changed
- **Created:**
  - `tools/type/spacing.py`
  - `docs/brief/2026-10-28-spacing-and-kerning.md`
  - this log
- **Updated:**
  - `tools/type/type.py` (`write_font` spaces and kerns by pairs; `space` fixed; the proof page)
  - `tools/type/construct.py` (the old per-letter spacing moved out; `write_ufo` writes kerning)
  - `fonts/pugin-lombardic/source.json` (`spacing`)
  - `spacing.json` (side bearings, the target and every kerned pair), the UFO, the family README, `docs/roadmap.md`
- Moving code out of `construct.py` changed every letter's fit fingerprint, so this build refitted them all. The outlines are unchanged.

## Open threads
- Judge the spacing on the proof page; `mean_side_bearings` and `depth` in `source.json` are the two settings to turn, and `type.py space` applies them in a second.
- Punctuation and figures aren't drawn yet, so they aren't kerned.
- The terminal-size pass (Josh) will change some outlines; spacing and kerning follow automatically.
