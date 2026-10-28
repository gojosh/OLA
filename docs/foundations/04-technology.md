---
title: Technology principles
status: draft
updated: 2026-10-27
---

# Technology principles

## What Josh has said

> "We are in the glory days of what can be done on the web. Nothing is off limits. We should stretch technology to its absolute limit if necessary for realizing a beautiful vision, while developing a iron-clad rigor - a meaning-imposing logic, to bring about a timeless unity and continuity. We may use WebGL with advanced shaders, we may use extensive animated SVG rendering, everything is on the table, but always, ALWAYS in service of some specific and known good for the user, never just because."

Source: [`docs/brief/2026-10-27-kickoff.md`](../brief/2026-10-27-kickoff.md)

**No stack has been chosen.** Choosing one is a decision record in Phase 3 (see `docs/roadmap.md`), made after the IA and content model are understood.

---

## Working proposals

### 1. Layers: a complete floor, then enrichment

Every page works at the lowest layer. Each layer above adds to it and never replaces it:

| Layer | Delivers | Must work without the layers above it? |
|---|---|---|
| **Content and structure** (semantic HTML, structured data) | Every fact, every task, every link. Screen readers, search, and AI assistants read this layer. | Yes, completely |
| **Presentation** (CSS: type, color, layout, geometry, pattern) | The design language, liturgical theming | Yes |
| **Behavior** (JavaScript) | Personalization, interactive calendar, live state | Yes |
| **Enrichment** (WebGL, shaders, complex SVG animation, audio) | Moments of beauty that serve a stated good | n/a: always optional |

Enrichment honors `prefers-reduced-motion`, `prefers-reduced-transparency`, `Save-Data`, low-power and low-memory devices, and always has a still or static equivalent that conveys the same meaning.

### 2. The Effect Ledger

Josh's rule ("always in service of some specific and known good") is enforced by writing it down. Before any non-trivial effect is built, add an entry to `docs/effect-ledger.md` (create the file with the first entry):

```markdown
## <Effect name>
- **Status:** proposed | approved | built | retired
- **What it is:** one or two sentences, concretely.
- **The good it serves:** what a person understands, feels, or can do because of it that they couldn't otherwise.
- **For whom:** which audience(s) and which mode (discerning / tasking).
- **Pugin test:** convenience, construction, or propriety? What real thing does it enrich?
- **Degrades to:** the reduced-motion / low-power / no-JS equivalent.
- **Cost:** bytes, CPU/GPU, battery, build and maintenance effort.
- **Kill criterion:** what would make us remove it.
```

An effect that can't fill in "the good it serves" in plain words doesn't get built.

**Illustrations** of what might pass (not commitments): light moving through a window as the real time of day and the liturgical color change (*propriety*: the building keeps time); a tracery pattern constructed stroke by stroke from its geometry, used where the site explains Gothic (*convenience*: it teaches how the form is made); a feast's ornament density set by its rank (*propriety*: the day's dignity is legible).

### 3. Budgets are part of the rigor

Proposed floors, to be confirmed when the stack is chosen:
- **Accessibility:** WCAG 2.2 AA at minimum, tested with real assistive technology, not only automated checks.
- **Performance:** a fast, fully usable first view on a mid-range phone over a slow mobile connection. Specific Core Web Vitals and byte budgets get set in Phase 3.
- **Resilience:** core content readable with JavaScript off and with the enrichment layer failing.

### 4. The liturgical calendar is core infrastructure

If the site keeps liturgical time (vision principle 6), the calendar engine sits at the center of the build. It has to be the **Ordinariate's calendar** (Divine Worship), which differs from the general Roman calendar: Sundays after Epiphany and after Trinity, Pre-Lent ("Gesimatide"), Ember and Rogation days, English and Ordinariate observances ⚑ verify specifics, plus OLA's own parish observances. Off-the-shelf Roman-calendar libraries probably won't get this right. Expect to build or extend one, and treat its correctness as a liturgical matter, reviewed by clergy.

**Existing source:** the current site's "Today's Mass Readings" block already pulls from **Universalis**, set to the Ordinariate calendar (it showed "Tuesday after the Twenty-first Sunday after Trinity" on 2026-10-27). Universalis is a candidate data source, or at least a reference to check our own engine against ⚑ verify its terms for website use and how complete its Ordinariate data is (ranks, colors, Ember/Rogation days).

Outputs it should drive: the day's feast, season, rank, and color; the day's schedule (including exceptions); upcoming observances; calendar feeds (ICS); structured data.

### 5. Content operations are a technical requirement

Whatever is chosen must let staff update schedules, notices, events, and the bulletin quickly and safely, without a developer. Schedule exceptions (holy days, holidays, Holy Week) are where parish websites usually go wrong, so the content model needs to handle them as first-class data rather than free text.

### 6. Integrate, don't rebuild

The parish already relies on outside systems. Known so far: **Tithely** (giving), **Flocknote** (email/text updates), **LPi / Parishes Online** (bulletin), **Formed** (formation streaming), **Universalis** (readings), **YouTube**, **Vimeo**, **Facebook**. Full list with evidence: [`docs/research/current-site-audit.md`](../research/current-site-audit.md) §2. The site should present these well and hand off cleanly, not rebuild them. Still unknown: parish-management/records system, and any contract terms (Q21).

### 7. Machines are an audience

Ship structured data (schema.org `Church`, `Event`, opening-hours style schedules), calendar feeds, a clean sitemap, and consider an `llms.txt`, so search engines, maps, Mass-time directories, and AI assistants report OLA's information accurately.
