# PRD Gate Report — 2026-05-19-personal-crm.md

- **Verdict**: PASS-WITH-OPEN-ITEMS *(judge dimensions pending — deterministic floor only)*
- **Aggregate score**: 0.97
- **requirement_confidence**: 0.85 (escalation threshold 0.7)
- **Stories**: 8 total, 1 failed (allowed: 1) — US-002
- **Mode**: deterministic-only

## Dimensions

| Dimension | Score | Judged by | Failures |
|---|---|---|---|
| gap | 1.00 | deterministic | 0 |
| no_weasel | 1.00 | deterministic | 0 |
| solution_free | 0.88 | deterministic | 1 |
| testable | 1.00 | deterministic | 0 |
| traceable | 1.00 | deterministic | 0 |
| unowned | 0.91 | deterministic | 2 |

## Evidence

- `[solution_free]` **US-002** — solution terms in story prose: sqlite
- `[unowned]` **OI row 19** — no concrete deadline: '2027 V2'
- `[unowned]` **OI row 20** — no concrete deadline: '2027 V2'

## Frontmatter patch (paste into PRD)

```yaml
final_gate_verdict: PASS-WITH-OPEN-ITEMS
gate_aggregate: 0.968
gate_confidence: 0.85
gate_report: 2026-05-19-personal-crm.gate.json
```
