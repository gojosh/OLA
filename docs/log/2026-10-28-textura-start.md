# 2026-10-28 — Pugin Textura: references, a simulated nib, the first letters

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction.** Josh: "Go with your proposal: build the plate 9 textura minuscule first, set it with Lombardic initials meanwhile, and give it plate 10's 15th-century capitals afterwards." Then: "As discussed prior, these will need to have plain versions, as well as these highly decorated versions." Recorded as decision 0011 (Q36 answered) and brief `2026-10-28-textura-start.md`.
- **The family** is `fonts/pugin-textura/`, with its own tools: `tools/type/textura.py` (extract, measure, build, proof), `tools/type/nib.py` (the pen), `tools/type/textura_letters.py` (the letters). It shares the shared code: ink separation from `type.py`, geometry, spacing, the UFO writer and the outline checks.
- **References for all 25 glyphs** (a–z without j, u and w; long s; an ampersand).
  - The letters run into each other through their flourishes, so they are separated by weight. An opening 13 px wide leaves the nib's strokes, whose larger pieces seed the letters (one box each). Every other piece of ink goes to the letter it is joined to by the shortest way along the ink (a watershed on the ink).
  - Checked on a contact sheet: every swash went to the letter it grows from.
- **Measurements.** x-height 205 px; ascenders 1.56 and descenders 0.52 of it; upright stems 33 px; the nib's edge at 45° (31 edges); so the nib is about 47 px wide; hairlines 8 px.
- **The nib** (`nib.py`): a stroke's outline is the path's Minkowski sum with a thin rectangular nib, computed exactly. Ribbons swept by each nib edge have the path's own curves, shifted, for sides; skia-pathops joins them; the outline is cleaned (single lines for straight runs, nodes at extremes, slivers merged, clockwise outlines).
  - Worked by hand first: one stroke (diagonal, down, diagonal) reproduced Pugin's i's diamond points within a couple of pixels.
  - Pugin's pen turns smoothly into and out of the stem, leaving hollows, so the minim's turns are curves.
- **Fitting** as for the Lombardic: each letter alone, shared values at the median, each letter refitted. The residuals are fixed in number whatever the outline's topology. A robust loss and an edge set limited to near the letter's body keep the flourishes from pulling the plain form.
- **Fixes along the way.**
  - The nib's measurements weren't registered at first, so the fit silently did nothing.
  - A following minim's head didn't reach the stem before it, so n and m came out in pieces. Now it starts against that stem, within a bound that keeps the heads touching, as Pugin's do.
  - Zero-length segments survived cleaning; nodes under a font unit apart collapsed on rounding.
  - skia-pathops failed on near-degenerate geometry: turns now have a minimum, slivers are skipped, and a union falls back to joining strokes one at a time on a 1/64 px grid.
- **Two proposals in the plain forms, for Josh to judge.**
  - **The l's top.** It forks: the head stroke, and a short spur up to the right. On the plate the spur runs on as a thick arm into a hairline loop. A long arm made the plain l read as a long s, so the plain form keeps only its start.
  - **A hairline stroke over the i.** In a textura spaced like Pugin's, "mini" and "minim" read as rows of identical minims and "li" as "h" without it. Scribes of the period marked i so; Pugin's plate 9 i has no mark. It is written with the pen but left out of the fit.
- **Spacing.** At first the spacing target was the mean side bearing, which l's overhanging arm skewed, and the letters set loose. A textura is spaced like a fence, so the target is now set to put two i's one minim's pitch apart, and the spacing module can take an explicit target. Clearance is checked over the whole height, so ascenders and arms never touch the next letter.
- **Results.** i, l, m, n pass the outline checks. Pugin's body edge sits 1.7, 8.1 (the arm the plain l omits), 2.2 and 1.7 px from them on average. The proof page (`/pugin-textura/proof/` on the font-proofs server) sets "Minim Nil Limn Mini Illi" under Lombardic initials, checked in the browser.

## What changed
- **Created:**
  - `tools/type/textura.py`, `tools/type/nib.py`, `tools/type/textura_letters.py`
  - `fonts/pugin-textura/` (`README.md`, `source.json`, `references/`, `measurements.json`, `recipes/`, `family.json`, `spacing.json`, `source/`)
  - `docs/decisions/0011-textura-capitals.md`, `docs/brief/2026-10-28-textura-start.md`, this log
- **Updated:**
  - `tools/type/spacing.py` (an explicit target; clearance over a taller zone)
  - `fonts/README.md`, `docs/decisions/README.md`, `docs/open-questions.md` (Q36 answered), `docs/roadmap.md`

## Open threads
- The other plain letters: the round and broken letters (c, e, o), the bowls (a, b, d, g, p, q), the ascenders (b, d, h, k, t, ſ), the descenders (g, p, q, y), and the rest.
- The hairline exits Pugin's pen leaves at the feet belong to the plain letters; not yet built.
- The flourished alternates, and how they are reached (stylistic set, `swsh`, or contextual): Josh's call once some can be seen.
- Plate 10's capitals (decision 0011).
- The shared values are provisional with four letters: the head's angle settled at 31° against 43° measured, and the minims' join sits at its bound.
