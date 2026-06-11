# req-dev-lite sessions/

After every req-dev-lite session, stage 8 automatically writes one retrospective
into this folder. Chinese version: [README.zh.md](README.zh.md).

## What this folder is for

- Feeding retro aggregation (a SKILL.md change is only proposed after ≥3 signals point the same way)
- Letting humans review past decisions and anti-pattern trends
- Cross-member collaboration (git-tracked, so multiple machines/sessions aggregate)

## Relationship to the full req-dev

`skills/req-dev/sessions/` (full version, not in this repo) and this folder are
**two independent retro pools** — never read them as one.

- Running `req-dev` (full) → writes to `skills/req-dev/sessions/`
- Running `req-dev-lite` (this skill) → writes here

The `req-dev-retro` skill reads both pools but keeps the signal pools **separated
by skill of origin**: lite signals only ever change lite's SKILL.md / references /
templates; full signals only change full's. No cross-contamination — propagating a
methodology change across skills requires the user's explicit confirmation at
retro time (a separate diff is proposed per skill).

## What this folder is NOT for

- ❌ Raw transcript archive (privacy + git size)
- ❌ Task tracker (tasks live in the PRD's trailing Open Items table)
- ❌ A basis for the agent to modify the skill on its own (every change passes the human-reviewed retro gate)

## File naming

```
YYYY-MM-DD-HHMM-{slug}.md
```

- `slug` is kebab-case, a short form of the PRD topic (e.g. `todo-tag-filter`)
- The time is the session **start** (not end — keeps sort order sane)
- A resumed session gets a **new start time** in its name (not the original's) and
  records the original session_id in its frontmatter `resumed_from` field

## Template

See `_template.md`. **Copy** it for each new session; never edit the template itself.

## The improvement loop

```
req-dev-lite finishes → stage 8 writes the retro automatically → sessions/*.md
                                              ↓
                                (N sessions accumulate)
                                              ↓
user explicitly triggers the retro skill (pointing at this sessions/ path)
        → aggregates ≥3 same-direction signals
                                              ↓
                          proposes a concrete diff to the user
                                              ↓
        user says yes  → applied to SKILL.md / templates
        user says no   → recorded in retro's proposals-log.md rejection section
                         (so the same proposal is never re-raised)
        user edits it  → the edited version is applied
```

## Git policy

This folder is **tracked** (not gitignored). Rationale: multi-machine sessions
aggregate; team members see each other's session feedback; files contain only
structured data, no PII by design.

If a session involved sensitive information (company confidential, client names,
contract amounts), the retro **redacts or omits it at write time** — the fix is
never "gitignore the whole file".
