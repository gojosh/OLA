# Decision records

A decision record captures one decision: the context, what was decided, and what follows from it. Records are numbered and never deleted. If a decision changes, write a new record that **supersedes** the old one and update the old one's status line to point at it.

Only Josh can accept a decision. An agent may draft a record with status `proposed`.

## Index

| # | Decision | Status |
|---|----------|--------|
| [0001](0001-project-knowledge-lives-in-the-repo.md) | Project knowledge lives in the repo, in a fixed structure | Accepted |
| [0002](0002-existing-concepts-are-reference-not-foundation.md) | Existing concepts are reference, not a foundation | Accepted |
| [0003](0003-start-fresh-content-earns-its-way-in.md) | Start fresh: existing content earns its way in | Accepted |
| [0004](0004-ia-direction-today-and-five-sections.md) | IA direction: a *Today* home page and five sections | Accepted (direction) |
| [0005](0005-traditional-terms.md) | Traditional terms, and the high-church term when in doubt | Accepted |
| [0006](0006-sacraments-say-what-only-we-can-say.md) | Sacraments: say what only we can say | Accepted |
| [0007](0007-tools-in-python-with-uv.md) | Small tools live in `tools/`, in Python, run with uv | Proposed |
| [0008](0008-font-approach.md) | How the Pugin fonts are made | Accepted |
| [0009](0009-lombardic-stem-weights.md) | Two stem weights in Pugin Lombardic | Accepted |
| [0010](0010-adjustments-by-hand.md) | Adjustments by hand: recorded moves on top of the construction | Accepted |

## Template

Copy into `NNNN-short-kebab-title.md`:

```markdown
# NNNN — <Decision in a few words>

- **Status:** proposed | accepted | superseded by [NNNN](NNNN-….md)
- **Date:** YYYY-MM-DD
- **Decided by:** Josh Goforth

## Context
What situation or question forced a decision? Link the brief, docs, or explorations involved.

## Decision
What we're doing, stated plainly.

## Consequences
What follows: what becomes easier, what becomes harder, what we've ruled out.
```
