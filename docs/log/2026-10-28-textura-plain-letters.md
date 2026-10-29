# 2026-10-28 — Pugin Textura: all the plain letters

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- **The direction.** Josh: "Keep the i stroke and the short l spur, and continue with the other plain letters." Both proposals are now marked kept in the family README.
- **Studied every remaining letter** at full resolution, with its heavy body tinted, deciding for each what is structure (kept in the plain form) and what is flourish (left to the alternates):
  - d's arm leaning back over its bowl is structure; the ball at its end is flourish.
  - ſ's top arm, left spur and tail are structure.
  - c, e, r and s hang a hairline and ball off their arms, which is flourish; e keeps its hairline, which closes the eye.
  - Swashes and loops on b, f, h, p, q, x, y and z are flourish.
- **What the study found.**
  - The o is two strokes: a flat-topped stem on the left that turns out at the foot, and a stroke on the right whose long head starts inside the left one and which stops with the nib's cut, in line with that foot. One stroke makes both the peaked top and the counter's sloping top. v, q and g are built the same way.
  - y and z sit on a second line squeezed to about 0.7 of the first's height, with the same pen. Their plain forms stand at the full x-height; only their comparison with Pugin's is squeezed (a `fit_affine` on the construction).
- **The kit grew** (`textura_letters.py`): minim variants (a given head or none, a stroke that stops without a foot, stems to the ascender and descender lines), free strokes of the pen through named points and headings, the forked ascender, the broken bowl, and the second-line squeeze.
- **All 24 letters on the plate built:** a b c d e f g h i k l m n o p q r ſ s t v x y z. All pass the outline checks. Means from Pugin's body edge: o 1.5, t 1.8, i 2.0, n 2.2, ſ 2.4, a 2.4, k 2.4, v 2.5, m 2.8, c 3.4, d 3.9, e 4.5, y 4.8, x 4.9, g 5.4, r 5.4, h 5.5, s 5.5, l 7.9, z 9.4, b 9.5, q 12, p 27 and f 32 px. The large ones are his flourishes, which count as body and which the plain forms leave out on purpose; z is genuinely the weakest.
- **Fixes along the way.**
  - My starting positions for several letters were 15–40 px off (b's stem by 34 px, f's by 40). Each letter's stems are now measured from its reference, and the saved fits were cleared so the new starts took effect.
  - z's top bar ran almost along the nib's angle and came out a hairline. Now it runs near level, which the pen makes thick.
  - skia-pathops failed on geometry the fit wandered into, even in its fallback. The fallback now cleans each stroke alone and retries with points nudged a thousandth of a pixel; during the fit, a union that can't be settled counts as a bad fit.
  - Rounding to font units collapsed slivers and left handles a degree off level. Outlines are now tidied after rounding (`nib.tidy_units`).
- **c and r.** In the specimen, "Ecce ancilla" read "Erre anrilla". A longer arm didn't help. Pugin's own pair shows why: his c's head stroke carries on past the stem as one wedge across the whole top, while his r has an ordinary head plus a small flag set apart by a notch. Rebuilt that way, c and r are distinct.
- **The proof page** sets "Kyrie eleison, Christe eleison, Gloria patri, Ave maris stella, Ecce ancilla domini, Fiat mihi, Pater noster, Salve regina" under Lombardic initials, chosen from phrases without u, j or w. Checked in the browser.
- **Spacing:** fence spacing (two i's one minim's pitch apart), 459 kerned pairs, nothing closer than the clearance over the whole height.
- **A note on briefs.** I appended Josh's reply to this session's brief by mistake and reverted it: briefs are verbatim and never edited. His words are recorded here instead.

## What changed
- **Updated:**
  - `tools/type/textura_letters.py` (the kit and all 24 letters)
  - `tools/type/textura.py` (the second-line squeeze, softer fit failures, tidying after rounding, the proof's phrases)
  - `tools/type/nib.py` (a sturdier union, `tidy_units`)
  - `fonts/pugin-textura/` (recipes, family, spacing, the UFO, the README)
  - `fonts/README.md`, `docs/roadmap.md`
- **Created:** this log

## Open threads
- **u, w and j:** Pugin drew none. Draft them in his idiom as proposals (u as two minims joined at the foot), so ordinary text can be set; until then the proof avoids them.
- **The ampersand:** Pugin's is all hairline; it needs a plain form.
- **The hairline exits** Pugin's pen leaves at the feet.
- **z's lower bowl** wants another pass.
- **Medieval use of ſ and s** (ſ inside a word, s at its end) belongs in a stylistic set (decision 0008).
- **The flourished alternates,** and how they are reached (Josh's call once some can be seen).
- **Build caching:** every textura build refits all 24 letters (about a minute). Fingerprint-based caching like the Lombardic's would make small changes quicker.
