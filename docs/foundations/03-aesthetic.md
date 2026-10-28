---
title: Aesthetic — English-Catholic
status: draft
updated: 2026-10-27
---

# Aesthetic: English-Catholic

## What Josh has said

- **"English-Catholic"**, used precisely: "our heritage is not just Anglican which has been welcomed back into the Catholic Church… We're grounding into the English Catholic tradition, reconnecting to the church that existed prior to Henry the VIII's devastation to the Catholic faith in England."
- "That means tying to the medieval, in a thread of continuity to the present. **Continuity will be a key word here.**"
- "We are richly drawing on the whole catholic tradition, but with a particularly English focus."
- "**Gothic** is our architectural inheritance, and we relish it."
- "**Pugin** represents a particularly vibrant touchstone… fully English, deeply Gothic, devout convert back into the Catholic faith — he looms large in our aesthetic landscape."
- "But we are also deeply **American**. What might be **American Gothic**? That's a question that hangs in my imagination, waiting to manifest."
- The early AI-image concepts (`explorations/ai-image-concepts/`) "DO NOT represent ideal direction — in fact, they almost represent what we don't want."
- `explorations/liturgical-system/` "has elements about it which were in the ballpark."

Source: [`docs/brief/2026-10-27-kickoff.md`](../brief/2026-10-27-kickoff.md)

---

## Working proposals

### 1. What we don't want, and why

Agent diagnosis of the AI-image concepts. ⚑ Josh: confirm or correct.

1. **Sham materials.** Carved wood, faux parchment, damask wallpaper, gold bevels, all *pictures of* materials. Pugin's word for this was *sham*, and he fought it all his life. (See principle 5, "Truth to materials," in `01-vision.md`.)
2. **Ornament as a frame, not as enrichment.** Decorative borders wrapped around content that is itself generic: "Worship / Grow / Give," "Welcome Home," "Plan Your Visit." A costume over a standard church template.
3. **A muddy "olde" palette.** Burgundy, sepia, antique gold. Real Gothic and Gothic Revival color is the opposite: bright, flat, clear, heraldic (see §4).
4. **Blackletter as costume.** Used on the parish name as a signal of "old church," not as a living letterform doing real work.
5. **Nothing is real.** Fake people, fake interiors, fake text. Nothing in them is Our Lady of the Atonement.

### 2. What `liturgical-system` got right

Agent reading. ⚑ Josh: which of these did you mean by "in the ballpark"?

1. **The calendar drives the site.** The day's feast is the hero; the season sets the color. The site keeps liturgical time.
2. **Restraint.** Generous space, a light ground, hierarchy carried by type rather than decoration.
3. **Real content from the tradition.** Guéranger's *The Liturgical Year* as the day's reading: the site prays with the Church instead of advertising.
4. **"The Day's Prayer."** Mass and the Office shown as the rhythm of a day, not a table of times.
5. **Rank is visible.** Upcoming feasts carry their rank (Solemnity, Memorial…).
6. **A dev tool for previewing any day.** A good pattern for building and testing calendar states.

**Where it falls short:** Cinzel and Cormorant are the default "elegant" pairing, and Cinzel is a *Roman* inscriptional capital, neither English nor Gothic. The liturgical colors are arbitrary hex values rather than drawn from real sources. There's no geometric or ornamental grammar yet. Nothing in it is specifically English or American. Its schedule data is invented but looks real (see AGENTS.md §4.4).

### 3. The thread of continuity: touchstones

These are threads to pull, not a mood board. Each is a possible source for type, color, ornament, imagery, or voice. ⚑ verify details before using any in public copy.

**Medieval England (to 1534)**
- **The Sarum Use** (Use of Salisbury): the dominant pre-Reformation English liturgical use, with its own color customs. One example is **Lenten array**: unbleached linen stencilled with Passion emblems in red and black instead of violet.
- **Opus Anglicanum**: English medieval embroidery, prized across Europe. Gold, silk, saints in architectural niches.
- **Perpendicular Gothic**: the style England gave Gothic: verticality, panel tracery, fan vaults.
- **East Anglian painted rood screens; English alabasters.**
- **"The Dowry of Mary"** (*Dos Mariae*): England's ancient Marian title. **Walsingham**, "England's Nazareth." The **Wilton Diptych**: Richard II with Our Lady, the angels in blue. Especially resonant for a parish named for Our Lady.
- **English illumination and books of hours**: the native tradition of initials, borders, and the page as an ordered, beautiful object.

**The remnant (1534–1829)**
- Recusant Catholicism kept the thread alive underground: the martyrs (More, Fisher, Campion, Clitherow), hidden chapels, the English colleges abroad.
- **William Byrd**: a Catholic composer under Elizabeth I who wrote for the Chapel Royal and also wrote Masses for clandestine recusant liturgies. Continuity in a single life.

**The Gothic Revival (19th century)**
- **A. W. N. Pugin**: *Contrasts* (1836), *True Principles* (1841), the *Glossary* (1844, in `reference/`), St Giles' Cheadle, the Palace of Westminster interiors. His work with John Hardman (metalwork, glass).
- **John Henry Newman**: the Oxford Movement to Rome, 1845.
- The Anglo-Catholic movement, which preserved much of the Catholic inheritance inside the Church of England. That inheritance is the patrimony the Ordinariate has now brought home.

**The 20th century**
- **Ninian Comper**: "unity by inclusion," gathering the whole tradition into one coherent whole with an English accent. Very close to Josh's "the whole catholic tradition, but with a particularly English focus."
- **Percy Dearmer** and the "English Use"; **The English Hymnal** (1906, with Vaughan Williams).
- **Edward Johnston**: revived broad-nib calligraphy and English lettering.
- **Note on Eric Gill:** a convert, and a major English typographer and carver (Perpetua, Joanna, Gill Sans; the Westminster Cathedral Stations). His own diaries record grave abuse. Using his typefaces on a Catholic parish site is a real question. ⚑ Josh.

**The patrimony in the Catholic Church today**
- Prayer Book English (the collects, the Coverdale psalter), the choral and hymn tradition, Evensong, now prayed within the Catholic Church through **Divine Worship** (2015) and the Ordinariates (2009–).

### 4. What the Pugin Glossary teaches

See `reference/pugin-glossary/README.md` for the plate catalog. Observations:

- **The palette is bright, flat, and heraldic:** vermilion, ultramarine, emerald, gold, black, on cream. Clarity, not murk. This alone corrects most of what's wrong with the AI concepts.
- **It is a complete ornamental grammar**, with named, systematic pattern types that map onto web structure:
  | Pugin's term | What it is | Possible web role |
  |---|---|---|
  | **Powdering** | Small motifs scattered evenly on a field | Quiet background fields |
  | **Diapering** | A repeating lattice pattern | Larger surfaces; feast-day fields |
  | **Borders, borderers** | Running bands | Section edges, rules |
  | **Orphreys** | Embroidered bands on vestments | Vertical bands, dividers, side rails |
  | **Cresting** | Ornamental top edge | Headers; the top edge of a page |
  | **Crosses, monograms, emblems** | IHS, MR, Trinity, Evangelists, Passion | Marks, icons, state indicators |
  | **Alphabets** | Lombardic capitals, textura | Initials, display lettering |
- **Altars are dressed for the day** (frontals, plates 07, 72–74). This is a direct precedent for a site that is vested according to the calendar.
- **Passion emblems** (plates 66–67) and **the Five Wounds** (65) are an obvious vocabulary for Lent and Holy Week states, and fit naturally with Lenten array.

### 5. American Gothic: threads for Josh's question

Not answers. Threads.

- **Carpenter Gothic.** Gothic translated into wood by local builders working from pattern books (e.g. Richard Upjohn's *Rural Architecture*, 1852). It was vernacular, democratic, and honest to its material. Grant Wood's *American Gothic* (1930) takes its name from the farmhouse's Carpenter Gothic window. **This may be the strongest key:** American Gothic is Gothic logic rendered honestly in a new, native material. Our native material is the web: light, type, vector, motion. That is exactly principle 5, truth to materials.
- **Richard Upjohn** (Trinity Church, Wall Street, 1846) brought Pugin's ideas to America.
- **Ralph Adams Cram**, America's great Gothicist and an Anglo-Catholic, argued Gothic was an *unfinished* tradition to be continued, not copied. That is continuity as a design philosophy.
- **Bertram Goodhue**, Cram's partner, was also a type and book designer. With printer **D. B. Updike** (Merrymount Press) he produced *The Altar Book* (1896), a high point of American liturgical book design ⚑ verify details. American blackletters (Goudy Text, Cloister Black) belong to the same lineage.
- **Fr. Paul Wattson and Graymoor.** The Society of the Atonement was an Episcopal community received into the Catholic Church in 1909. It promoted the title **Our Lady of the Atonement** and founded the Chair of Unity Octave, which runs from the old feast of the Chair of St. Peter. An American Anglican-to-Catholic story nearly a century before the Ordinariate. ⚑ verify, and ⚑ Josh: does OLA's name trace to Graymoor?
- **Place.** Texas limestone, South Texas light, live oaks; San Antonio's Spanish missions as the region's older Catholic layer. ⚑ Josh: how much should place show?

**Working hypothesis (proposed):** *American Gothic is the Gothic grammar (geometry, light, rank, the calendar, the ornament system) built honestly in local materials by local hands, with a democratic openness to whoever walks in.*

### 6. Directions to explore (not decisions)

- **Type.** Textura and Lombardic capitals for initials and display, used where they do real work (the start of a text, the name of a feast), paired with a durable text face of English or American lineage. Avoid the Cinzel/Trajan "classical elegance" default. To be chosen in the design-language phase.
- **Color.** Liturgical colors taken from real sources: OLA's own vestments and frontals (photographed), Pugin's plates, English customs such as Lenten array. Not arbitrary hex values.
- **Geometry.** Medieval masons designed with compass and straightedge: *ad quadratum* and *ad triangulum* proportions, the vesica, tracery built from arcs. A layout and ornament system generated from the same constructions would give the site a structural logic, not only a look.
- **Imagery.** Real photography of the real church, its liturgy, and its people (with consent). No generated imagery presented as real ⚑ Josh: make this a decision?
