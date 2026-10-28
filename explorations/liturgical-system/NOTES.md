# liturgical-system

**What it is:** a single-page HTML concept (Dec 2025, made with Claude) for a home page driven by the liturgical calendar. A dev menu on the right switches between 14 sample days (First Sunday of Advent, Gaudete, Holy Family, Ash Wednesday, Good Friday, Easter, Pentecost, Assumption, All Souls, …). Each switch changes the season, feast, color theme, Guéranger reading, schedule, and upcoming feasts.

## Verdict

**Josh (2026-10-27):** "has elements about it which were in the ballpark." Asked which: "Probably just having the seasons integrated, and clean typography, and use of color."

**Keep: confirmed by Josh**
- Seasons integrated into the site.
- Clean typography.
- Use of color (season-driven).

**Agent assessment**

**Also possibly worth keeping** (agent's reading, not confirmed)
- The calendar drives the site: the day's feast is the hero, and the season sets the color.
- Restraint: generous space, a light ground, hierarchy carried by type.
- Real content from the tradition (Guéranger's *The Liturgical Year*) as the day's reading.
- "The Day's Prayer": Mass and the Office shown as the rhythm of a day.
- Feast rank shown alongside upcoming feasts.
- A dev tool for previewing any liturgical day (worth rebuilding properly for the real site).

**Avoid**
- Cinzel and Cormorant: the generic "elegant" pairing, and Cinzel is Roman rather than English or Gothic.
- Arbitrary hex values for liturgical colors.
- Invented schedule data that looks real. **The times, Mass names, and confession hours in this file are not verified parish facts.**
- Nothing in it is yet specifically English, Gothic, or American.

See also `docs/foundations/03-aesthetic.md` §2.
