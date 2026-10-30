# Roadmap

## Now / Next

- **Now:** Phase 0 wrapping up; Phase 1 discovery has started. The current-site audit and content inventory are done (`docs/research/current-site-audit.md`).
- **Next:** section design, one section at a time (`docs/sections/`). Sacraments: framework accepted (decision 0006); next is gathering the *Here* facts and Father's emphasis. Then Today (home) and Visit. IA direction accepted (decision 0004); traditional terms throughout (decision 0005).
- **Also in progress:** the Today home page. Josh chose concept A, *Folio* (2026-10-28), and it has had a second pass (`explorations/home-page-concepts/`). Three Effect Ledger entries are proposed.
- **Also in progress:** recovering Pugin's alphabets (plates 9–12) as fonts. Flattening the plates and removing the gutter shading are done (`tools/flatten`). The method is decided (decision 0008). The first family, **Pugin Lombardic** (plate 9 capitals), has references, proportions, a construction kit, and the whole plate built: 31 glyphs (A–Z without J; both forms of M, T and W, the uncial ones under `ss01`; the cross and the dot ornament; a modern Y of our own under `ss02`), spaced, in a draft font, in `fonts/pugin-lombardic/`. The letters share two stem weights (decision 0009), one curl, and regularized balls, trefoil and two-lobe terminal, each set to the median of what the letters want alone. A rebuild takes under a minute. The proof page has a point editor for final tweaks, saved as recorded moves the build applies (decision 0010). Spacing and kerning are judged a pair at a time (`tools/type/spacing.py`), set tighter at Josh's request. Next for it: a family-wide pass on terminal lobe sizes (Josh, 2026-10-28); the defaults and code points wait on Q34 and Q35. The second family, **Pugin Textura** (plate 9's small alphabet, late 15th century), has references for all its glyphs, a simulated broad nib (`tools/type/nib.py`), all 24 plain letters on the plate and proposed u, w and j in a draft font, set under Lombardic initials (decision 0011). Its pen turns, as Pugin's does, from 45° at the heads to 50° at the feet, and its free feet carry spurs that the stylistic set `ss01` turns off. Where two strokes meet in one edge (b, d, g, o, q, v, w), the outline is trued to Pugin's straight edge. n's, m's and h's heads and k's bowl are joined to the stem before them by a hairline, as his are; d's and g's bowls are closed, and k is one piece. The i's head is written light with a top spur, and the mark over i and j is our own: a short touch of the nib turned to 30°. The s is a single stroke of a pen that turns as it goes, its pressure one level with a bump at each turn and is now Josh's own outline, drawn over Pugin's in a drawing program and built as it stands (decision 0014; 0.96 px from Pugin's letter). So are the g, the r, the p (with Pugin's curls on the left), the f, the t, Pugin's archaic x and the z, drawn over the built letters (the z over Pugin's), and an alternate y under `ss03`; the x is now a modern one in the family's pen, with the archaic x under `ss04` (decision 0015); a pressure dimension along every line is next, worked through with Josh letter by letter. Finer features have begun with the e's crossing member, drawn with the nib's tip and ending in pips. Its details can now be set by hand in a stroke editor on the proof page (decision 0012). b, d, h, k and l share one plain split top, and q ends in the same split turned upside down at the descender line, Pugin's flourished tops and swashes to come as alternates; its five settings are tuned in a panel of the stroke editor, all seven letters at once. Corrections to some letters are built with `--fit`, which leaves the rest as they stand. Next: the ampersand and the hairline exits, then the flourished alternates, then plate 10's capitals.
- **Waiting on Josh:** see `docs/open-questions.md`, especially Q26 (what OLA wants to say about each sacrament), Q20 (analytics access), Q23 (after-hours emergencies).

*(Agents: update this section at the end of any session that moves the phase or the focus.)*

## Phases

These are a sketch, not a schedule. Phases will overlap.

### Phase 0 — Foundations *(current)*
Project structure and conventions; the brief captured; first drafts of vision, audiences, aesthetic, technology, and IA. **Done when:** Josh has reacted to the drafts and the key principles are marked accepted.

### Phase 1 — Discovery and information architecture
Inventory the current site's content; check audience needs against real usage; draft the IA and navigation; test it with real parishioners and newcomers (card sort, tree test). **Done when:** an IA is accepted as a decision record.

### Phase 2 — Design language
Research the touchstones; build the systems: type, liturgical color, geometry and grid, the ornament grammar (from the Pugin Glossary and beyond), photography direction, voice. Prototype key pages as explorations. **Done when:** a design language is documented and key page prototypes are accepted.

### Phase 3 — Technical architecture
Choose the stack, CMS, and hosting; design the liturgical calendar engine and content model; set performance and accessibility budgets; approve the first Effect Ledger entries. **Done when:** a stack decision record is accepted and a vertical slice runs.

### Phase 4 — Build
Build the site in its layers: the complete floor first, then enrichment.

### Phase 5 — Content, migration, and launch
Write and migrate content; clergy review; editor training; accessibility and performance audits; launch.

### Phase 6 — Stewardship
Ongoing care, measurement, and refinement through the liturgical year.
