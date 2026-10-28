# Effect Ledger

Every non-trivial visual or technical effect is justified here before it's built into the site (AGENTS.md §4.5; template in [`foundations/04-technology.md`](foundations/04-technology.md) §2). Concept explorations may try an effect first, but the effect enters the build only once its entry is approved.

## Ornament scaled by the day's rank
- **Status:** proposed (tried in `explorations/home-page-concepts/`, both concepts)
- **What it is:** the amount of ornament on the page is set by the liturgical calendar. In Folio this includes the day's altar frontal, drawn after plates 07 and 74. A feria gets plain rules. A Sunday gets cresting in the day's color. A feast adds gold. A solemnity adds diapering and jewels. Lent strips color and gold for linen marked in red and black. The ornament is drawn as SVG vectors after Pugin's *Glossary*.
- **The good it serves:** the day's dignity is legible at a glance, even to someone who can't name it. Regular visitors learn the calendar by seeing it. The site keeps the same propriety the church does: plain on a Tuesday, fully vested on a solemnity.
- **For whom:** everyone, in either mode; most of all parishioners and the liturgically curious. Visitors on a task lose nothing, because the ornament never sits between them and the times.
- **Pugin test:** propriety. It enriches real things: the top edge of the page, the side of the main panel, the first letter of the feast's name. It is never a free-floating frame.
- **Degrades to:** plain rules in the day's color. The day's name, rank, and color are always stated in text. No motion is involved.
- **Cost:** a few kilobytes of inline SVG. No images, no JavaScript needed once rendered on the server. The calendar engine supplies rank and color anyway.
- **Kill criterion:** visitors find it distracting or "costume-like," or editors can't keep the calendar data correct enough for the ornament to be truthful.

## Turning to another day
- **Status:** proposed (tried in `explorations/home-page-concepts/a-folio.html`)
- **What it is:** when someone turns to the previous or next day (arrows by the folio number, ← → keys, or a day in the week's kalendar), the main panel slides about 28 px and cross-fades in the direction of travel over about a third of a second. It uses the browser's View Transitions API.
- **The good it serves:** it tells the reader that they moved through time, and in which direction, so a changed date isn't missed. A common task is "what's on tomorrow?", and the page reads as one continuous book of days rather than a set of separate pages.
- **For whom:** parishioners and regular visitors planning ahead; anyone browsing the calendar.
- **Pugin test:** convenience. It clarifies a real action (moving between days) and adds no ornament.
- **Degrades to:** an instant change, for anyone with reduced motion set and in browsers without view transitions. Every day stays a plain, linkable page.
- **Cost:** a few lines of CSS and JavaScript; nothing to download.
- **Kill criterion:** people find it slow or distracting, or it gets in the way of screen readers.

## The year as a rose window
- **Status:** proposed (tried in `explorations/home-page-concepts/b-tracery.html`)
- **What it is:** an SVG drawing of the Christian year as a rose window. There is one light per week, glazed in its season's color, with the seasons named on an inner ring and a hand pointing to today. It is generated from the calendar, not drawn by hand.
- **The good it serves:** it shows something a list can't: where today stands in the whole year, how long the seasons are relative to one another, and what's coming. It teaches the shape of the Christian year to newcomers, using the Gothic form the parish's tradition built for light.
- **For whom:** discerning visitors (inquirers, pilgrims) and parishioners; it's secondary for visitors on a task.
- **Pugin test:** construction and convenience. It enriches real data (the calendar). Its form comes from tracery geometry rather than being applied to it.
- **Degrades to:** a text caption ("The Christian year 2025–26 · week 48 of 52 · Time after Trinity"). The SVG carries an equivalent accessible label. No motion is involved.
- **Cost:** under 10 KB of script and markup in the concept. Server-side rendering would remove the script. The real calendar engine supplies the data.
- **Kill criterion:** people read it as decoration rather than information, or it can't be kept accurate to the Ordinariate calendar.
