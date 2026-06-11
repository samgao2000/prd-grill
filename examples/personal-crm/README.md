# Worked example: personal CRM

Real artifacts from one pipeline pass (2026-05-19), unedited:

- `prd.md` — the PRD produced by req-dev-lite (8 user stories, Chinese; the bilingual
  contract accepts either language). Kept **verbatim** — including links to the
  producing workspace's session retro, which is intentionally not published.
- `personal-crm-snapshot.md` — the session snapshot (bucket tally, open-items digest).
- `prd.gate.md` / `prd.gate.json` — the prd-gate report: PASS-WITH-OPEN-ITEMS,
  aggregate 0.97, US-002 flagged for solution language pending judge review.

Reproduce the score: `prd-gate score --prd examples/personal-crm/prd.md`

The implementation run from an earlier version of this PRD shipped 8 stories /
51 tests / 94% coverage in 32 minutes AFK (single-LLM review, git mode).
