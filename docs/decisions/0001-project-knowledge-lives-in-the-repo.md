# 0001 — Project knowledge lives in the repo, in a fixed structure

- **Status:** accepted
- **Date:** 2026-10-27
- **Decided by:** Josh Goforth (delegated: "set up the project such that other LLMs can onboard as needed along the way easily")

## Context
The project will span many working sessions with different AI agents and tools. Chat history doesn't carry over between them, and summaries drift from what was actually said. Without a shared, durable record, every new agent would re-ask settled questions or quietly reinterpret the brief.

## Decision
- All project knowledge lives in this repository as plain Markdown.
- `AGENTS.md` is the canonical, tool-agnostic onboarding; `CLAUDE.md` imports it.
- Josh's direction is stored **verbatim** in `docs/brief/` and never edited. Everything else cites it.
- Foundation docs separate **what Josh has said** from **working proposals**.
- Decisions are recorded in `docs/decisions/`; open questions in `docs/open-questions.md`; each session leaves an entry in `docs/log/`; the current phase is in `docs/roadmap.md`.
- Outside source material goes in `reference/`, with web-viewable previews next to any original an agent can't open. Concept work goes in `explorations/`, each with a `NOTES.md` verdict.

## Consequences
- Any agent can get up to speed by reading `AGENTS.md` and following its reading order.
- Intent can always be traced back to Josh's own words.
- There is overhead: each session has to update the log, the roadmap, and open questions. That cost is accepted.
