# prd-grill + ECC

[中文版 → README.zh.md](README.zh.md)

[ECC](https://github.com/affaan-m/ECC) gives a coding agent an engineering
system: `plan -> test -> implement -> review -> verify -> remember -> improve`.
Every gate in that chain sits **after** code exists. Nothing checks the
requirement the plan was built from.

prd-grill is the stage before `/ecc:plan`. It interrogates the requirement
until it is falsifiable, scores the resulting PRD with an independent judge,
and — with this integration — refuses to let ECC plan or build from a PRD that
never passed.

```
prd-grill                                  ECC
──────────────────────────────────────     ──────────────────────────────────────
req-dev-lite   (grill, human answers)
      ↓
prd-gate score (deterministic floor)
      ↓
prd-judge      (fresh-context agent)   ──► product-capability   (PRD → constraints)
      ↓                                          ↓
prd-gate merge → PRD frontmatter        ──► /ecc:plan            (plan artifact)
      │  final_gate_verdict                      ↓
      │  gate_mode: prd-gate            ──► tdd-workflow         (RED → GREEN, evidence report)
      │  gate_confidence                         ↓
      └─ prd-gate-guard hook ───────────►  /code-review, verify, remember
         blocks /ecc:plan, tdd-workflow,
         product-capability when the PRD
         is FAIL / unscored / self-graded
```

Nothing in ECC is modified. prd-grill adds three pieces that ECC's own
architecture already has slots for.

## The three pieces

| Piece | File | ECC concept | What it does |
|---|---|---|---|
| Judge agent | [`agents/prd-judge.md`](../../agents/prd-judge.md) | agent (own context, restricted tools) | Answers `judge-tasks.json` from ONLY the PRD + anchor rubric. Independence by construction, not by asking nicely. |
| Guard hook | [`hooks/prd-gate-guard.py`](../../hooks/prd-gate-guard.py) + [`hooks/hooks.json`](../../hooks/hooks.json) | hook (runs outside the model's context, exit 2 blocks) | On `/plan`, `/ecc:plan`, `/tdd`, or a model-invoked `plan` / `tdd-workflow` / `product-capability` / `auto-dev-lite` skill: reads the newest `docs/prd/*.md` frontmatter and blocks unless `final_gate_verdict` is `PASS*` **and** `gate_mode: prd-gate`. |
| Three skills | [`skills/`](../../skills) | skills (ECC's primary surface) | Unchanged. Frontmatter carries `metadata.origin: prd-grill` and a `When to Activate` section in ECC's format. |

The guard closes the gap the gate's README admits: "independence is enforced by
discipline, not technology." A self-graded PASS is now blocked by a mechanism.

## Install

### With the Claude Code plugin (recommended)

```
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
/plugin marketplace add samgao2000/prd-grill
/plugin install prd-grill@prd-grill
```

The prd-grill plugin ships the skills, the `prd-judge` agent, and the guard
hook. Order does not matter; neither plugin depends on the other at install
time.

### Manual (ECC installed via `./install.sh`, or project-local)

```bash
git clone https://github.com/samgao2000/prd-grill
python prd-grill/integrations/ecc/install.py            # → ~/.claude
python prd-grill/integrations/ecc/install.py --project  # → ./.claude  (run inside your project)
```

Idempotent. Merges two hook entries into `settings.json`, copies the agent,
the guard, and the three skills. `--dry-run` shows the plan; `--uninstall`
removes the hook entries.

### The gate CLI

```bash
pip install "prd-grill @ git+https://github.com/samgao2000/prd-grill"
```

Stdlib-only. Required for the deterministic layer; without it the PRD stays
`gate_mode: self-reported` and the guard will block planning — which is the
intended behaviour.

## Daily flow

```
"grill my requirements"                      → docs/prd/2026-10-25-billing-alerts.md
prd-gate score --prd docs/prd/2026-10-25-billing-alerts.md
                                             → .judge-tasks.json, exit 2 if already FAIL
"use the prd-judge agent on docs/prd/2026-10-25-billing-alerts.judge-tasks.json"
                                             → .judge-results.json  (fresh context)
prd-gate merge --prd ... --judge-results ... → .gate.json / .gate.md + frontmatter patch
paste the frontmatter patch into the PRD

/ecc:plan "billing alerts per docs/prd/2026-10-25-billing-alerts.md"
                                             → guard: OK PASS-WITH-OPEN-ITEMS (gate_confidence=0.85)
tdd-workflow                                 → RED → GREEN, evidence report
```

If the verdict is FAIL, or you skipped the judge, `/ecc:plan` returns:

```
[prd-gate-guard] BLOCKED 2026-10-25-billing-alerts.md: verdict PASS is gate_mode=self-reported.
The author model graded its own PRD. Run `prd-gate score` + the prd-judge agent + `prd-gate merge`, then retry.
```

## Guard behaviour, exactly

| Situation | Result |
|---|---|
| Prompt/skill is not a planning or build trigger | pass, silent |
| Trigger, but the project has no `docs/prd/` | pass with a one-line advisory (`PRD_GATE_GUARD=strict` → block) |
| Newest PRD: `PASS` / `PASS-WITH-OPEN-ITEMS` and `gate_mode: prd-gate` | pass, prints verdict + confidence |
| Newest PRD: `PASS*` but `gate_mode: self-reported` or missing | **block** |
| Newest PRD: `FAIL` / `not_reached` / no frontmatter | **block** |
| `PRD_GATE_GUARD=off` | pass, silent |
| `PRD_GATE_GUARD_PRD=<path>` | gate that file instead of the newest |
| `req-dev-lite`, `prd-gate` skills | never blocked (they *are* the gate) |

"Newest" = highest `YYYY-MM-DD` filename prefix in `docs/prd/`, mtime on ties.
`*.gate.md`, `*-snapshot.md`, `*.judge-*.json` are ignored.

## What the integration does not do (yet)

- **Calibration from ECC runs.** `prd-gate calib add` derives rework outcomes
  from auto-dev-lite's run-log events (`pytest_failed`, `issue_blocked`, ...).
  ECC's `tdd-workflow` leaves a different trail (checkpoint commits + the
  `.tdd.md` evidence report). An adapter that maps RED/GREEN evidence to the
  calib event vocabulary is the next item; until then, runs built with
  tdd-workflow are not admissible calibration records.
- **Gate the plan artifact.** The guard gates the PRD, not `*.plan.md`.
  Gating plans is a different rubric and out of scope here.
- **Replace ECC's hooks runtime.** The guard is two plain hook entries; it does
  not use or depend on ECC's hook dispatcher.

## Why not contribute this into ECC directly?

It may happen later, with calibration data (≥10 gated runs). Until then the
integration lives here so the method stays attributable and the three skills
stay installable on their own. ECC's adaptation policy ("copy the idea, not
the identity") is reasonable for a harness; for a method, provenance matters.
Hence `metadata.origin: prd-grill` in every skill and `CITATION.cff` at the
repo root.

— Sam Gao, 2026
