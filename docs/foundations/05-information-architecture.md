---
title: Information architecture
status: draft
updated: 2026-10-27
---

# Information architecture

**Status:** direction accepted (decision 0004): a *Today* home page and five sections. Section-by-section design is under way in `docs/sections/`.

## What Josh has said

> "Once we have some basic block and tackle in place for the project, we'll start by thinking about the information architecture."

> "My first stab at simplifying from today's navigation was in pursuit of a much easier-to-understand navigation at first glance. This doesn't take too much into account in terms of audience segmentation, FYI."

> "we do not need to have everything or even most of what is currently on the site on the new site. Father has given me cart blanche." ([brief](../brief/2026-10-27-ia-kickoff.md); decision [0003](../decisions/0003-start-fresh-content-earns-its-way-in.md))

### Current navigation (19 items, top level only; the full menu is ~70 links, see the audit)

- **Quick:** Home, Emergency Pastoral Care, Sunday Bulletin, Formed, Donations and Gifts, Join Us, Events
- **Primary:** Liturgy, Sacraments, Ministries, Education, Becoming Catholic, About Us, Giving
- **Footer:** Holidays, Mass Times, Confession Times, Sunday Bulletin, Parishioner Business Directory

### Josh's first simplification

- **Primary nav:** Sacraments, Ministries, Education, Gallery
- **Footer:** About Us, Join Us, Emergency Pastoral Care, Formed, Giving, Sunday Bulletin, Parishioner Business Directory
- **Moved into the page body:** Holidays, Mass Times, Confession Times, Events

Source: [`docs/brief/2026-10-27-kickoff.md`](../brief/2026-10-27-kickoff.md)

---

## Early observations (agent, for discussion)

**What works**
- Cutting 19 items to 4 primary is the right instinct.
- Moving Mass and Confession times into the page body is right: it's the most common task, and it shouldn't take a click.
- Holy days and events in the body fit naturally with a calendar-driven home page.

**Questions to work through**
1. **Inquirers lose their front door.** "About Us," "Join Us," and "Becoming Catholic" are in the footer or gone. For both inquirer audiences, and for Ordinariate seekers, those are the main path in.
2. **"Liturgy" disappeared.** For this parish the liturgy is arguably *the* distinctive thing, and Divine Worship, music, the Office, and the liturgical year aren't sacraments. Should it be primary?
3. **Emergency Pastoral Care in the footer.** It's the one truly urgent task. It probably needs to be reachable from anywhere in one tap, especially on mobile, while staying discreet.
4. **"Gallery."** What good does it serve? It might be stronger as a tour of the church (its art, architecture, and story), or the whole site could be the gallery. ⚑ Josh: what was the intent?
5. **Labels reflect how the parish is organized** (Ministries, Education) more than what people come to do. To be tested against the audience needs in `02-audiences.md` §E.
6. **Parishioner vs. public.** The remembered state (`02-audiences.md` §D) could carry much of the parishioner load (bulletin, giving, ministries), letting the public navigation stay very simple.

## Suggested inputs for the IA session

- **The current-site audit:** [`docs/research/current-site-audit.md`](../research/current-site-audit.md). It has the full menu as built (~70 links), an 83-page inventory, content-health problems, and IA implications (§7).
- Analytics data, if access is granted (Q20).
- The audience × needs table in `02-audiences.md` §E.
- Later: card sorting and tree testing with real parishioners and real newcomers.

---

## Proposal A: Today, and five doors (2026-10-27; direction accepted)

### Stance

1. **Plain labels; a rich experience.** The navigation should be instantly legible to a stranger on a phone. Distinctiveness comes from the home page, the craft of each section, and the data underneath, not from clever labels.
2. **The home page is *Today*.** It answers the most common question ("when can I come?") before anyone has to look, and it keeps liturgical time: the day's feast, season, and color, then today's and this week's services, then current notices. This is the calendar principle (vision §6) applied to the IA.
3. **Enter once, show everywhere.** Services, events, notices, groups, and people are structured data. Pages are views of that data, which is how times stay consistent and correct.
4. **Doors, not menus.** About five sections, each a well-made landing page rather than a dropdown of links. Roughly 35 pages in total, against 95 today.
5. **Everything has an owner.** A page or group without a named person keeping it true doesn't ship (decision 0003).

### The structure

```
TODAY (home)
  The day: feast, season, color, readings
  Today and this week: Mass, Office, Confession, Adoration, with exceptions applied
  Notices (each with an expiry date)
  The five doors
  Remembered parishioners get a shortcut row: my Mass, this week's bulletin, my groups, give

VISIT                       for travelers, the curious, seekers, Catholics considering OLA
  Mass and Confession times (the full schedule, holy days, seasonal changes)
  Your first visit: what to expect at Divine Worship
  Directions, parking, accessibility
  Start here: four short paths
    Curious about the Catholic faith
    Coming from the Anglican or Protestant tradition
    Coming home to the Church
    New to San Antonio? Join the parish

WORSHIP                     for everyone: the heart of the place
  Holy Mass and Divine Worship
  The Daily Office: Mattins and Evensong
  Confession
  Adoration and devotions
  The liturgical year: calendar, holy days, Holy Week and Christmas schedules
  Sacred music: choirs, organs, concerts
  Watch: recordings or livestream
  Request a Mass intention

SACRAMENTS                  for people at a threshold
  Becoming Catholic (instruction; reception into the Church)
  Holy Baptism
  Confirmation
  First Holy Communion
  Holy Matrimony
  Anointing of the Sick, and care of the homebound
  Funerals: the Requiem and burial   (new: no page today)
  Holy Orders and vocations
  Each page: how to arrange it at OLA first, then what the sacrament is

PARISH LIFE                 for parishioners and those who serve
  Join the parish (registration)
  Calendar and events
  The bulletin
  Groups and ministries (one directory, filterable)
  Formation: adults, children, Formed
  Giving
  Stay in touch (Flocknote)
  Safe environment (for volunteers)

ABOUT                       for the curious, pilgrims, press
  Our story: 1983, the Pastoral Provision, the Graymoor title, the Ordinariate
  The Ordinariate and the Anglican patrimony
  The church: architecture, art, glass, organs   (where "Gallery" could live)
  Clergy and staff
  Contact and office hours

ALWAYS VISIBLE (header, including on phones)
  Need a priest?            emergency and pastoral care, one tap
  Give
```

### Check against the audiences

| Audience | First stop | Then |
|---|---|---|
| Traveler | Today (next Mass, address) | Visit → directions |
| Curious non-Christian | Visit → Start here | About → our story, the church |
| Christian seeker (Ordinariate) | Visit → "Coming from the Anglican or Protestant tradition" | About → the Ordinariate; Sacraments → Becoming Catholic |
| Catholic considering OLA | Visit → your first visit | Worship; Parish Life → join |
| Returning Catholic | Visit → "Coming home" | Worship → Confession |
| Person at a threshold | Sacraments, or Need a priest? | The specific rite, a person to contact |
| Pilgrim / admirer | Worship → music, watch | About → the church |
| Parishioner | Today (shortcut row) | Parish Life |
| Those who serve | Parish Life → groups | (Later: member tools) |
| Machines | Every schedule and event as structured data and a calendar feed | |

The spatial model from `02-audiences.md` §C still holds underneath: About is the churchyard, Visit is the porch, Worship is the sanctuary (central and visible to all), Parish Life is the nave, and member tools would sit in the chancel.

### Compared with Josh's first simplification

| Josh's draft | Proposal A | Why |
|---|---|---|
| Sacraments | **Sacraments** | Kept. Becoming Catholic and Funerals added. |
| Ministries | Inside **Parish Life**, as a directory | 28+ groups need filtering, not a menu, and they sit alongside events, bulletin, and giving |
| Education | Inside **Parish Life** (formation) | Mostly parishioner programs |
| Gallery | Inside **About** as "The church" | Gives the art and architecture a story and context (⚑ Josh: Q17) |
| *(footer)* About, Join Us | **About**, **Visit** promoted to primary | Inquirers' main ways in |
| *(footer)* Emergency Pastoral Care | **Need a priest?** in the header | The one urgent task, reachable from anywhere |
| *(missing)* | **Worship** | The liturgy is what most distinguishes OLA |
| *(body)* Mass times, holidays, events | **Today** home page plus schedule data | As Josh proposed, and generated from one source |

### What happens to today's content

| Fate | Content |
|---|---|
| **Rebuild** (needed, rewritten in the new voice) | Schedules (as data); practical sacrament pages; Becoming Catholic; the Ordinariate explainer; our story; clergy and staff; contact; giving (Tithely); bulletin (LPi); events; safe environment; emergency care |
| **Merge** | The two sacrament layers → one page per sacrament; Why Catholic, What is Salvation?, Who is Jesus?, and Coming Back → the four Visit paths; organs and music pages → Sacred music and The church; 28 ministry pages → one directory, listing only groups with an active, named contact |
| **Cut** | COVID-19; the Academy booster club; test pages; News; duplicate calendars and pages; the 2025 holidays PDF (closures become schedule exceptions); link lists to outside resources from 2023; YouTube-embed catechesis pages from 2019; the photo album (replaced by The church) |
| **Decide** | Parishioner Business Directory (cut, or a later member feature with consent from those listed); careers (show only when there's an opening) |
| **New** | Today; Funerals; Mass intentions; What to expect at Divine Worship; the four Start-here paths; the liturgical year; Watch; Need a priest? |

### Josh's answers (2026-10-27)

Verbatim in [`brief/2026-10-27-ia-answers.md`](../brief/2026-10-27-ia-answers.md). Recorded as decision [0004](../decisions/0004-ia-direction-today-and-five-sections.md).

1. **Sections:** "The number of sections won't be determined by a number, but by proposed sets." Having read Proposal A: "yes, I think both have the right idea." → Today plus the five sections is the working direction. Alternative sets are below for comparison.
2. **Today:** yes. It should feature "today from a Church calendar/saints perspective, as well as schedule, events, etc," and "also needs to serve as the front door for everything."
3. **Gallery:** inside About → "The church," for now. (Q17 answered.)
4. **Ministries:** "minimally should have a description and contact, and don't necessarily need their own page." → A directory entry by default.
5. **Business Directory:** "Potentially keep, but deprioritize for now."

Also: pages are added "slowly… with deliberation," not converted. Even the initial core is "just drawing material from what exists."

### Alternative sets

Whole sets, for comparison against Proposal A.

| Set | Sections | Strength | Weakness |
|---|---|---|---|
| **A (working)** | Visit · Worship · Sacraments · Parish Life · About | Each section matches a distinct need; plain labels | Five items is the most a phone header can carry comfortably |
| **B: three doors** | Welcome · Worship · Parish | Simplest first glance; maps directly onto porch, sanctuary, and nave | Large landing pages. Someone arranging a funeral has to know the sacraments live under Worship. |
| **C: a door for seekers** | Visit · Worship · Sacraments · **Becoming Catholic** · Parish Life · About | Puts OLA's founding mission (receiving converts, especially Anglicans) in the primary navigation | Overlaps Visit's "Start here" paths and Sacraments; a sixth item |
| **D: life moments** | Visit · Worship · **Life's Moments** · Parish Life · About | Plain words for people who don't know the term "sacraments" ("I need to plan a funeral") | Gives up the Church's own word; Confirmation and Holy Orders fit awkwardly; more generic in tone |
| **E: Josh's first draft, completed** | Sacraments · Ministries · Formation · The Church (times and visiting on Today) | Closest to how parishioners already think about the parish | No section for the liturgy; a directory in the primary nav; inquirers depend entirely on the home page |

**Agent's view:** A, with C's point carried by a strong "Coming from the Anglican or Protestant tradition" path inside Visit. Revisit C if testing shows seekers miss that path.

### Section designs

Each section is designed in its own doc before its pages are written. Labels and terms follow the usage list in [`docs/glossary.md`](../glossary.md) (decision [0005](../decisions/0005-traditional-terms.md)).
- [`docs/sections/sacraments.md`](../sections/sacraments.md): what OLA should say about the sacraments, given that general answers are now one question away. Framework accepted, Witness deferred (decision [0006](../decisions/0006-sacraments-say-what-only-we-can-say.md)).
