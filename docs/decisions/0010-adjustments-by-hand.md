# 0010 — Adjustments by hand: recorded moves on top of the construction

- **Status:** accepted
- **Date:** 2026-10-28
- **Decided by:** Josh Goforth

## Context
Josh wants to make the final tweaks himself, by dragging handles on the proof page, and asked how best to handle them and fold them into the build ([brief](../brief/2026-10-28-manual-adjustments.md)). The font source (UFO) is generated from the recipes on every build, so changes made in the UFO would be lost. Decision 0008 already asks that per-glyph corrections be "kept as recorded changes, so a rebuild doesn't erase them".

## Decision
Josh: "Accept decision 0010: final tweaks are recorded point moves made on the proof page and applied by the build."

- **What a tweak is.** A move of one control point (a node or a handle), recorded relative to the construction, in plate pixels. Each move names the node of the segment it belongs to.
- **Where tweaks live.** In `fonts/<family>/adjustments/<glyph>.json`, in the repository, alongside the recipes.
- **Where they are made.** On the proof page, served by `tools/type/type.py serve` (the `font-proofs` entry in `.claude/launch.json`). The editor keeps the outline rules:
  - a node carries its handles;
  - a smooth node's other handle turns to stay in line;
  - a handle at an extreme keeps its direction (Alt frees it);
  - mirrored letters stay mirrored, with their axis nodes on the axis;
  - lines stay lines.

  The arrow keys nudge by one font unit. Save writes the file; Save and rebuild also runs the build and reloads the page.
- **How the build uses them.** It applies the moves after fitting, by the same rules (`construct.adjust`), then runs the usual outline checks. A move whose node no longer matches (the construction changed) is skipped and reported, never misapplied.
- **When to use something else.** A tweak that is really about a measurement (a stem's weight, a curl's angle, a terminal's size) goes in the recipe's `corrections`, which stay coherent through refits. Point moves are for final optical touches.
- **The last mile.** Hinting, kerning and any final optical pass in a font editor happen once the family is frozen. At that point the UFO becomes the source of truth and these tools stop regenerating it (Q32).

## Consequences
- Tweaks survive rebuilds and refits, are reviewable in git, and can be undone by deleting a file.
- A construction change can orphan tweaks. The build says which, so they can be redone.
- Tweaks are not fitted to Pugin's letter. The proof page still shows how far the tweaked outline is from his edge.
