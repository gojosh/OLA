# 2026-10-27 — Current-site audit

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- Josh answered Q1, Q6, Q7, and Q10 (saved verbatim in `docs/brief/2026-10-27-answers-1.md`).
- Crawled ourladyoftheatonement.org politely (robots.txt respected, 10 s delay): sitemap plus link discovery, 175 fetches, 83 unique content pages. Checked giving, bulletin, events, and readings embeds in the browser.
- Wrote the audit: platform and systems, the menu as built, the full inventory, content health, parish facts as published, and implications for the IA.
- The parish history page answered Q12: the name comes from the Graymoor tradition.

## What changed
- **Created:** `docs/research/current-site-audit.md`, `docs/brief/2026-10-27-answers-1.md`.
- **Updated:** `open-questions.md` (Q1, Q6, Q7, Q10, Q12 answered; Q20–Q23 added), `02-audiences.md` (school families removed), `03-aesthetic.md` (Josh's Q10 answer; Graymoor confirmed), `04-technology.md` (systems in use; Universalis), `05-information-architecture.md` (links to the audit), `glossary.md`, `explorations/liturgical-system/NOTES.md`, `AGENTS.md` (research folder), `roadmap.md`.

## Open threads
- Urgent and fixable on the current site, independent of the redesign: "in union with Pope Francis" on the home page FAQ; the 2025 holidays PDF; the publicly live `/test` page; the Academy booster-club page.
- Q23 (after-hours emergency route) is a parish process question that the new site depends on.
- Next session: the IA. Start from the audit's §7 and `02-audiences.md` §E.
- A crawler bug, not the site's: `tel:` links were mis-resolved as page paths during the crawl. Nothing in the audit relies on them.

## Addendum: Drupal admin (same session)
- Josh logged into the site's Drupal admin in the browser pane. Read-only review: no traffic reports exist there (only error logs, ~3.7 days, mostly bots); the content list shows 95 pages, 11 unpublished. The Parishioner Business Directory is unpublished, not members-only. Findings are in the audit §8; Q24 (Mass intentions) added.
- Nothing was changed in the admin.
