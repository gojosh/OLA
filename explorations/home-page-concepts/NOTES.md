# home-page-concepts

**What it is:** two draft concepts for the *Today* home page (decision 0004), made 2026-10-27 by Claude (Opus 5.5). Folio was taken further on 2026-10-28 (see "A · Folio, second pass" below). Josh asked for "a couple of draft home page concepts… pugin vector art, clean typsetting, generous whitespace. This needs to be absolutely cutting edge design steeped in tradition."

| File | Concept | The idea in a line |
|---|---|---|
| [`a-folio.html`](a-folio.html) | **A · Folio** | The home page is a page of a liturgical book, and each day is a new page. |
| [`b-tracery.html`](b-tracery.html) | **B · Tracery** | The home page is architectural and contemporary; the year is drawn as a rose window. |

**How to look at them:** open either file in a browser; they need an internet connection for the fonts. A bar at the bottom left switches among sample days so you can see the page change with the calendar. B has five; Folio now has nine, including the whole week from 27 October to 2 November, and you can turn between them with the arrows by the page number or the ← → keys. B's five days are:
- a green weekday after Trinity
- the feast of Saints Simon and Jude (red)
- All Saints, a solemnity (white and gold)
- the First Sunday in Advent (violet)
- a weekday in Lent, shown in Lenten array as a proposal

When the real date matches a sample day, the page marks which services have already happened and which comes next, using parish time.

## Verdict

**Josh (2026-10-28):** "Take Folio (A) further." → A is the direction. B is kept for reference; its ideas (the rose, the timeline) can be borrowed by decision.

## A · Folio, second pass (2026-10-28)

What was added, and why:

- **The frontal for the day.** The page's illustration is now an altar frontal drawn for the day, after plates 07 (frontals) and 74 (palls). It has:
  - a field in the day's color
  - side orphreys of quatrefoils on blue
  - an inscription band lettered in textura, with a cross at each end
  - a fringe
  - one or two roundels with the day's emblem

  It follows the rank ladder:
  - Feria: no frontal at all.
  - Sunday: a plain field with a cross.
  - Feast: a field powdered with gold crosslets.
  - Solemnity: a diapered field.
  - All Souls: a black pall with white crosses.
  - Lent: linen with a crown of thorns.

  This is the idea in `03-aesthetic.md` §4 made literal: "Altars are dressed for the day… a direct precedent for a site that is vested according to the calendar."
- **Emblems, drawn after plate 63:**
  - Saint Simon's saw and Saint Jude's ship
  - a crown of glory for All Saints
  - a crown of thorns for Lent
  - the cross for Sundays and All Souls

  They are gold on colored grounds inside quatrefoiled roundels, as in Pugin. Emblems follow common Western iconography ⚑ verify: East Anglian rood screens sometimes give Simon a fish and Jude a boat or club.
- **Inscriptions** come from public-domain English sources, cited in the frontal's caption:
  - the Coverdale Psalter: Psalm 19.4 for the apostles, 25.1 for Advent Sunday (its Introit), 51.1 for Lent
  - the King James Version: Revelation 7.9 for All Saints
  - the traditional English of the Requiem introit for All Souls (⚑ check against *Divine Worship*)

  Textura is used here for lettering on a real object, as on Pugin's palls, not as costume.
- **The week, as a kalendar.** "Days to come" is now the next seven days laid out like the calendar page of a Book of Hours:
  - day number, weekday, observance
  - feasts and solemnities in red (red-letter days)
  - the current day marked with the day's color

  Sundays are named by a small calendar engine. Other days come from a short sample list. Days with no listed observance are left blank, as medieval kalendars did. ⚑ The real calendar engine fills them in. Days in the sample can be opened from the kalendar.
- **Turning the page.** The arrows beside the folio number, or ← → on a keyboard, turn to the previous or next day. Where the browser supports it, the plate slides and fades in the direction of travel. This uses view transitions and is a proposed Effect Ledger entry. With reduced motion, or without support, the change is instant. In the concept the arrows step through the sample days; on the real site they would step through every day.
- **Heading by day.** "Today at the Atonement" becomes "Thursday at the Atonement" when you're looking at another day, and the next service is marked only on the real today.
- **On phones:** title, then today's times, then the week, then the frontal, then the collect. Practical things come before ornament.
- **A placeholder where a text can't be used yet.** All Souls has no 1662 collect, so the page shows a bracketed placeholder, pending Q27.

Still open in Folio:
- Real Lombardic initials, drawn after plate 09, to replace the Caslon initial.
- An emblem for every saint's day: a content system that needs a source list and clergy review.
- How the frontal behaves on days with two observances (for example a Sunday that is also a saint's day).

## What both concepts share

- **The Today brief from the IA work:**
  - the day (feast, rank, season, color)
  - the day's collect
  - today's services
  - days to come
  - parish notices
  - the five sections
  - *Need a priest?* and *Give* always in the header, including on phones
- **Ornament scales with the day's rank** (vision principle 7). It is set by the calendar, not by taste:

  | Day | A · Folio | B · Tracery |
  |---|---|---|
  | Feria (ordinary weekday) | Two plain rules in the day's color. No initial. | The center of the rose is left empty. The day's name is set in the quiet serif. |
  | Sunday | Cresting in the day's color; a thin side band; a colored initial. | The center is glazed in the day's color. The name is set in textura. |
  | Feast | Gold cresting on a band of the day's color; a diapered side band. | A gold cross in the center; the eight roundels are tinted. |
  | Solemnity | Gold cresting set with red and blue jewels, plus a diapered band below; a wide side band; the initial set in a diapered square. | Gold in the center and in every roundel; the name is set heavier. |
  | Lent (proposal) | No color and no gold. The page turns to unbleached linen, marked with red and black crosses. | The Lent weeks are glazed in linen; a red crosslet sits in the center. |

- **Ornament is drawn, not copied.** The fleur-de-lis, cross pattée, crosslet, quatrefoil, cresting, diapering, and borders are hand-built SVG vectors. Each follows a specific Glossary plate:
  - crosses for marking church linen: plates 13–14
  - borders for altar cloths: 15–16
  - cresting: 19
  - diapering: 23–27
  - frontals and orphreys: 07

  These are a few kilobytes, sharp at any size, and colored by the calendar.
- **Colors come from the plates.** They were sampled from the Glossary previews with a script and white-balanced against the plates' paper (photographed `#E3DCC6`, corrected to `#F4EFE3`). Where text needed contrast, the color was darkened.

  | Role | Value | Source |
  |---|---|---|
  | Paper | `#F4EFE3` | plate paper, corrected |
  | Vermilion (ornament) / rubric red (text) | `#C4503B` / `#A8382A` | plates 09, 19 (`#C05542` photographed) |
  | Ultramarine | `#2F4F94` | plates 09, 23, 24 (`#4066A2`) |
  | Green (text) / green (glass) | `#3F6447` / `#4A824D` | plates 07, 22, 29 (`#3B5C3E`, `#457843`) |
  | Gold | `#B8963F` | plates 19, 23 (`#C8B869`), deepened to show on cream |
  | Violet | `#56406F` | plates 01–06. Pugin uses almost none, so this is the weakest sample. |
  | Black | `#2A2729` | plate 74 (funeral palls) |
  | Rose | `#B76E7C` | not in the plates; derived from the red ⚑ |

  Text contrast was checked. Body text, red text, and labels pass WCAG AA (4.5:1 or better). The exceptions:
  - The gold initials in A pass only at their large size.
  - The placeholders sit around 3.3:1.
  - The season labels on the rose's green glass reach 4.3:1.

## A · Folio

- **The page as a plate.** A hairline vermilion frame like the Glossary's plates. The folio number is the day of the month, and a caption between crosses names the season.
- **Rubrication.** Red is used for what to *do*: times, labels, the date. Black is used for what to *read*. This is the liturgical books' own convention ("say the black, do the red").
- **Red-letter days.** In *Days to come*, feasts and solemnities are written in red, as in medieval calendars. This is where the phrase comes from.
- **Vested by the calendar.**
  - **Cresting** (plate 19) runs along the top edge.
  - **An orphrey band** runs down the side of the page, like the borders on a frontal (plate 07).
  - **A Lombardic-style initial**, two-colored after plate 09, begins the feast's name.
- **Caslon throughout.** It was the type of English printers and of colonial American ones. A colophon at the foot says so, as a book would.
- On phones, today's times move up to sit right after the day's name.

## B · Tracery

- **The year as a rose window.** The rose is drawn from the calendar:
  - The outer ring has one lancet light per week of the Christian year (52 or 53), glazed in its season's color.
  - The inner ring names the seasons.
  - Eight roundels and a central quatrefoil carry the day's rank.
  - A hand points to today, so you can see where you stand in the year.
  - Hovering over a light shows that Sunday's name and date.

  A small calendar engine in the file computes Easter, Advent, and the seasons.
- **Textura is kept for days that have a name of their own.** Sundays, feasts, and solemnities are set in Texturina, a recent textura revival. Weekdays are set in a quiet serif. This uses blackletter for real work, as `03-aesthetic.md` §6 suggests, not as costume.
- **Today as a timeline.** The day's services are placed on a line from 6 a.m. to 7 p.m., with Confession shown as a span and a "now" marker. On phones it becomes a list. A one-line summary of today's services sits in the opening section on every screen size.
- **Contemporary frame.** A grotesk (Instrument Sans) for navigation and labels, Newsreader for reading, a strict grid, and hairlines. A thin band of the day's color runs across the top like a stole.

## Honesty about the content

- **Times** are as published on the current site on 2026-10-27 (audit §6). ⚑ verify.
- **Day names, ranks, and colors** are the agent's reading of the Ordinariate calendar. ⚑ verify, especially:
  - "Tuesday after the Twenty-first Sunday after Trinity" as the form of a weekday name
  - All Souls labelled "Commemoration" and colored black
  - the Lateran dedication as a Feast in the Ordinariate calendar
  - Laetare in rose
  - "Pentecost" as the name in the rose's hover text
- **The calendar engine in B is approximate.** It ends Christmastide at the Epiphany and colors Passiontide violet. It doesn't handle transferred feasts or the Sunday next before Advent. It exists to draw the year, not to be the real engine (`04-technology.md` §4).
- **Collects are from the Book of Common Prayer (1662)**, which is public domain. They stand in for the *Divine Worship* texts until licensing is settled (Q27). The weekday uses the Sunday's collect, as the Prayer Book does ⚑ verify for *Divine Worship*.
- **Hagiography** is limited to what tradition holds and is labelled as such (Simon and Jude in Persia).
- **Lenten array** is a design proposal. Whether OLA keeps the custom is Q30.
- **Notices and events** are placeholders in brackets. The readings link isn't wired yet; the current site uses Universalis.

## Not production

- Content is rendered by JavaScript from a data block, so the concepts can switch days. The real site renders on the server, so the floor works without JavaScript (vision principle 8).
- The fonts are Google Fonts cuts. A real build could license stronger ones (for example a fuller Caslon with true small caps).
- The two Effect Ledger entries (rank-scaled ornament; the rose) are in [`docs/effect-ledger.md`](../../docs/effect-ledger.md) as **proposed**.

## Keep / avoid

*To be filled in after Josh's reaction.*
