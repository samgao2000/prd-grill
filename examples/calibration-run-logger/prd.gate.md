# PRD Gate Report — 2026-06-10-calibration-run-logger.md

- **Verdict**: PASS-WITH-OPEN-ITEMS
- **Aggregate score**: 0.96
- **requirement_confidence**: 0.85 (escalation threshold 0.7)
- **Stories**: 3 total, 0 failed (allowed: 0)
- **Mode**: deterministic+fresh-context-judge

## Dimensions

| Dimension | Score | Judged by | Failures |
|---|---|---|---|
| contradiction | 0.67 | llm | 1 |
| dangling | 1.00 | llm | 0 |
| fallacy | 1.00 | llm | 0 |
| gap | 1.00 | merged | 0 |
| no_weasel | 1.00 | deterministic | 0 |
| overreach | 1.00 | llm | 0 |
| redundancy | 1.00 | llm | 0 |
| solution_free | 1.00 | merged | 0 |
| testable | 1.00 | deterministic | 0 |
| traceable | 1.00 | deterministic | 0 |
| unowned | 1.00 | deterministic | 0 |

## Evidence

- `[contradiction]` **US-002** — US-002 ext 3a and US-001 ext 2b are both matchable by the same constructible input with no precedence rule, and prescribe incompatible outcomes. US-002 ext 3a: 'Dataset contains a corrupted record (crash during a previous append, US-001 ext 3c) -> emission moves the corrupted record to the quarantine area, appends the new record ... appends never stay blocked'. US-001 ext 2b: 'Same run_id already present in the dataset -> emission rejected, nothing appended ("duplicate run_id")'. Input: the dataset holds a corrupted record from a crashed append AND a valid record whose run_id matches the incoming record (e.g. an operator re-runs the emission step for an already-recorded run after some other run's crash). Ext 3a says the new record is appended; ext 2b says nothing is appended — both cannot hold. The same overlap leaves a second behavior undefined: when the incoming record is rejected (by US-001 ext 2b or US-002 ext 1a/1b/2a), does the quarantine move of the pre-existing corrupted record still occur? Neither story says. Fix per anchor [Contradiction]: write the boundary condition (e.g. validation/duplicate checks take precedence and quarantine occurs only on a successful append, or quarantine occurs unconditionally before the candidate is judged).

## Frontmatter patch (paste into PRD)

```yaml
final_gate_verdict: PASS-WITH-OPEN-ITEMS
gate_aggregate: 0.9587
gate_confidence: 0.85
gate_report: 2026-06-10-calibration-run-logger.gate.json
```
