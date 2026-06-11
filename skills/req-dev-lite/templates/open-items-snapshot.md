# Open-Items Snapshot Template (lite)

Generated at session end → `<project_root>/docs/prd/{slug}-snapshot.md`.
Chinese version: [open-items-snapshot.zh.md](open-items-snapshot.zh.md).

**Lite-specific**: no issue-tracker links; the authoritative Bucket-C carrier is the
PRD's trailing Open Items table — the snapshot is session history + resume state.
One snapshot per slug, **overwritten** on each (re)run.

```markdown
# Requirements session snapshot (lite) — {slug}

**PRD**: [YYYY-MM-DD-{slug}.md](./YYYY-MM-DD-{slug}.md)
**Slug**: {kebab-case-slug} (resume key)
**First session**: YYYY-MM-DD HH:MM · **Last updated**: YYYY-MM-DD HH:MM
**Total sessions**: N (original + resumes) · **Total time**: ~NN minutes
**Methods enabled**: Mom Test + Impact Mapping + 5 Whys + SBE + Cockburn + INVEST + Volere QG (+ optional X/Y)
**Final gate verdict**: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached (+ gate_mode)

---

## Resume info (only when the last session was stopped; otherwise N/A)

- **Status**: completed | paused | aborted
- **Stop reason**: `user_initiated` | `agent_failed` | `not_applicable`
- **Pending stage**: N (1/2/2.5/3/4/4.5/5)
- **Pending items** (unanswered questions, item-level; also in the PRD Open Items table tagged `[resumable]`):
  - [ ] [question 1] — expected answer shape: [recommended-answer summary]
- **Resumable slug**: {slug} ("continue req-dev-lite {slug}" finds this snapshot)
- **Resume rule**: read this section first, continue from pending_stage, ask pending_items first — never restart.

---

## Bucket tally (last session)

- Bucket A (Gherkin AC → PRD User Stories): N
- Bucket B (Outcome metrics → PRD Problem Statement): N
- Bucket C (Open items → PRD trailing table): N
- Discarded (no bucket → PRD Out of Scope): N

## Bucket C digest (authoritative copy lives in PRD § 8)

| OI-ID | Title | Stage | Owner | Deadline | Status |
|---|---|---|---|---|---|
| OI-001 | <summary> | Stage X | @user or [TBD] | YYYY-MM-DD | open / `[resumable]` / resolved / still-open |

## Decisions resolved in-session (formal record: PRD Implementation Decisions)

### D-001: <summary>
- **Decision**: <conclusion> · **Rationale**: <why, which stage>

## Anti-patterns hit (team learning; counts live in the retro)

- [ ] Compliment trap — N · [ ] Future-tense — N · [ ] Solution-as-requirement — N
  (which solutions got demoted?) · [ ] Abstract AC — N (which weasel words → fixed how?)
  · [ ] Happy-path — N

## Session history (reverse chronological — append per run)

### Run 2 (resumed) — YYYY-MM-DD HH:MM
- Status: completed · Resumed from: <session id> · Resolved OI-NNN · Added OI-XXX

### Run 1 — YYYY-MM-DD HH:MM
- Status: paused (user_initiated) · Stuck at stage X · Produced N stories, N OIs

## Prep for next session

- [ ] OI-XXX owner reply → next session opener
- [ ] OI-YYY data pull → after SQL
- [ ] Stage-1 Why/Who/How is locked — do not re-litigate
```
