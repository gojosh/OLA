# Fonts

Revivals of A. W. N. Pugin's alphabets from the *Glossary of Ecclesiastical Ornament* (1844). The method is set out in decision [0008](../docs/decisions/0008-font-approach.md):
- The flattened plates are references, never sources.
- Glyphs are rebuilt from measured, averaged primitives and checked against the plates.
- The tools live in [`tools/type`](../tools/type/type.py): `type.py` runs the steps, `construct.py` is the construction kit and the joint fit, `letters.py` holds one construction per letter, and `geom.py` the curve geometry. `spacing.py` spaces and kerns both families. The textura has its own: `textura.py` runs its steps, `nib.py` is the simulated broad nib, and `textura_letters.py` holds its letters. The plates are flattened by [`tools/flatten`](../tools/flatten/README.md).
- Recipes are the source of truth for glyphs. The UFO in each family's `source/` is generated from them, so the fonts open in any editor that reads UFO (Glyphs, FontLab, RoboFont).

The plates' dates are Pugin's own, from the Glossary's entry Inscriptions (see [`reference/pugin-glossary`](../reference/pugin-glossary/README.md#the-alphabet-plates-in-pugins-words)). The plate numbers here are the file numbers; the book's are one higher.

| Family | Source | State |
|---|---|---|
| [`pugin-lombardic/`](pugin-lombardic/README.md) | Plate 9, the capitals (13th–14th centuries) | All 31 glyphs on the plate built, spaced and kerned in a draft font |
| [`pugin-textura/`](pugin-textura/README.md) | Plate 9, the small alphabet (late 15th century) | References for all 25 glyphs; a simulated broad nib; all 24 plain letters on the plate fitted, spaced, kerned and compiled, with proposed u, w and j. Lombardic initials meanwhile; plate 10's capitals afterwards (decision 0011). |
| Gothic capitals | Plate 10, the large capitals (15th century) | Not started |
| Lombardic, small | Plate 10, the small capitals (earlier) | Not started |
| Black letter | Plates 11–12, three minuscules and one set of capitals (16th century) | Not started |
| Ornaments | Plates 9–12 and others | Not started |

Names and licenses are undecided (Q33).
