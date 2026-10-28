# Fonts

Revivals of A. W. N. Pugin's alphabets from the *Glossary of Ecclesiastical Ornament* (1844). The method is set out in decision [0008](../docs/decisions/0008-font-approach.md):
- The flattened plates are references, never sources.
- Glyphs are rebuilt from measured, averaged primitives and checked against the plates.
- The tools live in [`tools/type`](../tools/type/type.py): `type.py` runs the steps, `construct.py` is the construction kit and the joint fit, `letters.py` holds one construction per letter, and `geom.py` the curve geometry. The plates are flattened by [`tools/flatten`](../tools/flatten/README.md).
- Recipes are the source of truth for glyphs. The UFO in each family's `source/` is generated from them, so the fonts open in any editor that reads UFO (Glyphs, FontLab, RoboFont).

| Family | Source | State |
|---|---|---|
| [`pugin-lombardic/`](pugin-lombardic/README.md) | Plate 9, capitals | E, F, I, L and T built from shared parts (stem, curl, trefoil) and compiled into a draft font |
| Textura | Plates 11–12 | Not started |
| Flourished lowercase | Plate 9 | Not started |
| Ornaments | Plates 9–12 and others | Not started |

Names and licenses are undecided (Q33).
