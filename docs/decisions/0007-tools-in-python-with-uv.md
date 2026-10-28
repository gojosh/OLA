# 0007 — Small tools live in `tools/`, written in Python and run with uv

- **Status:** proposed
- **Date:** 2026-10-28
- **Decided by:** Josh Goforth (to ratify)

## Context
Recovering Pugin's alphabets as fonts starts with flattening the photographed plates. That needs numerical work: camera models, least-squares fitting, and image resampling. AGENTS.md says a codebase gets its own folder and a decision record explaining the stack. The website's stack is still undecided (Phase 3), and this tool shouldn't wait for it or constrain it.

## Decision
- Utilities that work on project material, not the website, live in `tools/<name>/`, each with a README.
- They are written in Python. Dependencies are declared inline in the script (PEP 723), so `uv run tools/<name>/<script>.py` works with no setup and no virtual environment checked in.
- Any browser interface a tool needs is a single HTML file served by the tool itself, with no build step.
- Their data lives next to the material it describes (e.g. `reference/pugin-glossary/flatten/`). Large regenerable outputs stay out of git until Q18 is settled.

## Consequences
- `uv` is needed to run tools; it installs Python and the packages on first run.
- These tools commit the project to nothing about the website's stack.
- First tool: [`tools/flatten`](../../tools/flatten/README.md).
