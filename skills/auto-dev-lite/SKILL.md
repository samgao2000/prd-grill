---
name: auto-dev-lite
description: >
  Autonomous software development pipeline, lite edition: no GitHub
  dependency, git optional. Drives local markdown issue files to git
  commits (when a repo exists) or to a runs/ledger.md audit log (when it
  doesn't), fully AFK end-to-end. Refuses to build from a PRD whose gate
  verdict is FAIL or missing. Trigger on "run auto-dev-lite on X",
  "implement the PRD AFK", "local pipeline go", or "start auto-dev-lite
  from the PRD". Chinese version: SKILL.zh.md (same folder)
metadata:
  origin: prd-grill
  author: Sam Gao
  homepage: https://github.com/samgao2000/prd-grill
---

# Auto-Dev Lite — Skill

## When to Activate

- A gated PRD (`final_gate_verdict: PASS` or `PASS-WITH-OPEN-ITEMS`) exists in
  `docs/prd/` and the user explicitly starts implementation.
- The user says "run auto-dev-lite on X", "implement the PRD AFK", "local
  pipeline go", "start auto-dev-lite from the PRD".
- `local-issues/*.md` already exist with status `ready`.
- Do **not** activate on a PRD with `final_gate_verdict: FAIL` or `not_reached`
  — step 0.5 hard-stops by design. Run prd-gate first.
- If the project already runs a build workflow such as ECC's `tdd-workflow`,
  this skill is optional: hand the gated PRD to that workflow instead and keep
  only step 10 (calibration record). See `integrations/ecc/README.md`.

## Triggers

- "run auto-dev-lite on X"
- "implement the PRD AFK"
- "local pipeline go"
- "start auto-dev-lite from the PRD" (implies step 0.5 auto-import)
- "turn the PRD into issues and run them"

## Position in the pipeline

```
user idea (human present)
  ↓ req-dev-lite grilling (human answers questions)
docs/prd/YYYY-MM-DD-{slug}.md  (three buckets + gate verdict)
  ↓ auto-dev-lite step 0.5 auto-import (no human)
local-issues/*.md  (Bucket A ready, Bucket C blocked)
  ↓ auto-dev-lite steps 1-9 loop (no human)
git commit sequence (or ledger entries) + retro
```

req-dev-lite **stops** after landing the PRD — it never auto-triggers this skill.
Whether and when to start implementation is the user's call. On start, if a PRD
exists and `local-issues/` is empty, step 0.5 picks it up automatically.

## Core constraints

1. **Acceptance-test immutability**: files marked `# AUTO_DEV_ACCEPTANCE: immutable`
   are NEVER modified, even when one edit would make a test pass. Wrong test →
   mark the issue `blocked` with a note; a human amends it.
2. **Kill switch**: between every major step, check `runs/<run_id>.kill`; abort if present.
3. **Tier-based risk control**: low/medium auto-commit; high → `needs-review`, no auto-commit.
4. **Cost ceiling**: $50 per run by default; hard-stop beyond it.
5. **Trailer**: every commit (or ledger entry in no-git mode) carries an
   `Auto-Dev-Lite-Trailer` block. Every issue MUST leave one traceable record —
   losing the trailer is losing the audit chain.

## Local issue file format

`<target_project>/local-issues/00N-slug.md` — full template (frontmatter fields,
state machine, Bucket-C variants) in [`references/issue-template.md`](references/issue-template.md).
States: `ready → in_progress → done | blocked | needs-review`.

## Run procedure (per issue, AFK)

### 0. Preflight

- **Git-mode detection** (git is optional, not a prerequisite):
  - `<target>/.git/` exists → `git_mode = tracked`: step 8 commits.
  - absent → `git_mode = ledger`: step 8 appends to `runs/ledger.md`. Do NOT
    `git init` on your own — version control is the user's decision. Print once:
    "No git repo: ledger mode. Per-issue rollback unavailable; consider (not required) git init."
- Lazy-create `<target>/runs/`.
- Read `<target>/PROJECT_CONTEXT.md` if present (stack, test command, migration
  command — overrides defaults).
- Probe `local-issues/` (files other than `.imported.md`) and `docs/prd/`:
  - issues exist → step 1
  - issues empty, PRD exists → step 0.5
  - both empty → **hard-stop**: "no issues and no PRD; run req-dev-lite first"

### 0.5. PRD import (auto-runs only when local-issues/ is empty)

Convert the latest req-dev-lite PRD into `local-issues/*.md`. Full rules:
[`references/prd-import-rules.md`](references/prd-import-rules.md) — including the
**bilingual (EN/中文) section-anchor table**. Summary:

| PRD section | Bucket | Lands in | status |
|---|---|---|---|
| `## 3. User Stories (Bucket A／桶 A)` `### US-NNN` blocks | A | `local-issues/00N-{slug}.md` (id = original `US-NNN`) | `ready` |
| `### Outcome Metrics (Bucket B／桶 B)` table | B | `PROJECT_CONTEXT.md § Reference Metrics` (lazy) | n/a |
| `## 8. Open Items (Bucket C／桶 C)` rows | C | `local-issues/00N-OI-NNN-{slug}.md` | `blocked` |
| `## 5. Testing Decisions` (SBE option a/b/c) | config | `PROJECT_CONTEXT.md § Testing` | n/a |

Hard rules: Bucket-A story bodies are copied **verbatim** (all 7 fields — never
rewritten or "tidied"); Bucket C keeps original `OI-NNN` ids and is always
`blocked`; Bucket B never becomes an issue; frontmatter `final_gate_verdict:
FAIL | not_reached` → **hard-stop** (an unscored or failed spec must not enter
implementation); parse failure / id conflict / all buckets empty → hard-stop, no
partial writes. Read `gate_mode` + `gate_confidence` for step 7 (below). Then
write the import log `local-issues/.imported.md` and proceed to step 1.

### 1. Pick the next issue

Scan `local-issues/*.md`: status `ready`, all `depends_on` done, lowest number first.
No candidate → final report.

### 2. Move to in_progress, init run

Set `status: in_progress`, generate `run_id` (YYYYMMDDHHMMSS-rand6), write it to
the issue, create `runs/<run_id>/log.jsonl`, emit `issue_fetched`.

### 3. Tier classify (re-evaluate)

Parse the story body, identify `planned_paths`, apply tier rules
(low = docs/config/single new file; medium = multi-file logic or schema
migration; high = ≥3 modules or auth/payment/data-loss boundaries or external
APIs). Update the issue's `tier:` field; emit `tier_classified`.

### 4. Claude as M3: write tests, then implementation

a. **Acceptance tests first** (translate Gherkin AC verbatim into pytest
   functions; one test per Scenario, named after it; include Extensions
   branches; file headed `# AUTO_DEV_ACCEPTANCE: immutable`; record the path in
   the issue's `acceptance_tests:` field).
b. **Then the implementation** (read surrounding code first; plan files; write
   via Edit/Write or bash heredoc; NEVER touch acceptance-test files).
c. Run schema migrations when needed.

### 5. Run pytest (subprocess — never in-process)

```python
# Must be a subprocess: in-process pytest + stdout capture + a
# ThreadPoolExecutor in the code under test deadlocks on Windows
# (observed in practice).
import subprocess
result = subprocess.run(["pytest", "--tb=short", "-q"], cwd=target_root,
                        capture_output=True, text=True, timeout=300)
```

Exit 0 or 5 → step 6. Anything else → issue `blocked`, emit `pytest_failed`,
append `## Block reason` with the stderr tail to the issue body, move on to the
next issue (blocked is a review queue, not a pipeline stall).

### 6. M4 self-review (single-LLM)

> **Design note — why single-LLM, for now.** M4's original design is a
> multi-LLM review: two or more independent models review the same diff, and
> the overlap between their finding sets feeds a **capture-recapture** estimate
> of the defects still uncaught — a statistical technique from wildlife
> population studies that Watts Humphrey applied to software inspections in his
> Personal Software Process (PSP) work. It is deferred deliberately: requiring
> a second model would raise the entry bar for users running a single LLM. v1
> therefore ships single-LLM self-review with an explicit `single_llm: true`
> flag in every review record, so multi-LLM records stay distinguishable when
> the feature lands. Planned as a future enhancement for review performance.

Read your own diff: correctness defects (off-by-one, null handling, missing
error paths)? security smells (plaintext secrets, SQL injection, unescaped HTML,
PII leaks)? spec violations against each Gherkin AC? any acceptance test
touched (absolute stop)? Blockers → handle as step-5 failure. Record the verdict
with the explicit caveat `single_llm: true`.

### 7. M5 escalation decision

Build the run state (helpers: `references/inlined-helpers.py` if the full
`auto_dev` package is absent): cost spent vs ceiling, test-failure count, new
dependencies, security findings, scope creep, arch conflicts, and
`requirement_confidence` sourced from the PRD frontmatter recorded at import:

- `gate_mode: prd-gate` → use `gate_confidence` verbatim.
- `gate_mode: self-reported` (or absent) → `min(verdict mapping, 0.85)`:
  PASS → 0.85, PASS-WITH-OPEN-ITEMS → 0.75. A self-graded verdict never earns
  full trust; below the 0.7 threshold it soft-escalates.

Decisions: `hard_stop` → `blocked`; `soft_escalate` → `needs-review`, next
issue; otherwise continue.

### 8. Leave the audit record (per git_mode)

**tracked** — single-branch commit to main, message body ending with the
`Auto-Dev-Lite-Trailer` block (run_id / issue_id / tier / review / cost_usd /
files_touched / lines / trailer_version: lite-1). No branches, no PRs.

**ledger** — append (never rewrite) an entry to `runs/ledger.md`:

```markdown
## L-NNN — US-XXX: <title>
- completed: <ISO timestamp>
- run_id / tier / review / cost_usd
- files_touched: path (+A/-B) per line
- trailer_version: lite-1-ledger
```

`L-NNN` is monotonically increasing. Known ledger-mode limits (state them in the
final report): no per-issue diff or rollback; audit granularity is file-level.

### 9. Mark done

`status: done`; emit `issue_done` with `commit_sha` (tracked) or `ledger_id`
(ledger); loop to step 1.

### 10. Emit the calibration record (mandatory final step)

When the run ends (run-all completed, or during abort cleanup), record emission is
mandatory: `python -m prd_gate calib add --run runs/<run_id> --prd <prd-path>`.
Exactly one record per run, pairing the PRD's gate scores with the run's rework
outcomes — this feeds the score-vs-rework calibration. If `prd_gate` is not
installed, skip and state "calibration record not emitted (prd_gate absent)" in
the final report. Full rules: the calibration-run-logger PRD in
`examples/calibration-run-logger/prd.md`.

## Run-all mode

Loop steps 1-9 until no `ready` issue remains. Per-issue one-liner:
`✅ US-003 done in 4 min, +120/-8 lines, commit abc1234` (ledger mode:
`..., ledger L-007`). Final report: total time, estimated cost, blocked list,
git/ledger mode, and whether the PRD verdict was independently gated.

## Anti-pattern self-checks

- ❌ Quietly amending an acceptance test to make it pass → hard-stop.
- ❌ In-process pytest (capture + thread pools deadlock on Windows) → always subprocess.
- ❌ Editor-style tools may silently truncate long files → bash heredoc for
  files >200 lines, then verify (`ast.parse` for Python).
- ❌ Cross-issue code (one issue touching five stories' code) → violates INVEST Independence.
- ❌ Skipping the trailer → audit chain lost.
- ❌ Step 0.5 marking Bucket B/C items `ready` → they have no Gherkin AC and will
  fail; B never becomes an issue, C stays `blocked`.
- ❌ Step 0.5 "tidying" PRD bodies → provenance broken; Bucket A is verbatim.

## Module sources (two-level fallback)

1. If the full `auto_dev` package is installed (`pip install -e`, same-repo
   scenario), import `tier_classifier` / `escalation` / `trailer` / `cost_meter`
   / `run_log` / `kill_switch` from it.
2. Otherwise use [`references/inlined-helpers.py`](references/inlined-helpers.py)
   — a stdlib-only simplified equivalent (tier heuristics, escalation decision
   including the 0.7 requirement-confidence threshold, trailer builder, run ids,
   ledger append, kill-switch check). Semantics match; the inlined rules are
   coarser (keyword heuristics). Where they disagree, the full package is authoritative.

## Files

- `SKILL.md` — this file
- `references/prd-import-rules.md` — full step 0.5 import rules (source
  selection, bucket mapping, bilingual anchors, edge cases, failure modes, log format)
- `references/issue-template.md` — local issue file template
- `references/inlined-helpers.py` — stdlib fallback implementation
- `sessions/` — post-run retros (same pattern as req-dev-lite)

Contract alignment: **req-dev-lite templates/prd-local(.en).md @ 2026-06-10**
(see "与 req-dev-lite 的契约" at the end of prd-import-rules.md).
