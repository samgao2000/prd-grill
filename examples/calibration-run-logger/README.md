# Worked example: calibration run logger (English, warts included)

A complete, unedited pipeline pass from 2026-06-10, in English. The requirement is
the repo's own roadmap item: a logger that pairs each run's gate score with its
rework outcome, so the score-vs-rework correlation can be computed at run #10.

- `prd.md` — the PRD: 3 user stories, 3 outcome metrics, 3 open items.
  Final verdict: **PASS-WITH-OPEN-ITEMS, aggregate 0.96, confidence 0.85.**
- `prd.gate.json` / `prd.gate.md` — the final gate report.
- `snapshot.md` — the session snapshot, including the full gate trajectory.

## Why this example is worth reading

The interrogation itself was smooth: six questions, every recommended answer
accepted on first ask. Everything after that shows the gate earning its keep:

1. **The gate stopped its own author.** The first drafting session burned all
   three rework rounds (each patch fixed the cited failures and introduced new
   cross-story inconsistencies) and the session was halted by the gate's own
   3-round rule, verdict FAIL at that point. Work resumed only after the
   requirement owner made the one genuinely open decision (corruption policy:
   quarantine-and-continue).
2. **Judge variance is real.** Round 1's judge accepted CLI names and file paths
   in acceptance criteria as "observable contract surface"; round 2's judge
   scored the same pattern `solution_free = 0.0`, correctly noting the PRD's own
   decision log listed alternatives to those choices. The stricter reading
   prevailed — consistent with the merge policy.
3. **Strict fresh judges may not converge to zero.** Each round surfaced one
   progressively-narrower condition-interaction ambiguity. The final finding
   (precedence between the quarantine sweep and duplicate-run_id rejection) hit
   no individual story, which is exactly the case PASS-WITH-OPEN-ITEMS exists
   for: it became OI-003 with an owner and a deadline instead of a fourth
   rework round.

Reproduce the deterministic score: `prd-gate score --prd examples/calibration-run-logger/prd.md`
