# AGENTS.md — onboarding for any AI agent working on this project

You are joining the overhaul of the website for **Our Lady of the Atonement** (OLA), a Catholic parish of the Personal Ordinariate of the Chair of St. Peter in San Antonio, Texas. The goal, in the project lead's words, is "ideally, the best catholic church website ever made."

The project lead is **Josh Goforth**. He makes the decisions. Your job is to help him get there with rigor, taste, and honesty, and to leave things so the next agent can pick up without asking him to repeat himself.

This file is tool-agnostic. `CLAUDE.md` imports it; other tools (Codex, Cursor, Gemini, etc.) read it directly.

---

## 1. Where we are

See [`docs/roadmap.md`](docs/roadmap.md) for the current phase and what's next. As of the last update, the foundations are drafted, the IA direction is accepted (a *Today* home page and five sections, decision 0004), and sections are being designed one at a time. No stack has been chosen and no code written.

Then read the most recent entry in [`docs/log/`](docs/log/) to see what the last session did and left open.

## 2. Read these first, in order

| # | File | Why |
|---|------|-----|
| 1 | [`docs/brief/`](docs/brief/) | Josh's own words, verbatim. The primary source for intent. |
| 2 | [`docs/foundations/01-vision.md`](docs/foundations/01-vision.md) | The ambition and the governing principles. |
| 3 | [`docs/foundations/02-audiences.md`](docs/foundations/02-audiences.md) | Who the site serves. |
| 4 | [`docs/foundations/03-aesthetic.md`](docs/foundations/03-aesthetic.md) | English-Catholic: what it means and what it doesn't. |
| 5 | [`docs/foundations/04-technology.md`](docs/foundations/04-technology.md) | Technology principles and the Effect Ledger. |
| 6 | [`docs/foundations/05-information-architecture.md`](docs/foundations/05-information-architecture.md) | Navigation and structure (in progress). |
| 7 | [`docs/decisions/`](docs/decisions/) | What has been decided. Don't re-argue these (see §4). |
| 8 | [`docs/open-questions.md`](docs/open-questions.md) | What's still unknown. Check before you guess. |
| — | [`docs/sections/`](docs/sections/) | Detailed design for each site section (e.g. Sacraments). Read the one for any section you're working on. |
| — | [`docs/research/`](docs/research/) | Discovery findings, starting with the audit of the current site. Its §6 holds parish facts as published: use them instead of inventing placeholders. |
| — | [`docs/glossary.md`](docs/glossary.md) | Liturgical, architectural, and Ordinariate terms, and the **usage list** of which term we use. Look things up here before writing about them. |

## 3. Repository map

```
AGENTS.md            ← you are here (canonical agent onboarding)
CLAUDE.md            ← imports AGENTS.md, plus Claude-specific notes
README.md            ← the front page for people
docs/
  brief/             ← Josh's words, verbatim, dated. NEVER edit.
  foundations/       ← numbered foundation docs (vision → IA)
  decisions/         ← numbered decision records (ADRs)
  log/               ← one dated entry per working session
  roadmap.md         ← phases; what's happening now and next
  open-questions.md  ← questions waiting on Josh or on research
  glossary.md        ← domain vocabulary, and the usage list of which term we use
  effect-ledger.md   ← every non-trivial effect, justified before it is built
  research/          ← discovery findings (e.g. the current-site audit)
  sections/          ← one design doc per site section, written before its pages
reference/           ← outside source material (inspiration, not templates)
  pugin-glossary/    ← Pugin's 1844 Glossary plates + viewable previews
explorations/        ← concept work made for this project, each with a verdict
tools/               ← small utilities (e.g. tools/flatten: unrolls the Pugin plates), each with a README
```

No `site/` or `src/` folder exists yet. When a codebase starts, it gets its own folder and a decision record explaining the stack.

## 4. Rules of engagement

**4.1 Josh's words are canonical. Your synthesis is a proposal.**
Everything under `docs/brief/` is verbatim and must never be edited. Add a new dated file when Josh gives significant new direction. Foundation docs separate **"What Josh has said"** from **"Working proposals"**. Proposals stay proposals until Josh ratifies them; when he does, update the doc's status and, if it's a real choice, write a decision record.

**4.2 Decisions live in `docs/decisions/`, not in chat.**
If a conversation settles something, record it (template in [`docs/decisions/README.md`](docs/decisions/README.md)). Accepted decisions are not re-argued in passing. If you think one is wrong, say so and propose a new record that supersedes it; don't quietly work around it.

**4.3 Questions live in `docs/open-questions.md`.**
When you hit something only Josh or the parish can answer, add it there instead of guessing. When it's answered, move it to the "Answered" section with the answer and the date.

**4.4 Never invent parish facts.**
Mass times, clergy names, history, ministries, phone numbers, quotations: if you didn't get it from Josh, the parish, or a cited source, don't state it as fact. Mark unverified claims with **⚑ verify**. Placeholder content in prototypes must look like placeholder content (e.g. `[MASS TIME]`), never plausible fakes.

**4.5 Every effect earns its place.**
Josh: "always, ALWAYS in service of some specific and known good for the user, never just because." Any non-trivial visual or technical technique (WebGL, shaders, animated SVG, scroll-driven motion, custom cursors, 3D, sound) needs an Effect Ledger entry (see `04-technology.md`) **before** it's built: what good it serves, for which audience, how it degrades, and what it costs.

**4.6 Reference is not a template. Explorations are studies, not foundations.**
`reference/` is source material to learn from. `explorations/` holds earlier concepts, each with a `NOTES.md` verdict. Read the verdict before using anything from them. Never build on top of an exploration's code without a decision record saying so.

**4.7 Theology, liturgy, and copyright need care.**
- Use liturgical and theological terms precisely (check the glossary). Doctrinal and liturgical content must eventually be reviewed by the clergy; flag anything substantive for that review.
- Don't reproduce copyrighted liturgical texts (Divine Worship, ICEL, modern translations of Scripture) without confirming licensing. Public-domain sources (e.g. Pugin, Guéranger, the 1662 BCP in most contexts) are fine; cite them.
- Don't fabricate quotations from saints, popes, or Scripture. Cite edition and location.

**4.8 Privacy.**
Never put real parishioner data (names, contact details, records, photos of identifiable people, anything about minors) into this repository.

**4.9 Leave a trail.**
At the end of a working session:
1. Add a dated entry to `docs/log/` (template in [`docs/log/README.md`](docs/log/README.md)): what happened, what changed, what's open.
2. Update the "Now / Next" section of `docs/roadmap.md` if the phase or focus moved.
3. Add or close items in `docs/open-questions.md`.

## 5. Conventions

- **Files and folders:** `kebab-case`. Dates are ISO `YYYY-MM-DD`. Numbered series use zero-padded prefixes (`01-`, `0001-`).
- **Doc front matter:** every doc in `docs/foundations/` starts with:
  ```yaml
  ---
  title: …
  status: draft | proposed | accepted | superseded
  updated: YYYY-MM-DD
  ---
  ```
  `draft` = still being shaped. `proposed` = ready for Josh to ratify. `accepted` = ratified. `superseded` = replaced (link the successor).
- **Markers:** **⚑ verify** = unconfirmed fact. **⚑ Josh** = needs Josh's call (also list it in open-questions).
- **Images for agents:** most tools can't open `.jp2` or `.heic`. Use the JPEG previews in `reference/pugin-glossary/previews/`, or the contact sheet, and keep originals alongside. Do the same for any new reference material: originals plus web-viewable previews.
- **Writing style:** plain, specific, no marketing voice. Short sentences. Precise terms. If a sentence would fit on any church's website, it's not good enough for this one.
- **Traditional terms:** the parish is traditional. For technical things (rites, sacraments, seasons, objects, places), use the traditional term that is still in living use; when in doubt, the high-church one: "Holy Communion," not "the Eucharist." Traditional is not antiquated: don't revive names the Church has retired ("Holy Unction"). Check the usage list at the top of [`docs/glossary.md`](docs/glossary.md) before writing copy or docs (decision 0005).
