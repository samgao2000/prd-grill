# Local PRD template (req-dev-lite, English)

Stage 7 generates the PRD from this template. Output to `<project_root>/docs/prd/YYYY-MM-DD-{slug}.md`.

**Contract note**: section numbering, US-NNN heading shape, story field order, and the
Open Items table columns are an **interface contract** consumed by auto-dev-lite step 0.5
and by the prd-gate parser. English and Chinese anchors are both accepted (see
`auto-dev-lite/references/prd-import-rules.md` § Bilingual anchors); do not invent a third variant.

Copy everything from the `---` frontmatter down, and fill in.

```markdown
---
title: <PRD title>
slug: <kebab-case-slug>
created: YYYY-MM-DD
author: <user name or blank>
status: complete | partial   # partial = user stopped mid-session; grounded in answered parts only
final_gate_verdict: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached
gate_mode: prd-gate | self-reported   # prd-gate = independent gate ran merge; self-reported = stage-5 self-review only
gate_aggregate:    # only when gate_mode: prd-gate — copy from .gate.json
gate_confidence:   # only when gate_mode: prd-gate — copy from .gate.json
gate_report:       # only when gate_mode: prd-gate — relative path to .gate.json
methods: [Mom Test, Impact Mapping, 5 Whys, SBE, Cockburn, INVEST, Volere QG]
session_id: YYYY-MM-DD-HHMM-{slug}
snapshot: docs/prd/{slug}-snapshot.md
---

# <PRD title>

> One-line summary: <the user's own words, or close to them>

## 1. Problem Statement

### Business goal (from Impact Mapping)

- **Why**: <the business goal nailed down in stage 1 + how it is quantified>
  - Baseline: <current metric value>
  - Target: <target metric value>
  - Deadline: YYYY-MM-DD
- **Who**: <specific role, down to job title>
- **How**: <behavior change: from X to Y>

### Outcome Metrics (Bucket B)

| Metric | Baseline | Target | Measurement |
|---|---|---|---|
| <metric 1> | X | Y | <how measured> |

### Current state and pain

- <Anecdote 1: when it last happened + concrete steps + cost>

## 2. Solution (candidates, not locked)

> The 5 Whys interceptor has demoted solutions to "implementation candidates".

- **Option A**: <summary> — <why it fits>
- **Rejected for now**: <option killed by 5 Whys + reason>

## 3. User Stories (Bucket A)

Every story uses the full structure (INVEST + Gherkin + Cockburn Extensions + Volere QG
self-check + bucket assignment). One-line "As a..., I want..." is **not allowed**.

### US-001: <short title>

**As** <specific role>, **I want** <action + object>, **so that** <observable value>.

**Traceability**: Why=<OKR-XX>, Who=<role>, How=<X -> Y>

**INVEST**: [x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC** (must contain real values):
```gherkin
Scenario: <noun-phrase scenario name>
  Given <initial state, down to field values>
  When <user action, down to click/input>
  Then <observable result, down to displayed text/data change/status code>
```

**Extensions (unhappy paths)**:
- 1a. <step 1 fails/times out> -> <specific behavior>
- 2a. <step 2 fails> -> <specific behavior>

**Volere QG**: [x] Testable [x] Traceable [x] Solution-free [x] No weasel words

**Bucket assignment**: Bucket A (has Gherkin with concrete values)

---

### US-002: ...

## 4. Implementation Decisions

| ID | Decision | Alternatives | Rationale | ADR |
|---|---|---|---|---|
| D-001 | <summary> | <alternatives> | <why> | <ADR path or N/A> |

## 5. Testing Decisions

### Unhappy-path coverage

| Story | Main-flow test | Extensions tests | Coverage |
|---|---|---|---|
| US-001 | T-001 | T-001a, T-001b | 2/2 |

### Specification by Example consistency

Pick one: (a) run Gherkin directly (Cucumber/Behave); (b) hand-translate Gherkin to test
code; (c) Gherkin as spec only, tests reviewed against it.

## 6. Out of Scope

### Explicitly discarded requirements

- <requirement X>: discard reason [Overreach / Fallacy / Untestable / User withdrew / Other]

## 7. Further Notes

### Session metadata

- Grilling session date: YYYY-MM-DD
- Methods used: <list>
- Session duration: ~NN minutes
- Final gate rounds: N/3
- Snapshot: [<slug>-snapshot.md](./<slug>-snapshot.md)

## 8. Open Items (Bucket C — replaces the issue tracker in lite)

Every row MUST have an owner + deadline + trigger context + current best assumption.
Rows missing owner or deadline get 24h to be completed, otherwise cut.

| ID | Title | Stage | Type | Owner | Deadline | Best assumption | Impact | Status |
|---|---|---|---|---|---|---|---|---|
| OI-001 | <summary> | Stage X | decision/data/stakeholder/tech/legal/other | @user or [TBD-by-YYYY-MM-DD] | YYYY-MM-DD | <PRD fallback assumption> | <which stories/ACs> | open / [resumable] / resolved / still-open |
```

## Hard rules (same as the Chinese template)

1. Story bodies are the import source for auto-dev-lite — field order is fixed, do not omit or reorder.
2. Open Items stays at the END of the PRD.
3. Bucket C rows with both owner and deadline TBD do not enter the PRD — back to stage 6.
4. The PRD filename must contain the date: `docs/prd/2026-06-10-todo-filter.md`.
