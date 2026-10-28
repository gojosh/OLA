# Decision records

A decision record captures one decision: the context, what was decided, and what follows from it. Records are numbered and never deleted. If a decision changes, write a new record that **supersedes** the old one and update the old one's status line to point at it.

Only Josh can accept a decision. An agent may draft a record with status `proposed`.

## Index

| # | Decision | Status |
|---|----------|--------|
| [0001](0001-project-knowledge-lives-in-the-repo.md) | Project knowledge lives in the repo, in a fixed structure | Accepted |
| [0002](0002-existing-concepts-are-reference-not-foundation.md) | Existing concepts are reference, not a foundation | Accepted |

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
