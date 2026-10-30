# 0015 — The textura's x is a modern x; Pugin's archaic x is an alternate

- **Status:** accepted
- **Date:** 2026-10-30
- **Decided by:** Josh Goforth

## Context
Pugin's x on plate 9 is the archaic form: a stem with a head running down past the baseline into a tail, a flag at the top right and a short stroke down to the right from the middle. Few readers today will take it for an x. Josh asked for "a modern x? Something along these lines, but of course matching all of our style, widths, etc.", with a textura x as the example ([brief](../brief/2026-10-30-textura-x-z.md)). It was built as an alternate under `ss04`, and the default was asked (Q42).

## Decision
Josh: "Yes, modern default" ([brief](../brief/2026-10-30-textura-x-default.md)).

- **The x is the modern one** (`textura_letters.x_modern`, the glyph `x`): two strokes crossing between where n's two stems stand, the thick one from n's first head to n's second foot, the thin one a hairline from a head at the upper right to a foot at the lower left. A proposal in Pugin's idiom (decision 0008), built from n's fitted measurements; Pugin drew no modern x.
- **Pugin's x is `x.archaic`,** reached through the stylistic set `ss04` ("Archaic x"), spaced and kerned in its own right. It is Josh's drawing over Pugin's (decision 0014).
- **Names.** Pugin's x keeps its reference, recipe and fit under `x.archaic` (`source.json`, `references/x.archaic.png`, `recipes/x.archaic.json`); the build's `x` is the modern x. A letter built as the others are that stands beside another is named in `BUILT_ALTERNATES`.

## Consequences
- In running text every x is the modern one. `ss04` sets Pugin's, also with `ss01` on.
- The modern x has a spur on its foot, so `ss01` drops it (`x.nospur`); the archaic x's spur is part of Josh's drawing.
- The modern x is spaced with the letters, in their joint fit, and the archaic x after them, on its own. The switch moved the other letters' side bearings by up to 2 units and changed 90 kerning pairs not involving an x, most by 5 units.
- Pugin's other archaic forms (the long s, ſ) are separate letters, not alternates, and are untouched.
