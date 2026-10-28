# 0002 — Existing concepts are reference, not a foundation

- **Status:** accepted
- **Date:** 2026-10-27
- **Decided by:** Josh Goforth

## Context
The repository started with a folder of earlier concept work: AI-generated home-page images and two HTML concepts made with Claude. Josh: "that is just fodder, not a starting point." Of the AI images: "they almost represent what we don't want." Of `liturgical-system`: it "has elements about it which were in the ballpark."

## Decision
- Earlier concepts move to `explorations/`, each with a `NOTES.md` verdict. They are studies, not a codebase to build on.
- `explorations/ai-image-concepts/` is an **anti-reference**: useful only as a clear picture of what to avoid.
- `explorations/liturgical-system/` is a **partial reference**: some of its ideas carry forward (see its `NOTES.md` and `docs/foundations/03-aesthetic.md` §2). Its code does not.

## Consequences
- No agent should extend, restyle, or "clean up" an exploration as a route to the real site.
- Ideas from explorations carry forward only when restated in a foundation doc or a decision record.
