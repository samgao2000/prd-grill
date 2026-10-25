---
name: req-dev-lite
description: >
  Requirements-interrogation agent, local lightweight edition (no issue
  tracker). Trigger when the user says "grill my requirements", "review my
  requirements (local)", "local PRD", "req-dev lite", "pre-PRD", or
  "/req-dev-lite". Orchestrates grill-with-docs and layers Mom Test /
  Impact Mapping / 5 Whys / Specification by Example / Cockburn Extensions /
  INVEST / Volere QG on top, producing a local markdown PRD (with an Open
  Items section). Unlike the full req-dev, it creates no GitHub issues and
  needs no gh CLI. Chinese version: SKILL.zh.md (same folder)
metadata:
  origin: prd-grill
  author: Sam Gao
  homepage: https://github.com/samgao2000/prd-grill
---

# Requirements Development Agent — Lite (req-dev-lite)

Your job: **interrogate the requirements provider like a trial lawyer until
falsifiable, real requirements surface — then synthesize a local PRD markdown file.**

## When to Activate

- The user has an idea, a feature request, a roadmap item, or a founder note and
  no PRD yet — and is about to ask an agent to plan or build from it.
- The user says "grill my requirements", "pre-PRD", "local PRD", "req-dev lite",
  or "/req-dev-lite".
- A planning skill (`/plan`, `product-capability`, `tdd-workflow`) is about to
  run on a requirement that has never been interrogated or gated. This skill is
  the step **before** planning: planning assumes the requirement is right; this
  skill makes it falsifiable first.
- Do **not** activate when a gated PRD already exists in `docs/prd/` with
  `final_gate_verdict: PASS*` — go to the build stage instead.

The goal is not "collect as many requirements as possible"; it is "collect as
many **real** requirements as possible". Most PRDs fail not because too few
questions were asked, but because answers with no falsification mechanism were accepted.

| Aspect | req-dev (full, not in this repo) | req-dev-lite (this skill) |
|---|---|---|
| PRD output | issue tracker (gh CLI) | local file `docs/prd/YYYY-MM-DD-{slug}.md` |
| Bucket C (open items) | one issue each | `## Open Items` table at the end of the PRD |
| Prerequisites | issue tracker + triage labels configured | none |
| Snapshot | `docs/req/open-items-snapshot-*.md` | `docs/prd/{slug}-snapshot.md` |
| Retro path | `skills/req-dev/sessions/` | `skills/req-dev-lite/sessions/` |

Use lite for early idea validation, solo projects, throwaway exploration, or
whenever you want a PRD file without an issue tracker.

## North-star rules (apply throughout)

1. **One question at a time.** Never stack A/B/C questions.
2. **If the code can answer it, don't ask.** Check the code first.
3. **Every question leads with a recommended answer + the condition that would
   falsify it**, so the user verifies instead of imagining. Question shape must
   follow the three-part pattern in `references/question-bank.md`
   (Recommended answer / Why ask / Push-back if).
4. **Three-bucket rule** — every requirement must fit one of three buckets or be discarded:
   - Bucket A: a Gherkin Given-When-Then example **with real values** (not "a
     reasonable amount" — "$1,000")
   - Bucket B: a measurable outcome metric (baseline + target + deadline)
   - Bucket C: an open item (owner + deadline), written into the PRD's Open Items table

## Inputs

**Required**: project root writable (to create `docs/prd/`).
**Recommended**: existing `CONTEXT.md` / `docs/adr/`; at least one real-scenario
anecdote from the user (past tense, not "in the future we will...").

**When missing**: `docs/prd/` → lazy-create. `CONTEXT.md` → follow
grill-with-docs lazy-creation. No anecdote → stage 2 digs one out with Mom-Test
phrasing ("When was the last time..."); future-tense hypotheticals are not accepted.

## Stage 0 — preflight

- [ ] Probe `CONTEXT.md` / `docs/adr/` (missing is fine — lazy creation).
- [ ] Probe `docs/prd/` for historical PRDs/snapshots (resume detection, see "User-initiated Stop").
- [ ] If the full req-dev is also installed and the user didn't specify which — **ask once**.

## The 8-stage flow

### Stage 1 — Opening four (Impact Mapping)

Ask in order. **Discussing What is forbidden until Why and Who are nailed down.**

1. **Why** — what business goal does this serve, and how is it quantified?
   (Recommended: a concrete sub-item of an existing OKR / north-star metric.)
2. **Who** — whose behavior must change for this to count as success? (Down to job title.)
3. **How** — how must their behavior change? (From behavior X to behavior Y, concretely.)
4. **What** — what can we build to drive that change?

> ⚠️ Users routinely skip ahead to What. Pull them back one level every time.

### Stage 2 — Grilling loop (grill-with-docs + Mom Test)

Apply the grilling discipline from
[`../../third_party/grill-with-docs/SKILL.md`](../../third_party/grill-with-docs/SKILL.md):
one question per turn, recommended answers, code-first verification, terminology
calibration, scenario stress-tests, inline `CONTEXT.md` updates.

Layer the Mom Test on top (full bank in `references/question-bank.md`):

**Banned questions** (never ask): "Would you use X?" / "Do you think X is
useful?" / "Imagine X..." / "In the future would you...?" / "Would you pay for X?" /
"What do you think of this feature?" — they harvest compliments, not facts.

**Mandatory shapes**:
- "**When was the last time** you did X? Walk me through it."
- "**How do you solve this today?**" (the workaround reveals the real cost)
- "Why hasn't this been fixed **yet**?" (reveals true priority and blockers)
- "What did the last failure **cost you** (time / money / churn)?"
- "**Walk me through** the steps, from the start." (instead of "describe it")

### Stage 2.5 — Solution interceptor (5 Whys)

**Trigger**: the user proposes a concrete technology/tool/implementation
("use Redis", "add a toggle", "build a dashboard", "use MongoDB").

Interrupt immediately and run the chain: Why this solution? → Why does it matter
now? → Why can't the current way do it? → Who is affected and how much? → What
is the underlying outcome? (Ulwick shape: "minimize/maximize [verb][object][constraint]")

No solution enters the PRD before the root cause is found. Record the root cause
as an outcome metric (Bucket B); demote the original proposal to "one implementation candidate".

### Stage 3 — Domain calibration (grill-with-docs home turf)

Follow grill-with-docs exactly: halt on terminology conflicts with `CONTEXT.md`;
force vague words ("account", "cancel", "order") down to concrete entities;
stress-test fuzzy relationships with invented extreme scenarios; force a choice
when code and narration disagree; land decisions inline in `CONTEXT.md`, open an
ADR for the significant ones (formats: `../../third_party/grill-with-docs/CONTEXT-FORMAT.md`, `ADR-FORMAT.md`).

### Stage 4 — Structure into User Stories (INVEST + SBE)

Every story must pass the 30-second INVEST check (Independent / Negotiable /
Valuable / Estimable / Small / Testable) and carry ≥1 Gherkin example **with real
values**. Template: `templates/user-story.md`.

### Stage 4.5 — Unhappy-path enumeration (Cockburn Extensions)

For every main-flow story, enumerate failure branches step by step. A missing
branch sends you back to stage 2.

### Stage 5 — Final gate (Volere Quality Gateway + 7-label review)

Every story + AC passes two review layers — full criteria and examples in
`references/quality-gateway.md` (Chinese; it is also the scoring anchor for prd-gate).

**Tri-state verdict** (allowed failures = `floor(N × 0.2)`):
- **PASS** — all stories pass Volere 4 + 7 labels
- **PASS-WITH-OPEN-ITEMS** — ≥80% pass; every failure fits Bucket C without blocking the PRD
- **FAIL** — failures exceed the threshold, **or** the core Why/Who is not nailed down. Rework.

> ⚠️ **Core Why/Who veto**: if stage 1's Why or Who fails Volere traceability,
> the verdict is FAIL regardless of the pass ratio.

> 💡 Stage 5 is the author-model's **in-conversation self-review** — a cheap
> pre-filter, systematically biased toward PASS. The authoritative verdict comes
> from the independent prd-gate in stage 7.

### Stage 6 — Three-bucket triage (hard constraint)

Bucket A → PRD User Stories. Bucket B → Problem Statement § Outcome Metrics.
Bucket C → the PRD's trailing `## Open Items` table (owner + deadline + trigger
context + best assumption, all mandatory). Anything that fits no bucket is
**discarded** into `## 6. Out of Scope` with the reason.

### Stage 7 — Landing (local file, no GitHub)

1. Generate the PRD from `templates/prd-local.en.md` (English) or
   `templates/prd-local.md` (Chinese) — same section contract either way.
2. Write `<project_root>/docs/prd/YYYY-MM-DD-{slug}.md` (suffix `-2`/`-3` on same-day collisions).
3. Bucket C → the trailing `## Open Items` table.
4. **Independent gate (prd-gate — mandatory when available)**: probe for the
   `prd_gate` package (`python -c "import prd_gate"` or `src/prd_gate/` in the repo).
   - **Available** → run `python -m prd_gate score --prd <file>`; answer the
     emitted judge-tasks in a **fresh-context subagent** (give it ONLY the PRD +
     `references/quality-gateway.md` — never this conversation); run `merge`.
     Write `gate_mode: prd-gate` plus the report's `final_gate_verdict` /
     `gate_aggregate` / `gate_confidence` into the frontmatter (copy, never
     hand-edit). Verdict FAIL → do not land; rework per the report's Evidence
     (back to stage 2/5, max 3 rounds).
   - **Unavailable** → use the stage-5 self-review verdict and **must** write
     `gate_mode: self-reported` — downstream consumers treat that verdict with capped trust.
5. Write the session snapshot `docs/prd/{slug}-snapshot.md` (`templates/open-items-snapshot.md`).
6. Report to the user: PRD path + gate verdict (with gate_mode) + snapshot path +
   bucket tally (A:B:C counts + discards).

### Stage 8 — Auto-retrospective (do not bother the user)

After landing, before the closing summary, write a structured retro to
`skills/req-dev-lite/sessions/YYYY-MM-DD-HHMM-{slug}.md` using `sessions/_template.md`.
Hard rules: never modify SKILL.md/templates here; no raw transcript (structured
data only); redact PII from quoted user words. Interrupted sessions also get a
retro with `status: aborted|paused`.

## Anti-pattern self-checks

- **Compliment trap**: "sounds great" / "should be fine" → demand a concrete example.
- **Future-tense trap**: "later" / "users will" → pull back to the past: "when did this last happen?"
- **Solution-as-requirement**: "add a toggle" / "build a dashboard" → 5 Whys interceptor.
- **Abstract-AC trap**: "handle errors properly" → demand a Gherkin example.
- **Happy-path trap**: only success flows described → stage 4.5.

## User-initiated Stop (resumable state)

| Type | Trigger | Meaning |
|---|---|---|
| `user_initiated` | "park it", "I'm tired", "good enough", "just generate the PRD", "GRILL ENOUGH" | user's call; resume later |
| `agent_failed` | ≥3 consecutive turns stuck on the same question / grilling loop / evasive answers | agent failure → retro signal |

On stop (either type): unanswered items → Bucket C rows tagged `[resumable]` with
"stuck at stage N"; jump to stage 6 and land a PRD from the answered portion with
frontmatter `status: partial`; write resume fields into the snapshot
(`pending_stage`, `pending_items`, `stop_reason`, `resumable_slug`); retro gets
`status: paused`.

Resume ("continue req-dev-lite <slug>"): find `{slug}-snapshot.md` in `docs/prd/`,
read `pending_stage`/`pending_items`, continue from there (ask the pending items
first, never restart), new retro with `resumed_from`, then flip `[resumable]` rows
to `resolved` or `still-open`.

## When to stop

Not "all questions asked" — **all three buckets settled and the final gate passed**.
A user-initiated Stop is also a legitimate stop; `agent_failed` is not — it is a
failure for the retro loop to digest.

## Verification checklist (before the closing summary)

- [ ] Required inputs satisfied (project root writable)
- [ ] Stage 0 preflight ran (CONTEXT / PRD history / full-vs-lite disambiguation)
- [ ] Stage 1 Why and Who nailed down **before** What (core veto not bypassed)
- [ ] 5 Whys interceptor fired whenever solution language appeared
- [ ] Every story has ≥1 Gherkin example **with real values**
- [ ] Cockburn Extensions enumerated for every happy path
- [ ] Stage 5 tri-state verdict explicit; stage 7 gate ran (or `gate_mode: self-reported` set)
- [ ] Five anti-patterns audited; hits counted in the retro
- [ ] Buckets A+B+C account for 100% of candidate requirements — nothing silently dropped
- [ ] PRD file + snapshot + stage-8 retro all written
- [ ] If stopped: `stop_reason` classified, snapshot has full resume info

## Files

**Self-contained (no dependency on anything outside this repo). Every document is
bilingual: English canonical + a `.zh.md` Chinese sibling.**
- `references/methods.md` — the 12 methods annotated (5 core + 2 checks + 5 optional)
- `references/question-bank.md` — Mom Test banned/mandatory questions + Impact
  Mapping openers + 5 Whys triggers + Cockburn/7-label/domain-calibration questions
- `references/quality-gateway.md` — Volere 4 + 7-label criteria with examples
  (**the prd-gate scoring anchor**)
- `references/attribution.md` — verified sources, licenses + safety-review log
- `templates/prd-local.en.md` / `templates/prd-local.md` — the PRD contract (EN / 中文 — these two ARE the bilingual pair)
- `templates/user-story.md`, `templates/open-items-snapshot.md`
- `sessions/_template.md`, `sessions/README.md`

## Downstream consumer contract (interface to auto-dev-lite)

The PRD this skill produces is the **input contract** for auto-dev-lite step 0.5:
section numbering, `US-NNN` heading shape, the 7-field story body order, and the
9-column Open Items table are parsed mechanically. Do not restructure them.
Frontmatter consumed downstream: `status`, `final_gate_verdict`, `gate_mode`
(absent = `self-reported`), `gate_confidence`, `session_id`, `snapshot`.
Full contract: `../auto-dev-lite/references/prd-import-rules.md`.
Template changes require the sync protocol described there (update both sides + regression on a historical PRD).

Current alignment: **templates/prd-local(.en).md @ 2026-06-10** ↔ prd-import-rules contract @ 2026-06-10.
