# 2026-10-29 — Pugin Textura: h's and k's joins, and the Finder's preview

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **Save and rebuild with the split top's settings.** Josh asked for the rebuild after tuning the notch to 15.5 px in the new panel. He had already run Save and rebuild from the panel, and the rebuild matched it exactly.
- **The Finder's preview** (brief `2026-10-29-textura-h-k-joins.md`). Josh: "for Textura, the font preview in the Finder only shows a and b, while the lombards font shows the whole alphabet?"
  - **Seen with `qlmanage`:** Quick Look's preview of the textura was a 44 × 90 px "ab"; the Lombardic's was its capitals on two lines.
  - **Found by testing copies of the font:**
    - mapping the capitals or the figures onto the lowercase letters brought the full sample back;
    - one figure didn't; a sample-text name (name ID 19) didn't;
    - Core Text's list of supported languages didn't explain it (the Lombardic's is empty too).
  - macOS decides what sample to show from the characters a font has. A font with lowercase letters only, no capitals and no figures, gets its first two letters.
  - **The fix:** the font now says outright that it is for the Latin script, in a `meta` table (`dlng`, `slng`: `Latn`), written into the UFO as `public.openTypeMeta` (`textura.py`, `write_font`). Quick Look now shows the whole lowercase alphabet on two lines. No glyph changed.
  - The Finder may keep its old preview of the file until the file is rebuilt or the Finder is reopened.
- **h's and k's joins** (same brief). Josh: "h and k need the same connecting spur we added to m and n, and k needs the bottom of the k bowl to fully connect into the stem, and the lower k stem to fully connect with the bowl."
  - **The hairline join** (`join_from`, now shared with `minim`'s `after`): the pen comes up from the stem along the nib's own edge to where the next stroke starts. The h's leg head and the k's loop now have it, as n's and m's second minims do.
  - **k's bowl into the stem** (`into_stem`): the loop's lower stroke runs on along its own heading at its end until it ends on the stem's centre line, so its end is buried in the stem. It meets the stem between 3406 and 3433 px; Pugin's meets it between about 3405 and 3430.
  - **k's leg out of the bowl** (`head_to_meet`): the leg's head starts back along its own diagonal (`minim`'s `lead`, as b's bowl does) until the lower corner of its cut is half a hairline inside the lower stroke's lower edge. The wedge of white between them is gone; the k is one piece with its counter (2 contours, from 3).
  - **Nothing fitted.** The new joins are derived from each letter's measurements, so the build ran with `--fit none`.
  - **What changed:** only h and k changed shape (with their forms without spurs), and one kerning pair, g k, went from 40 to 35. All 27 pass.
  - **Against Pugin:** the h measures 6.72 px from his edge (from 6.75) and the k 3.14 (from 2.84). The references of his letters' bodies have his thin joins cut away, so a joined k measures a little further from them. Compared by eye with his full ink, the joins are where his are.
  - **Checked:** in the browser (cards and the stroke editor, with the proof server restarted) and set large in words (`nhkn`, "the kingdom which hath no end").

## What changed
- **Created:** `docs/brief/2026-10-29-textura-h-k-joins.md`, this log
- **Updated:**
  - `tools/type/textura_letters.py` (`join_from`, `into_stem`, `head_to_meet`; h, k; `minim` uses `join_from`)
  - `tools/type/textura.py` (the `meta` table)
  - `fonts/pugin-textura/` (the UFO, h and k; spacing's one pair; the README)

## Settled
- **The h's join is lower than Pugin's.** His hairline leaves the stem at about 3345–3352 px, flatter than the nib's 45° edge; ours, along the nib's edge, leaves it about 19 px lower. Asked whether to raise it, Josh: "Leave the h's join as it is." So it stays along the nib's edge, as n's and m's do.
