# PRD Import Rules (step 0.5)

Detailed rules referenced by `SKILL.md` step 0.5. Chinese version: [prd-import-rules.zh.md](prd-import-rules.zh.md).

> **Contract version**: aligned to `req-dev-lite/templates/prd-local(.en).md` @ **2026-06-10**
> (8-section structure + 9-column Open Items table; additive frontmatter
> `gate_mode` / `gate_aggregate` / `gate_confidence` / `gate_report` — older PRDs
> missing them are treated as `gate_mode: self-reported`). Template changes MUST update this file in lockstep.

## Trigger (precondition)

Step 0 enters step 0.5 only when BOTH hold; otherwise skip to step 1:

1. `<target>/local-issues/` is empty (no `.md` files; `.imported.md` doesn't count)
2. `<target>/docs/prd/` exists with ≥1 `*.md`

Both empty → hard-stop at step 0 ("run req-dev-lite first").

## PRD source selection

1. Parse the `YYYY-MM-DD` filename prefix; take the **newest**.
2. Same-day multiples (`-2`/`-3` suffixes) → last alphabetically + record in the import log.
3. Read frontmatter:
   - `status: complete` (or absent) → import normally
   - `status: partial` → warn + continue ("starting from an incomplete PRD" in log and summary)
   - `final_gate_verdict: FAIL | not_reached` → **hard-stop** (specs that failed or skipped the gate must not enter implementation)
   - `gate_mode` (default `self-reported`) + `gate_confidence`:
     - `gate_mode: prd-gate` with `gate_confidence` → escalation `requirement_confidence` uses that value verbatim
     - `gate_mode: self-reported` (or absent) → `requirement_confidence = min(verdict mapping, 0.85)`; mapping PASS → 0.85, PASS-WITH-OPEN-ITEMS → 0.75 (a self-graded verdict never earns full trust)
     - record gate_mode in the import log; the final report tells the user whether this run's verdict was independently gated
   - record `session_id` and `snapshot` (audit trail)
4. Parse failure (neither `## 3. User Stories` nor `## 8. Open Items` present) → **hard-stop**, write nothing.

## Bilingual anchors (EN/中文, since 2026-06-10)

req-dev-lite ships two equivalent templates: `templates/prd-local.md` (中文) and
`templates/prd-local.en.md` (English). **Section numbering, US-NNN heading shape,
story field order, and Open Items column order are identical** — only the natural
language differs. The two columns below are interchangeable during parsing; mixed
documents must also be accepted:

| 中文锚点 | English anchor |
|---|---|
| `## 3. User Stories（桶 A）` | `## 3. User Stories (Bucket A)` |
| `### Outcome Metrics（桶 B）` | `### Outcome Metrics (Bucket B)` |
| `## 8. Open Items（桶 C ...）` | `## 8. Open Items (Bucket C ...)` |
| `**作为** ... **我希望** ... **以便** ...` | `**As** ... **I want** ... **so that** ...` |
| `**追溯**：Why=..., Who=..., How=...` | `**Traceability**: Why=..., Who=..., How=...` |
| `**Extensions（不开心路径）**` | `**Extensions (unhappy paths)**` |
| `**三桶归属**` | `**Bucket assignment**` |
| Open Items columns `Owner` / `答复截止` | `Owner` / `Deadline` |

Remaining anchors (`### US-NNN[:：]`, `**INVEST**`, `**Gherkin AC**`, `**Volere QG**`,
frontmatter keys) are language-neutral.

## Section anchors (strict match)

The core req-dev-lite ↔ auto-dev-lite contract. Match exactly:

| Anchor regex | Source | Use |
|---|---|---|
| `^## 3\. User Stories.*$` | Bucket A | → `local-issues/*.md`, status ready |
| `^### US-(\d{3})[:：]\s*(.+)$` | one story's heading | extract ID + title (full- or half-width colon) |
| `^### Outcome Metrics.*$` (inside `## 1.`) | Bucket B table | → PROJECT_CONTEXT.md |
| `^## 8\. Open Items.*$` | Bucket C table | → `local-issues/*-OI-*.md`, blocked |
| `^## 5\. Testing Decisions.*$` | SBE option (a/b/c) | → PROJECT_CONTEXT.md (overrides default pytest) |
| `^## 2\. Solution.*$` | candidates + rejected | appended to each story body as context |
| `^## 4\. Implementation Decisions.*$` | decision log + ADRs | appended to each story body as context |
| `^## 6\. Out of Scope.*$` | discarded requirements | **not imported**; log "N out-of-scope items" only |

The `\.` is required — template headings carry numeric prefixes.

## Bucket → local-issues mapping

| PRD section | Bucket | Lands in | status |
|---|---|---|---|
| `### US-NNN` blocks under `## 3.` | A | `local-issues/00N-{slug}.md` (id = `US-NNN`) | `ready` |
| Outcome Metrics table under `## 1.` | B | `PROJECT_CONTEXT.md § Reference Metrics (from PRD)` (lazy-created) | n/a |
| each row of the 9-column table under `## 8.` | C | `local-issues/00N-OI-{NNN}-{slug}.md` (id = `OI-NNN`, **original ID kept**) | `blocked` |
| `## 5. Testing Decisions` option | config | `PROJECT_CONTEXT.md § Testing` | n/a |

**File numbers `00N` follow import order; issue IDs follow the PRD. The two are decoupled.**
E.g., 8 US + 3 OI → `001-…` to `008-…` (US-001…US-008), then `009-OI-001-…`, `010-OI-002-…`, `011-OI-003-…` (blocked).

## Bucket A → user-story issue format

Each PRD story body carries 7 fields in fixed order (EN or 中文 names per the
bilingual table): As/I want/so that · Traceability · INVEST · Gherkin AC ·
Extensions · Volere QG · Bucket assignment.

Generated issue file:

```markdown
---
id: US-001                                    # PRD's original ID
title: <from the ### heading, "US-NNN:" prefix stripped>
status: ready
tier: medium                                  # default; step 3 re-evaluates from planned_paths
depends_on: []                                # see extraction rules below
acceptance_tests: null
run_id: null
originated_from: prd_user_story
prd_source: docs/prd/YYYY-MM-DD-{slug}.md
prd_session_id: <PRD frontmatter session_id>
imported_at: YYYY-MM-DD HH:MM
---

# US-001: <title>

<the full story body copied VERBATIM from the PRD — all 7 fields, zero edits>

---

## Context (from PRD § 2 Solution)

<copy of `## 2. Solution`, so step 4 knows the candidate and rejected approaches>

## Decisions (from PRD § 4 Implementation Decisions)

<only the Decision Log rows whose ADR column references this US; omit the section if none>
```

**Hard rules**: the 7-field body is copied **verbatim** — never rewritten, simplified,
or "completed". `## Context` = whole §2 (omit if missing). `## Decisions` = only
rows referencing this US.

**`depends_on` extraction** (priority order): explicit `**前置**：US-NNN, …` → extract;
explicit `Depends on US-NNN` → extract; otherwise `[]`. (The PRD template does not
currently force dependency declarations; update this rule if that changes.)

## Bucket C → open-item issue format

The PRD Open Items table has 9 columns:
`ID | Title | Stage | Type | Owner | Deadline | Best assumption | Impact | Status`
(中文: `ID | 标题 | 拦截阶段 | 类型 | Owner | 答复截止 | 目前最佳假设 | 影响范围 | 状态`).

Each row becomes:

```markdown
---
id: OI-001                                    # PRD's original ID
title: <Title column>
status: blocked                               # always; never enters the step-1 queue
tier: medium
depends_on: []
acceptance_tests: null
run_id: null
originated_from: prd_open_item
prd_source: docs/prd/YYYY-MM-DD-{slug}.md
prd_open_item_status: open                    # from the Status column: open / [resumable] / resolved / still-open
intercepted_at_stage: <Stage column>
item_type: <Type column>
owner: <Owner column>
deadline: <Deadline column>
affected_scope: <Impact column>
imported_at: YYYY-MM-DD HH:MM
---

# OI-001: <title>

## Origin

Imported from the PRD `## 8. Open Items` table on YYYY-MM-DD HH:MM.
**Needs human resolution before auto-dev-lite can process.**

Original row values (verbatim, for cross-checking):

- **Stage**: <value> · **Type**: <value> · **Owner**: <value> · **Deadline**: <value>
- **Best assumption**: <value> · **Impact**: <value> · **Status in PRD**: <value>

## How to unblock

1. **Preferred**: resolve the uncertainty with the owner → promote to a user story:
   add a full `### US-NNN` (INVEST + Gherkin AC) to the PRD §3, delete this row, re-import (see Re-import).
2. **Alternative**: edit this file in place — `status: blocked` → `ready`, `id:` →
   an appropriate `US-NNN`, add Gherkin AC per the story template, delete `## Origin`.
3. **Reject**: if the item is unresolvable or obsolete → set the PRD row's Status to
   `resolved` (or delete the row) → delete this issue file.
```

**Status column handling**: `open` → import as blocked. `[resumable]` → import as
blocked **plus a prominent warning**: "⚠️ stopped mid-grilling; prefer resuming
req-dev-lite over promoting this directly." `resolved` / `still-open` → **not imported**.

## Bucket B → PROJECT_CONTEXT.md

Metrics table → `## Reference Metrics (from PRD)` (lazy-create the file with a header
comment if absent; if present, append rows — never delete existing ones — under a
source comment `<!-- Appended from docs/prd/… on … -->`).
**Never touch any other user-authored section** (`## Testing`, `## Deployment`, …) except as below.

## Testing Decisions → PROJECT_CONTEXT.md § Testing

PRD §5 has three mutually exclusive options: (a) run Gherkin directly
(Cucumber/Behave), (b) hand-translate Gherkin into test code, (c) Gherkin as spec
only. Detect the selected one (look for selection verbs near `(a)/(b)/(c)`; default
(b) if unclear). Write:

```markdown
## Testing

<!-- Imported from PRD § 5 Testing Decisions on YYYY-MM-DD HH:MM -->

- **SBE option**: (b) hand-translate Gherkin into pytest tests
- **Test command**: `pytest --tb=short -q` (default; user may override)
- **Test directory**: `tests/`
```

Option (a) → command `behave` (or the language's Cucumber runner); option (c) → keep
pytest, note "Gherkin is spec reference only" in issue bodies. SKILL.md step 5 reads
the test command from here.

## `## 6. Out of Scope`

Never imported. One import-log line: `- Out of scope: N discarded requirements (see PRD § 6)`.
Discards exist for human readers — to prevent re-proposal — not for the queue.

## Idempotency & edge cases

| Case | Behavior |
|---|---|
| `local-issues/` has a file with the same `US-NNN`/`OI-NNN` id | **hard-stop**: list conflicts; user archives or deletes first |
| ≥2 PRDs in `docs/prd/` | newest wins; log "ignored N older PRDs: <list>" |
| No `## 3. User Stories` (open items only) | skip Bucket A; import C; tell the user |
| No `## 8. Open Items` | skip Bucket C; no error |
| No Outcome Metrics | skip Bucket B; no error |
| No `## 5. Testing Decisions` | no Testing section; step 5 defaults to pytest |
| `final_gate_verdict: FAIL` or `not_reached` | **hard-stop** |
| All three buckets empty | **hard-stop**: "nothing importable — re-run req-dev-lite" |

## Import log

Append to `<target>/local-issues/.imported.md` after every successful import: source
PRD, frontmatter status / verdict / gate_mode / session_id / snapshot, per-bucket file
lists, testing option, out-of-scope count, skipped older PRDs, warnings (partial /
resumable). See the Chinese sibling for the fully worked layout.

## Step 0.5 user summary (mandatory before step 1)

```
✅ PRD imported: docs/prd/2026-05-19-crm-pilot.md
   Bucket A (ready):    8 user stories  → 001-* … 008-*
   Bucket B (metrics):  2 metrics       → PROJECT_CONTEXT.md § Reference Metrics
   Testing:             (b) pytest      → PROJECT_CONTEXT.md § Testing
   Bucket C (blocked):  3 open items    → 009-OI-001-* … 011-OI-003-*
   Out of scope:        5 discarded (recorded in the PRD only)
   Gate:                PASS-WITH-OPEN-ITEMS via prd-gate (confidence 0.85)

   ⚠️  PRD status = partial — some requirements were not fully grilled.
       Consider resuming req-dev-lite afterwards.

Proceeding to step 1 (select next ready issue)...
```

## Step-0.5 anti-patterns

- ❌ `status: ready` on Bucket B/C items — they have no Gherkin AC and will fail
- ❌ rewriting PRD bodies during import — Bucket A is verbatim
- ❌ writing partial local-issues after a parse failure — all-or-nothing
- ❌ overwriting an existing same-ID issue — conflict = hard-stop
- ❌ touching PROJECT_CONTEXT.md sections other than Reference Metrics / Testing
- ❌ running tests or writing code during step 0.5 — it is format conversion only
- ❌ swallowing a `final_gate_verdict: FAIL` PRD

## Re-import (PRD updated)

The trigger is "`local-issues/` empty", so updates never auto-re-import. Manual path:
move done issues to `local-issues/done/`, prune obsolete blocked OIs, restart
auto-dev-lite → step 0 sees an empty dir → imports the new PRD.
*Future extension (not in v1)*: an explicit "re-import PRD" trigger diffing by
`prd_source` + `id`, appending only new stories.

## Contract with req-dev-lite

This file's parsing rules depend on `req-dev-lite/templates/prd-local(.en).md`. The
interface = frontmatter fields (`status`, `final_gate_verdict`, `gate_mode`,
`gate_confidence`, `session_id`, `snapshot`), the 8 numbered section anchors (with the
bilingual equivalents above), the 7-field story body order, and the 9-column Open
Items order.

**Sync protocol for template changes**: edit the template → add a change note to
req-dev-lite SKILL.md's "Downstream consumer contract" → update this file's anchor and
mapping sections → bump the contract-version line at the top → regression-test the
import against a historical PRD (e.g. `examples/personal-crm/prd.md`).

Current alignment: **req-dev-lite 2026-06-10**.
