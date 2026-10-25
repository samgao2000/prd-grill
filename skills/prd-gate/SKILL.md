---
name: prd-gate
description: >
  Independent PRD quality gate — the measurable checkpoint between "spec
  produced" (req-dev-lite) and "build started" (auto-dev-lite, or any
  planning/TDD workflow). Scores a PRD on 11 dimensions (Volere 4 + 7 review
  labels): deterministic checks plus a fresh-context LLM judge, emitting
  .gate.json (machine-readable), .gate.md (human-readable), a PASS /
  PASS-WITH-OPEN-ITEMS / FAIL verdict, and a requirement_confidence value
  consumed by build-stage escalation (threshold 0.7). Trigger on "run
  prd-gate", "score this PRD", "gate this PRD", "/prd-gate".
metadata:
  origin: prd-grill
  author: Sam Gao
  homepage: https://github.com/samgao2000/prd-grill
---

# prd-gate — Independent PRD Quality Gate

> Chinese version: [SKILL.zh.md](SKILL.zh.md)

## When to Activate

- A PRD exists in `docs/prd/` and someone is about to plan or build from it.
  Gate first; the verdict decides whether building is allowed.
- The user says "run prd-gate", "score this PRD", "gate this PRD", "/prd-gate".
- req-dev-lite stage 7 reached landing (mandatory when `prd_gate` is installed).
- A PRD's frontmatter says `gate_mode: self-reported` or lacks
  `final_gate_verdict` — it has only been self-graded by its author model.
- Do **not** run the judge in the session that wrote the PRD. The judge is a
  fresh-context subagent (in ECC: the `prd-judge` agent); reuse of the authoring
  context silently destroys the gate.

## Why it exists

Code generation is commoditizing; the binding constraint on agentic software
delivery is **spec quality**. Yet in most pipelines the only quality check on a
PRD is the author model grading its own homework in the same conversation — a
review systematically biased toward PASS.

prd-gate splits the same rubric (single anchor:
`skills/req-dev-lite/references/quality-gateway.md`) into two independently
executed layers:

1. **Deterministic layer** (Python, zero LLM): Gherkin presence + real-value
   detection, traceability anchors (`Why=` / `Who=`), a weasel-word lexicon,
   Cockburn-Extensions presence, Open-Items owner+deadline rules, and the core
   Why/Who one-vote veto. Reproducible; regression-tested.
2. **Independent judge layer** (fresh-context LLM): Contradiction / Gap /
   Fallacy / Redundancy / Dangling / Overreach / Solution-language — the
   dimensions that need domain judgment. The judge sees ONLY the PRD file and
   the anchor doc — never the conversation that produced the PRD.

Merge rule: **strict-verdict-first** — for dimensions scored by both layers,
take `min()`; exception: `solution_free`, where the deterministic lexicon is
only a signal and the judge is authoritative (the evidence is still carried for audit).

## Usage

### Inside an agent session (recommended)

Nested SDK calls from a Bash subprocess are typically blocked inside coding
agents, so the judge runs as a fresh subagent:

1. `python -m prd_gate score --prd docs/prd/<file>.md`
   → deterministic report + `<file>.judge-tasks.json` (exit 2 = already FAIL — rework first)
2. Spawn a **fresh-context subagent** whose only inputs are: the PRD file, the
   anchor doc, and judge-tasks.json. It writes `<file>.judge-results.json`
   following the embedded result schema. Never give it the elicitation conversation.
3. `python -m prd_gate merge --prd <file> --judge-results <file>.judge-results.json`
   → final `.gate.json` / `.gate.md` including the frontmatter patch.
4. Paste the frontmatter patch into the PRD (copy values exactly; never hand-edit).

### Other agents (Cursor, Windsurf, Codex CLI, Gemini CLI, ...)

The judge-tasks/merge flow is vendor-neutral: any capable LLM can be the judge.
The one thing you must provide yourself is context isolation — open a brand-new
chat/session whose ONLY inputs are the three files (the PRD, the anchor rubric,
judge-tasks.json), save its answer as `<prd>.judge-results.json` (raw JSON; code
fences and surrounding prose are tolerated), then run `merge`. Re-using the
session that wrote the PRD silently destroys the gate's independence.

### Terminal with an API key

```bash
pip install -e ".[api]"
ANTHROPIC_API_KEY=... python -m prd_gate score --prd docs/prd/x.md --judge api
```

CI / tests: `PRD_GATE_MOCK=1` (judge layer returns an all-pass stub; pipeline only).

## Output contract

- `<prd>.gate.json` — schema `prd-gate/v1`: per-dimension score (0..1) with
  cited failures, verdict, weighted aggregate (weights in
  `src/prd_gate/scoring.py`), `requirement_confidence`
- `<prd>.gate.md` — human-readable report + frontmatter patch block
- exit code 0 = PASS / PASS-WITH-OPEN-ITEMS; 2 = FAIL

Verdict semantics replicate req-dev-lite stage 5: allowed story failures =
`floor(N × 0.2)`; the core Why/Who veto forces FAIL and caps confidence at 0.5
(below the 0.7 escalation threshold, so a downstream build soft-escalates).

## Downstream consumers

| Consumer | Reads | Behavior |
|---|---|---|
| auto-dev-lite step 0.5 | frontmatter `final_gate_verdict` | FAIL / not_reached → hard-stop |
| auto-dev-lite step 7 | `gate_mode` + `gate_confidence` | prd-gate → use verbatim; self-reported → capped at 0.85 |

## Calibration (`prd-gate calib`)

`calib add --run <run-dir> --prd <prd>` appends one validated record pairing the
PRD's gate scores with the run's rework outcomes (auto-dev-lite step 10 makes
this mandatory). `calib report` prints the paired table, Pearson/Spearman
correlation (n ≥ 3), and explicit exclusions (aborted runs, self-reported
verdicts, quarantined records, unrecorded runs). Spec: `examples/calibration-run-logger/prd.md` — which is itself record #1.

## Known limits (v1)

- **Independence is enforced by discipline, not technology.** Nothing prevents a
  user from feeding the judge the authoring conversation, and no tool can detect
  it. The gate makes honest judging easy and auditable; it cannot make dishonest
  judging impossible.
- `--judge api` supports the Anthropic API only (the judge-tasks/merge flow works
  with any vendor).
- The deterministic lexicons (weasel words, solution-language signals) cover
  English and Chinese; PRDs in other languages lean on the judge layer for those
  dimensions.
- `calib add` derives outcome counts from the auto-dev-lite run-log event
  vocabulary (issue_fetched / pytest_failed / issue_blocked / issue_needs_review /
  run_finished); other build systems need an adapter emitting those events.
- Judge-dimension scores are still LLM judgments — their credibility comes from
  fresh context + a single anchor + mandatory evidence citation, not magic.
  Review the Evidence section; don't consume the number blind.
- The parser contract is the real template files (`prd-local(.en).md`,
  `user-story.md`) — both English and Chinese anchors are accepted. A
  free-form PRD may parse to 0 stories → automatic FAIL. That is a feature:
  specs that don't meet the contract shouldn't enter the pipeline.
- No calibration data yet correlating gate scores with downstream
  escalations/rework. Planned after ≥10 gated runs — see README roadmap.

## Files

- `src/prd_gate/` — parser / checks / judge / scoring / report / cli
- `tests/` — regression tests incl. good/bad PRD fixtures and a bilingual parser test
- `skills/req-dev-lite/references/quality-gateway.md` — the single scoring
  anchor (predates this tool; the tool is its executor)
