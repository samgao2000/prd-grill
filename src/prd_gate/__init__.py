"""prd-gate — measurable spec-quality gate between req-dev (spec produced)
and auto-dev (build started).

Scores a PRD on 11 dimensions (Volere 4 + 7 标签) against the single anchor
skills/req-dev/references/quality-gateway.md, producing a machine-readable
report whose `requirement_confidence` feeds auto_dev escalation (M5).
"""

__version__ = "0.1.0"
