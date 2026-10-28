---
title: Vision and governing principles
status: draft
updated: 2026-10-27
---

# Vision and governing principles

## What Josh has said

> "The ambition for this site is extremely high - ideally, the best catholic church website ever made."

> "Continuity will be a key word here."

> "…developing a iron-clad rigor - a meaning-imposing logic, to bring about a timeless unity and continuity."

> "…always, ALWAYS in service of some specific and known good for the user, never just because."

Source: [`docs/brief/2026-10-27-kickoff.md`](../brief/2026-10-27-kickoff.md)

---

## Working proposals

### What "best ever" could mean

"Best" has to be something we can check, or it turns into a matter of taste. Proposed tests:

1. **Each audience's main job is easier here than on any other parish site.** A traveler finds today's Mass on a phone in seconds. A non-Christian understands what this place is from one page. A parishioner gets to what they need in one or two taps.
2. **It could only be this parish.** Cover the logo and it's still unmistakably OLA. Nothing generic, nothing that would fit on any church's website.
3. **It teaches.** People leave knowing more about the faith, the liturgy, and the English Catholic inheritance than when they arrived, without being lectured.
4. **It stays true.** Content stays current because updating it is easy for the people who have to do it.
5. **It survives expert scrutiny from every side:** a liturgist, a type designer, an accessibility auditor, a performance engineer, and a historian of Gothic architecture should each find it right.
6. **It lasts.** In fifteen years it should look rooted, not dated.

### Governing principles

Each principle is marked **Josh** (stated in the brief) or **Proposed** (an agent's reading, waiting for ratification).

#### 1. Continuity (Josh)
One thread runs from the pre-Reformation English Church through Pugin and the Gothic Revival, through the Anglican patrimony welcomed home, to an American parish today. Every design choice should be able to say which part of that thread it carries.

#### 2. Every element earns its place (Josh, with a proposed framing)
Josh's rule for technology turns out to be Pugin's own first principle. From *The True Principles of Pointed or Christian Architecture* (1841):

> "The two great rules for design are these: 1st, that there should be no features about a building which are not necessary for convenience, construction, or propriety; 2nd, that all ornament should consist of enrichment of the essential construction of the building."

Proposed translation for the web:
- **Convenience:** it helps someone do something they came to do.
- **Construction:** it reflects the real structure of the site: its content, data, and code.
- **Propriety:** it fits. Right for a church, right for this day, right for this moment.
- **Ornament enriches construction:** decoration belongs on real things (the start of a text, the edge of a section, the state of the calendar), never as free-floating frames around generic content.

This is the "meaning-imposing logic." It applies equally to a WebGL shader and a drop cap.

#### 3. English-Catholic, specifically (Josh)
Not "Anglican-flavored" and not generically "traditional." See [`03-aesthetic.md`](03-aesthetic.md).

#### 4. Hospitality to every audience (Josh)
The stranger, the inquirer, the parishioner, and those who serve should each find their way. See [`02-audiences.md`](02-audiences.md).

#### 5. Truth to materials (Proposed)
Also Pugin. He despised sham: plaster pretending to be stone, cast iron pretending to be carving. On the web, the sham is fake stone textures, faux parchment, carved-wood frames, gold bevels. That is a big part of why the early AI-image concepts fail. Gothic should be expressed in the web's own materials: light, type, vector geometry, color, motion, and real photography of the real church. American Carpenter Gothic did the same thing in wood, and did it honestly (see `03-aesthetic.md`).

#### 6. The site keeps liturgical time (Proposed)
The liturgical calendar is the site's clock. Season, feast, rank, and color are live state that shapes what the site shows and how it looks, the way the church building itself is dressed differently in Advent and at Easter. This is the main thing `explorations/liturgical-system` got right.

#### 7. Propriety: ornament scales with rank (Proposed)
In the liturgy, vestments, music, candles, and incense scale with the rank of the day. A ferial weekday is plain; a solemnity is fully vested. The site could follow the same rule: the amount of ornament is set by the day's rank, not by a designer's mood. This gives ornament a non-arbitrary logic and keeps the site from feeling overdone on an ordinary Tuesday.

#### 8. A floor for everyone (Proposed)
The site is fully usable without any advanced effects: fast on an old phone, legible to a screen reader, comfortable for older eyes, usable on a weak connection. Every effect is layered on top of a floor that is already complete. Accessibility here is a form of charity, not a compliance checkbox.

#### 9. Stewardship (Proposed)
The site has to outlive its builders. "Timeless" includes operations: parish staff can keep the content true without a developer, and the code is plain enough that a future maintainer can understand it.
