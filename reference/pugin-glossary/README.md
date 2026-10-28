# Pugin — *Glossary of Ecclesiastical Ornament and Costume*

A. W. N. Pugin's *Glossary of Ecclesiastical Ornament and Costume* (first edition 1844) is a dictionary of liturgical ornament illustrated with chromolithographed plates. Pugin died in 1852; the work is in the public domain.

These are **photographs of a physical copy** (the book is visible in its cradle). ⚑ Josh: whose copy, which edition, and is any attribution owed? See `docs/open-questions.md` Q19.

## Files

| Path | What |
|---|---|
| `plates/` | Originals: 74 × JPEG 2000 (`.jp2`) + 1 × HEIC, 3744×5616 px. Most tools and browsers can't open these. |
| `previews/` | The same plates as 1200 px JPEGs (~200 KB each). **Agents: look at these.** |
| `contact-sheet.jpg` | All 75 plates on one numbered sheet. Fastest way to see the whole set. |

Regenerate previews (macOS):
```bash
cd reference/pugin-glossary && for f in plates/*; do b=$(basename "$f"); sips -Z 1200 -s format jpeg -s formatOptions 70 "$f" --out "previews/${b%.*}.jpg"; done
```

## Catalog

Plate numbers match the filename prefixes.

| Plates | Subject | Notes for this project |
|---|---|---|
| 01–02 | Forms and sizes of the sacred vestments | Vestment shapes and proportions |
| 03 | English priests from monumental effigies | Specifically English medieval vesture |
| 04 | French and Flemish priests | |
| 05–06 | Various ministers; various bishops | |
| 07 | Frontals for altars | The altar dressed for the day: precedent for a site "vested" by the calendar |
| 08 | Principal figures of shapes | Geometric figures underlying the ornament |
| 09–12 | Alphabets | Lombardic capitals and textura: initials and display lettering |
| 13–14 | Crosses for marking church linen | Small marks, possible icon vocabulary |
| 15–16 | Borders for altar cloths | Section edges and rules |
| 17 | Crockets for stencilling, stained glass and embroidery | |
| 18 | Borderers | Running bands |
| 19 | Crowns and cresting | Top edges; headers |
| 20–22 | Patterns for powderings | Scattered motifs on a field: quiet backgrounds |
| 23–29 | Patterns for diapering (29 from the choir of Cologne Cathedral) | Allover lattices. 23 is AVE + MR on blue, green, and gold: Marian |
| 30–33 | Apparels for albs | |
| 34–39 | Patterns for stoles and maniples | Narrow bands: dividers, side rails |
| 40–46 | Orphreys of copes | Vertical bands with figures in niches |
| 47–50 | Hoods of copes | Shield-shaped compositions |
| 51–56 | Crosses | |
| 57–58 | Monogram of the Holy Name (IHS) | |
| 59–60 | Monogram of Our Blessed Lady's name | Marian monograms: directly relevant to the parish's title |
| 61 | Emblem of the Holy Trinity | |
| 62 | The Rosary | |
| 63 | Various emblems | |
| 64 | Emblem of the Four Evangelists | |
| 65 | The Five Wounds of Our Lord | Passiontide / Holy Week |
| 66–67 | Emblems of Our Lord's Passion | Lent; pairs naturally with Lenten array |
| 68–69 | Conventional forms of animals; of lions | Heraldic beasts |
| 70 | Various specimens of the nimbus | |
| 71 | Examples of precious mitres | |
| 72–73 | An altar; an open altar | |
| 74 | Funeral palls | Requiem / All Souls |
| 75 | The End | Colophon |

## Observations

- **The palette is bright, flat, and heraldic:** vermilion, ultramarine, emerald, gold, and black on cream. Nothing like the muddy "olde" palette of the AI-image concepts.
- **The plates form a systematic grammar** (powdering, diapering, borders, orphreys, cresting, monograms, alphabets). See `docs/foundations/03-aesthetic.md` §4 for how each might map onto web structure.
