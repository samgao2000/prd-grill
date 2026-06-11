---
session_id: YYYY-MM-DD-HHMM-{slug}
date_start: YYYY-MM-DD HH:MM
date_end: YYYY-MM-DD HH:MM
duration_minutes: NN
slug: {kebab-case-slug}
status: completed | paused | aborted | escalated
stop_reason: not_applicable | user_initiated | agent_failed
pending_stage: N | null   # stage number, only when status=paused
resumed_from: YYYY-MM-DD-HHMM-{original slug} | null   # only when this session is a resume
prd_file: docs/prd/YYYY-MM-DD-{slug}.md | null   # lite: a local path, not an issue
snapshot_file: docs/prd/{slug}-snapshot.md | null
final_gate_verdict: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached
---

> **status / stop_reason matrix**:
> - `completed` + `not_applicable`: ran to the end — buckets settled, final gate passed
> - `paused` + `user_initiated`: user stopped (fatigue/priority/time), intends to resume
> - `paused` + `agent_failed`: the agent got stuck in a loop / couldn't land its questions — a retro improvement signal
> - `aborted` + any: session voided, no resume intended (e.g. the requirement was killed)
> - `escalated` + any: escalated to a human decision; this skill no longer applies

# Retrospective: {short title}

> This is the req-dev-**lite** retro. Lite lands the PRD as a local file rather than
> an issue, so `prd_file` / `snapshot_file` are local paths. All other fields match
> the full version.

## Methods enabled

**Core (always)**:
- [x] Mom Test
- [x] Impact Mapping
- [x] 5 Whys
- [x] Specification by Example (Gherkin)
- [x] Cockburn Extensions
- [x] INVEST
- [x] Volere QG

**Optional (signal-triggered)**:
- [ ] Event Storming — trigger signal: [fill] | not triggered
- [ ] JTBD/ODI — trigger signal: [fill] | not triggered
- [ ] KAOS goal trees — trigger signal: [fill] | not triggered
- [ ] Continuous Discovery / OST — trigger signal: [fill] | not triggered
- [ ] Critical Decision Method — trigger signal: [fill] | not triggered

## Stage timings (estimated)

| Stage | Minutes | Notes |
|---|---|---|
| 1 opening four | | |
| 2 grilling loop | | |
| 2.5 5 Whys interceptions | | times triggered: N |
| 3 domain calibration | | CONTEXT.md inline updates: N |
| 4 structuring user stories | | |
| 4.5 unhappy paths | | |
| 5 final review | | rounds to pass: N/3 |
| 6 bucket triage | | |
| 7 landing (local PRD file + gate) | | |
| 8 retro (this step) | | automatic, not counted |

## Stop scenario (only when status ≠ completed)

> Sessions with `status=completed` write `not_applicable` here.

- **Stop reason**: user_initiated | agent_failed
- **Pending stage**: N (stage at interruption)
- **Trigger phrase / situation**:
  - if `user_initiated`: the user's own words ("park it", "I'm tired", "just generate the PRD")
  - if `agent_failed`: the self-check trigger (N consecutive stuck turns / loop / evasive answers)
- **Pending items count**: N items into Bucket C (tagged `[resumable]` in the PRD's Open Items table)
- **Resume path**: the user says "continue req-dev-lite {slug}"; the agent reads the Resume section of `docs/prd/{slug}-snapshot.md`
- **If agent_failed**: this stop is itself a retro improvement-signal source — it MUST be tagged with a [SIG-N] in the signals section below

---

## Bucket tally

| Bucket | Count | Share |
|---|---|---|
| A (Gherkin AC → PRD User Stories) | N | NN% |
| B (Outcome metric → PRD Problem Statement) | N | NN% |
| C (Open items → PRD § 8 table) | N | NN% |
| Discarded (→ PRD § 6 Out of Scope) | N | NN% |

> Bucket C above 30% is an anomaly signal — the requirement isn't mature; resolve
> the open items before the next session. For a `paused` session the C share
> includes pending_items; don't misread that as a maturity problem.

## Anti-pattern hits

| Anti-pattern | Hits | Notes (which solutions were demoted / which weasel words fixed) |
|---|---|---|
| Compliment trap | N | |
| Future-tense trap | N | |
| Solution-as-requirement | N | 5 Whys demoted [solution X] to outcome [Y] |
| Abstract AC | N | weasel words fixed: [list] |
| Happy-path trap | N | branches added at stage 4.5 |

## Friction points

> Steps that took **more than 2 turns** to advance. What stuck, why, how it was resolved.

### Friction-1
- **Stage**:
- **Symptom**: the user repeatedly couldn't give a concrete answer to [question/concept]
- **Cause**: user didn't understand | agent asked unclearly | method doesn't apply | missing project context | other
- **Resolution**: rephrase / give an example / check the code / move on and return / other
- **If the method itself is suspect**: tag [SIG-N] and add to the signals section

### Friction-2
...

## User feedback, verbatim

> Direct quotes, **never paraphrased**. Redact PII only (names/emails).

- "..." (stage N)
- "..." (stage N)

## Agent self-assessment

### Questions that worked
- [ ] stage X's "..." got an instant, concrete answer
- [ ] stage Y's code cross-check punctured a disguised requirement in one move

### Questions that struggled
- [ ] stage X's "..." took the user 3 turns to parse → candidate [SIG-N]
- [ ] stage Y missed asking [...] — noticed only afterwards

### Over-asking
- [ ] stage X asked N questions the code could have answered
- [ ] kept probing a user story that was already clear

### Lite-specific checks
- [ ] the user asked "why no issues?" — lite was the wrong pick, should have been full req-dev; record the situation so retro can sharpen the description triggers
- [ ] an Open Items row with owner=TBD sat unfilled past 24h — the owner-field mandate wasn't communicated hard enough; tag [SIG-N]

## Improvement signal candidates

> ⚠️ Do **not** edit SKILL.md/templates here. Signals only; the retro skill
> proposes changes after ≥3 signals point the same way.

Format: `[SIG-N] description + evidence + suggested direction`

- [SIG-1] stage X's question "..." routinely confuses users. Suggest rewording to "..." or splitting in two. Evidence: this session's friction-1.
- [SIG-2] optional module [X]'s trigger is unclear; it should have fired this session and didn't. Suggest a trigger example in methods.md §X. Evidence: stage 1 miss cost N minutes of stage-3 repair.
- [SIG-3] ...

## Metadata notes

Anything that fits no section above (project peculiarities, user's state that day, external interruptions).
