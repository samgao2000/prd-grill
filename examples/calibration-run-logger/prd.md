---
title: Calibration Run Logger
slug: calibration-run-logger
created: 2026-06-10
author: Sam Gao
status: complete
final_gate_verdict: PASS-WITH-OPEN-ITEMS
gate_mode: prd-gate
gate_aggregate: 0.9587
gate_confidence: 0.85
gate_report: 2026-06-10-calibration-run-logger.gate.json
methods: [Mom Test, Impact Mapping, 5 Whys, SBE, Cockburn, INVEST, Volere QG, ODI]
session_id: 2026-06-10-2207-calibration-run-logger
snapshot: docs/prd/calibration-run-logger-snapshot.md
---

# Calibration Run Logger

> One-line summary: "I am eager to see if there are correlations between the gate score and the rework effort." — every pipeline run must leave one paired record, so that question gets answered with data instead of belief.

## 1. Problem Statement

### Business goal (from Impact Mapping)

- **Why**: Upgrade prd-gate from a scorer to a calibrated predictor — publish a correlation analysis of gate score vs. downstream rework in the prd-grill repository.
  - Baseline: 1 gated run total (personal-crm, 2026-05-19); 0 paired (score → rework) records exist; the correlation has never been computed.
  - Target: ≥10 gated runs with paired records, correlation analysis published.
  - Deadline: 2026-09-30
- **Who**: Primary — the agent executing an auto-dev-lite run (emits records automatically, zero operator effort). Secondary — the repository maintainer acting as analyst (consumes the aggregated dataset, and backfills records for runs that crashed without cleanup).
- **How**: Agent: from "run ends at final report + retro, calibration data scattered across gate.json / log.jsonl / ledger / issue files" → "run ends by appending exactly 1 validated paired record to a single dataset file". Analyst: from "correlation impossible without hours of manual archaeology (never done, including for the CRM run)" → "one command yields the paired table + correlation in under a minute".

### Outcome Metrics (Bucket B)

| Metric | Baseline | Target | Measurement |
|---|---|---|---|
| Paired (score → rework) records | 0 | ≥10 by 2026-09-30 | row count of completed+prd-gate records in dataset |
| Record emission compliance | n/a (no mechanism) | 1 record per completed run, 100% | dataset rows vs. run logs cross-check at analysis time |
| Time from "want analysis" to correlation output | hours (manual, never attempted) | < 1 minute | wall-clock of `calib report` at run #5 and #10 |

### Measurement definitions (how outcome counts derive from run artifacts)

- total issues = story issues imported for the run (open-item issues excluded)
- pytest retry cycles = number of failed-test events recorded in the run's event log
- blocked issues = issues whose final status is blocked
- needs-review escalations = issues whose final status is needs-review
- rework_rate = (retry cycles + blocked × 3 + needs-review × 2) / total issues
- quarantine area = the holding place for records that fail integrity validation; quarantined records are excluded from all analysis and disclosed in every report

### Current state and pain

- 2026-05-19 personal-crm run: the gate report (aggregate 0.97) and the run outcomes (8 issues, test retries, escalation events in `runs/*/log.jsonl`) both exist on disk, but pairing them was never attempted because it requires manual archaeology across 4 file types. The correlation question has been open since the gate shipped.
- Design assumption (declared, falsifiable): data capture must cost zero marginal operator effort, or compliance will decay. Basis: the author's appraisal experience across 300+ organizations — treated here as an assumption, not evidence. Falsifier: the "record emission compliance" metric above; if compliance falls below 100% even with automated emission, the assumption and the design both get revisited (see OI-002).

## 2. Solution (candidates, not locked)

> The 5 Whys interceptor demoted the original phrasing ("build a logger tool") to a candidate. The underlying outcome (Ulwick form): **maximize [the number of validated score-rework record pairs] [at zero marginal operator effort per run]**.

- **Option A (selected)**: a record schema documented as a contract + a `calib` subcommand on the existing `prd_gate` package (`add` = validate + append, `report` = paired table + correlation) + one mandatory final step in auto-dev-lite's run procedure. Minimal new surface; enforcement pattern identical to the gate itself; stdlib-only.
- **Rejected — convention only (no code)**: fails the author's own review-failure test: nothing validates compliance, so emission decays into formality.
- **Rejected — standalone calib package/CLI**: cleaner separation but more surface to maintain and a second install step; nothing in the requirements needs it.
- **Rejected — dashboard**: at n=10 a dashboard is theater; a table and one coefficient suffice.

## 3. User Stories (Bucket A)

### US-001: Emit one validated calibration record per completed run

**As** the agent executing an auto-dev-lite run, **I want** to append one schema-validated record pairing the PRD's gate scores with the run's outcome counts (counted per the Measurement definitions in section 1) as the mandatory final step of the run procedure, **so that** calibration data accumulates without any human remembering to do bookkeeping.

**Traceability**: Why=CALIB-2026Q3, Who=run-executing agent, How=scattered fragments → 1 validated record per run

**INVEST**: [x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC** (must contain real values):
```gherkin
Scenario: Completed run appends exactly one record
  Given run 20260610-a1b2c3 completed with 8 issues total, 2 pytest retry cycles, 1 blocked issue, 1 needs-review escalation
    And the source PRD frontmatter has gate_mode "prd-gate", gate_aggregate 0.97, gate_confidence 0.85
    And the calibration dataset contains 4 records
  When the agent performs the record-emission step for run 20260610-a1b2c3
  Then the calibration dataset contains 5 records
    And the new record has rework_rate 0.875 ((2 + 1*3 + 1*2) / 8)
    And the new record carries run_status "completed", gate_mode "prd-gate", and the 11 per-dimension scores copied from the gate report file named in the PRD frontmatter (gate_report)
```

**Extensions (unhappy paths)**:
- 1a. Run's event log missing → emission rejected, nothing appended, error names the missing artifact
- 1b. PRD frontmatter has gate_mode "self-reported" or no gate_mode at all → record written with gate_mode "self-reported", gate_aggregate, gate_confidence and the 11 per-dimension scores set to null, and a warning printed (US-002 requires score fields only when gate_mode is "prd-gate")
- 1c. PRD frontmatter says gate_mode "prd-gate" but the gate_report file is missing or unreadable, or gate_aggregate is absent → emission rejected, nothing appended, error names the missing artifact (precedence: the declared gate_mode governs — a claimed-gated PRD with incomplete gate artifacts is a data error, never silently degraded to self-reported)
- 2a. Calibration dataset does not exist yet → created with the new record as record 1
- 2b. Same run_id already present in the dataset → emission rejected, nothing appended ("duplicate run_id")
- 3a. Run aborted via kill switch → the abort cleanup handler (the same step that marks the issue blocked) performs the record-emission step, writing run_status "aborted"; rework fields filled from log events up to the abort
- 3b. Process died **before** any emission started (crash, no cleanup) → no record exists; the correlation report (US-003 ext 4b) lists runs that have an event log but no dataset record, and the maintainer-as-analyst backfills each via the record-emission step with run_status "aborted"
- 3c. Process died **during** an append → a corrupted record remains in the dataset; handled by US-002 ext 3a (quarantine), not by this story

**Volere QG**: [x] Testable [x] Traceable [x] Solution-free [x] No weasel words

**Bucket assignment**: Bucket A (Gherkin with concrete values)

---

### US-002: Reject malformed records at append time

**As** the repository maintainer acting as analyst, **I want** every append validated against the record schema (required fields present — gate-score fields required only when gate_mode is "prd-gate", null otherwise; enums legal; counts non-negative; rework_rate arithmetic consistent with raw counts), **so that** the dataset stays analyzable at run #10 without a cleaning pass.

**Traceability**: Why=CALIB-2026Q3, Who=maintainer-as-analyst, How=trust-then-clean → reject-at-the-door

**INVEST**: [x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC** (must contain real values):
```gherkin
Scenario: Inconsistent rework arithmetic is rejected
  Given a candidate record with 8 issues total, 2 retries, 1 blocked, 1 needs-review, and rework_rate stated as 0.5
  When validation runs during the record-emission step
  Then the append is rejected
    And the error message states "rework_rate 0.5 != computed 0.875"
    And the calibration dataset is unchanged
```

**Extensions (unhappy paths)**:
- 1a. run_status outside {completed, aborted} → rejected, error lists legal values
- 1b. gate_mode outside {prd-gate, self-reported} → rejected, error lists legal values
- 2a. Negative count in any outcome field → rejected, field named in the error
- 3a. Dataset contains a corrupted record (crash during a previous append, US-001 ext 3c) → emission moves the corrupted record to the quarantine area, appends the new record, and prints "quarantined: 1 record at position N"; appends never stay blocked (owner decision 2026-06-10: quarantine-and-continue)

**Volere QG**: [x] Testable [x] Traceable [x] Solution-free [x] No weasel words

**Bucket assignment**: Bucket A (Gherkin with concrete values)

---

### US-003: One-command correlation report with explicit exclusions

**As** the repository maintainer acting as analyst, **I want** a single-step correlation report giving the paired table, the Pearson and Spearman coefficients of gate_aggregate vs rework_rate, and an exclusion summary (aborted runs, self-reported records), **so that** at run #5 and #10 the correlation check costs under a minute and the analysis cannot silently include invalid points.

**Traceability**: Why=CALIB-2026Q3, Who=maintainer-as-analyst, How=hours of archaeology → one command under a minute

**INVEST**: [x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC** (must contain real values):
```gherkin
Scenario: Report correlates only valid records and names its exclusions
  Given the calibration dataset holds 12 records: 10 with run_status "completed" and gate_mode "prd-gate", 1 "aborted", 1 "self-reported"
  When the analyst requests the correlation report
  Then the paired table lists exactly 10 rows
    And the output contains a Pearson r and a Spearman rho computed over those 10 pairs
    And the output contains the line "excluded: 1 aborted, 1 self-reported"
    And the report completes in under 60 seconds
```

**Extensions (unhappy paths)**:
- 1a. Fewer than 3 valid pairs → table prints, coefficients suppressed with "n < 3: correlation not computed"
- 1b. Zero variance in either column (all scores identical) → coefficients suppressed with the reason
- 2a. Dataset missing entirely → report fails with guidance to record at least one run first
- 3a. Every record has run_status "aborted" or gate_mode "self-reported" (the two exclusion criteria) → table empty, exclusion summary still printed
- 4a. Quarantine area is non-empty → exclusion summary gains a line "quarantined: N" (quarantined records never enter the correlation)
- 4b. A run directory has an event log but no dataset record (US-001 ext 3b) → report lists those run ids under "unrecorded runs" so the analyst can backfill
- 4c. The dataset still holds a corrupted record from a crash-during-append (US-001 ext 3c) and no append has run since → the report excludes it from all counts and prints "corrupted: 1 record at position N (quarantined at next append)"; the report itself never modifies the dataset

**Volere QG**: [x] Testable [x] Traceable [x] Solution-free [x] No weasel words

**Bucket assignment**: Bucket A (Gherkin with concrete values)

## 4. Implementation Decisions

| ID | Decision | Alternatives | Rationale | ADR |
|---|---|---|---|---|
| D-001 | Ride the existing prd_gate package as a `calib` subcommand | standalone package; shell scripts | one install, one CLI, same enforcement pattern as the gate | N/A |
| D-002 | Storage = runs/calibration.jsonl, append-only, one JSON object per line | SQLite; CSV | human-diffable, git-friendly, crash-tolerant appends, n≤100 scale | N/A |
| D-003 | Statistics in stdlib only (Pearson and Spearman computed directly) | scipy/pandas | keeps the package dependency-free; two formulas, ~30 lines | N/A |
| D-004 | Record carries raw counts AND the computed rework_rate; weights (retry 1, blocked 3, needs-review 2) stored in each record | rate only; counts only | raw counts allow re-weighting at analysis time without losing v1 comparability | N/A |
| D-005 | Corruption policy = quarantine-and-continue: corrupted records move to a sibling quarantine file; appends resume immediately (owner decision, 2026-06-10) | fail-closed until manual repair | fail-closed would break the 100% emission-compliance metric after any crash | N/A |

## 5. Testing Decisions

### Unhappy-path coverage

| Story | Main-flow test | Extensions tests | Coverage |
|---|---|---|---|
| US-001 | T-001 | T-001a, T-001b, T-001c, T-001d, T-001e, T-001f, T-001g, T-001h | 8/8 |
| US-002 | T-002 | T-002a, T-002b, T-002c, T-002d | 4/4 |
| US-003 | T-003 | T-003a, T-003b, T-003c, T-003d, T-003e, T-003f, T-003g | 7/7 |

### Specification by Example consistency

Option (b): hand-translate Gherkin into pytest tests; test function names match scenario names; the arithmetic examples above (0.875) appear verbatim in test assertions.

## 6. Out of Scope

### Explicitly discarded requirements

- Dashboard / chart rendering: discarded [Overreach] — at n=10 a table and two coefficients carry the conclusion; revisit only if the dataset grows past ~100 runs.
- Cross-project normalization beyond per-issue rate: discarded [Untestable at n=10] — with heterogeneous projects and n=10, any further normalization is unfalsifiable tuning.
- Automatic detection of post-done fix commits as a rework signal: discarded for v1 [Fallacy risk] — attributing later commits to spec defects requires judgment the data does not support; revisit with OI-002 evidence.

## 7. Further Notes

### Session metadata

- Grilling session date: 2026-06-10
- Methods used: Mom Test, Impact Mapping, 5 Whys, SBE, Cockburn, INVEST, Volere QG + ODI (outcome syntax)
- Session duration: ~35 minutes (6 questions, all answered on the recommended option)
- Final gate rounds: session 1 used 3/3 and stopped per the gate's rule; resumed after the owner's quarantine decision and used 3/3 again, ending PASS-WITH-OPEN-ITEMS with the final judge finding bucketed as OI-003. Full trajectory in the snapshot's Session history.
- Snapshot: [calibration-run-logger-snapshot.md](./calibration-run-logger-snapshot.md)

## 8. Open Items (Bucket C — replaces the issue tracker in lite)

| ID | Title | Stage | Type | Owner | Deadline | Best assumption | Impact | Status |
|---|---|---|---|---|---|---|---|---|
| OI-001 | Revisit rework weights (1/3/2) against actual human clearing effort | Stage 3 | data | @samgao2000 | 2026-09-30 | v1 weights stand until n=10; raw counts in records make re-weighting free | US-001 record content; report interpretation | open |
| OI-002 | Decide whether optional human-minutes field becomes mandatory | Stage 3 | decision | @samgao2000 | 2026-08-15 | stays optional; mandatory entry would reproduce the formality failure | US-001 schema; OI-001 evidence base | open |
| OI-003 | Precedence when a corrupted record and a duplicate run_id occur in the same emission (gate finding, round 3 resumed) | Stage 7 | decision | @samgao2000 | 2026-06-30 | integrity sweep (quarantine) runs first and unconditionally; validation then accepts or rejects the append | US-001 ext 2b; US-002 ext 3a | open |
