# 0008 — How the Pugin fonts are made

- **Status:** accepted
- **Date:** 2026-10-28
- **Decided by:** Josh Goforth

## Context
With the alphabet plates flattened and evened (`tools/flatten`), Josh asked how to make "ultra-high quality Pugin fonts" with "clean refined lines everywhere". His questions ([brief](../brief/2026-10-28-fonts-kickoff.md)) were how to handle antiquated forms, how to treat repeated shape primitives, and how to use bespoke software. The approach below was proposed in reply. Josh: "Outstanding approach. Completely agree. Let's start with the harder of the two - Lombardic."

## Decision
- **The plates are references, not sources.** Glyphs are rebuilt from clean construction and checked against the plates; they are never traced and cleaned up.
- **The target is a regularized revival.** Pugin's proportions and details stay; hand wobble and lithographic noise are averaged out. Optical adjustments for screens are allowed.
- **Primitives are a construction system.**
  - Repeated parts (terminals, cusps, trefoils, stems, bowls) are measured across every instance, averaged, and fitted with clean curves.
  - Glyphs are recipes that place those primitives.
  - Per-glyph optical corrections are kept as recorded changes, so a rebuild doesn't erase them.
  - Textura is built from a simulated broad nib. Lombardic uses components for terminals and fitted curves for bowls.
- **Antiquated forms** are both encoded characters and alternates (for example ſ, ꝛ, ⁊). Default text stays readable; historical behavior is switched on through stylistic sets that follow the scribal rules. Flourished forms are base letter plus flourish, so plain forms come from the same parts.
- **Bespoke tooling** lives in the repository:
  - glyph extraction and ink separation
  - measurement
  - primitive mining and averaging
  - a construction kit that generates font sources
  - proof pages regenerated on every build, including overlays against the plates
  - automated quality checks

  The fonts' source of truth is text in the repository, in an open font source format. Taste stays human.
- **First alphabet:** the Lombardic capitals of plate 9.

## Consequences
- Fonts live in `fonts/<family>/`, with references, measurements, primitives, sources, and proofs. Tools live in `tools/type/`.
- Glyphs Pugin never drew (J, numerals, punctuation, accented letters) will be drafted in his idiom as proposals for Josh's judgment.
- Still to decide (open questions): intended uses, editors and whether a type designer does final passes, license and names, and default forms where Pugin gives alternates.
