# 0004 — IA direction: a *Today* home page and five sections

- **Status:** accepted (as direction; labels and contents can still change)
- **Date:** 2026-10-27
- **Decided by:** Josh Goforth

## Context
Proposal A in `docs/foundations/05-information-architecture.md` put forward a home page called *Today* and five sections: Visit · Worship · Sacraments · Parish Life · About. Josh: "yes, I think both have the right idea." Josh's other answers are in the [brief](../brief/2026-10-27-ia-answers.md).

## Decision
- **Home page:** *Today*. It features the day from the Church's calendar (feast, saints, season), the schedule, and events, and it is also the front door to everything else.
- **Sections:** Visit · Worship · Sacraments · Parish Life · About is the working structure. The number of sections comes from comparing whole proposed sets, not from a target count.
- **Pages are added deliberately, one at a time.** Nothing is converted from the old site. The initial core draws material from what exists but is written fresh.
- **Ministries:** each needs at least a description and a contact, and doesn't necessarily get its own page. A directory entry is the default.
- **Gallery** lives inside About → "The church," for now.
- **Parishioner Business Directory:** possibly kept later; deprioritized.

## Consequences
- The content model needs a *ministry* entry type (description, contact, and optionally meeting time and link) that can exist without a page.
- Each section is designed in its own doc under `docs/sections/` before its pages are written.
- The Business Directory is out of the initial core.
