# 2026-10-27 — Project setup

**Agent/tool:** Claude Code (Opus 5.5)

## What happened
- Josh gave the kickoff brief (audiences, aesthetic, tech, IA) and said the existing files were fodder, not a starting point. The AI-image concepts are close to what he *doesn't* want; `liturgical-system` had elements in the ballpark.
- Reviewed all existing material: six AI mockups, two HTML concepts, 75 photographed plates from Pugin's *Glossary* (1844).
- Set up the project structure and conventions for multi-agent onboarding (decision 0001).
- Drafted all five foundation docs, with Josh's words kept separate from agent proposals.

## What changed
- **Created:** `AGENTS.md`, `CLAUDE.md`; `docs/` (brief, foundations 01–05, decisions 0001–0002, roadmap, open questions, glossary, log); READMEs for `reference/` and `explorations/`; a `NOTES.md` verdict for each exploration.
- **Moved:** `pugin-glossary-of-ecclesiastical-ornament-and-costume/` → `reference/pugin-glossary/plates/`; `site-concepts/claude-site-concepts/*` → `explorations/`; `site-concepts/nano-banana-home-page-concepts/` → `explorations/ai-image-concepts/`.
- **Generated:** `reference/pugin-glossary/previews/` (75 × 1200 px JPEG) and `contact-sheet.jpg`.
- **Rewrote:** `README.md`, `.gitignore`. Stopped tracking `.DS_Store` files.

## Open threads
- Josh to react to the drafts, especially: audience additions (`02-audiences.md` §B), the porch-to-altar model (§C), the remembered-state tiers (§D), and the proposed principles 5–9 in `01-vision.md`.
- Next session: information architecture. Most useful inputs: current site URL and analytics (Q6), the systems in use (Q7), and whether the Academy is in scope (Q1).
- Repository: decide how to handle large binaries (Q18).
