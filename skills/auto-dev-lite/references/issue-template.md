# Local Issue File Template

One file per issue: `<target_project>/local-issues/00N-{slug}.md`. The `00N` prefix
sets execution order (lowest-numbered ready issue runs first).
Chinese version: [issue-template.zh.md](issue-template.zh.md).

```markdown
---
id: US-001                 # matches the PRD's US-NNN (copied verbatim at import)
title: <short issue title>
status: ready              # ready | in_progress | done | blocked | needs-review
tier: medium               # low | medium | high (initial guess; step 3 re-evaluates)
depends_on: []             # [US-NNN, ...] — all must be done before selection
acceptance_tests: null     # filled once tests exist, e.g. tests/test_us001_login.py
run_id: null               # filled when the run starts
---

# US-001: <issue title>

[Full user story body. Step 0.5 copies the 7 fields verbatim from the PRD:
**As/I want/so that** → **Traceability** → **INVEST** → **Gherkin AC** →
**Extensions (unhappy paths)** → **Volere QG** → **Bucket assignment**]
```

## Status semantics (state machine)

| Transition | Trigger |
|---|---|
| `ready` → `in_progress` | step 2 starts the run |
| `in_progress` → `done` | pytest green + commit/ledger entry written |
| `in_progress` → `blocked` | acceptance test failed hard-stop / pipeline cannot continue; body gains `## Block reason` |
| `in_progress` → `needs-review` | tier=high (no auto-commit) or an M5 soft-escalate |

## Bucket-C (Open Item) issues differ

- Filename `00N-OI-NNN-{slug}.md`; `id` keeps the PRD's `OI-NNN`
- `status` is always `blocked` (no Gherkin AC — must never be picked by step 1)
- Body carries the 9 original table columns verbatim + a `## How to unblock` section
