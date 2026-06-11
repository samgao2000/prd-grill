"""Aggregate dimension scores -> verdict + requirement_confidence.

Verdict semantics replicate req-dev 阶段 5 exactly:
- PASS                  — every story passes every story-scoped dimension,
                          no PRD-level hits, no core veto.
- PASS-WITH-OPEN-ITEMS  — failed stories <= floor(0.2 * N), no core veto.
- FAIL                  — beyond threshold, or core Why/Who veto (一票否决).

requirement_confidence feeds auto_dev.modules.escalation.RunState
(threshold 0.7 -> soft_escalate).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .checks import CoreVeto, DimensionResult

# Severity weights. Contradiction breaks builds outright; redundancy wastes
# effort but rarely ships defects.
WEIGHTS: dict[str, float] = {
    "testable": 1.25,
    "traceable": 1.25,
    "solution_free": 1.0,
    "no_weasel": 1.0,
    "contradiction": 1.5,
    "gap": 1.25,
    "fallacy": 1.0,
    "redundancy": 0.75,
    "dangling": 1.0,
    "overreach": 1.0,
    "unowned": 1.0,
}

# Story-scoped dimensions used for the per-story pass/fail roll-up.
STORY_SCOPED = ("testable", "traceable", "solution_free", "no_weasel", "gap", "dangling")

VERDICT_PASS = "PASS"
VERDICT_POI = "PASS-WITH-OPEN-ITEMS"
VERDICT_FAIL = "FAIL"


@dataclass
class GateResult:
    verdict: str
    aggregate: float
    requirement_confidence: float
    failed_stories: list[str]
    allowed_failures: int
    total_stories: int
    core_veto: CoreVeto
    dimensions: list[DimensionResult] = field(default_factory=list)
    judge_pending: bool = False   # True when judge dims not yet merged


def aggregate_score(dimensions: list[DimensionResult]) -> float:
    num = sum(WEIGHTS.get(d.dimension, 1.0) * d.score for d in dimensions)
    den = sum(WEIGHTS.get(d.dimension, 1.0) for d in dimensions)
    return round(num / den, 4) if den else 0.0


def failed_story_ids(dimensions: list[DimensionResult]) -> list[str]:
    ids: set[str] = set()
    for d in dimensions:
        if d.dimension in STORY_SCOPED:
            ids.update(f.unit for f in d.failures if f.unit.startswith("US-"))
    return sorted(ids)


def decide(dimensions: list[DimensionResult], core_veto: CoreVeto,
           total_stories: int, judge_pending: bool = False) -> GateResult:
    agg = aggregate_score(dimensions)
    failed = failed_story_ids(dimensions)
    allowed = math.floor(total_stories * 0.2)
    prd_level_hit = any(
        d.dimension in ("contradiction", "redundancy", "fallacy", "overreach", "unowned")
        and d.score < 1.0
        for d in dimensions
    )

    if core_veto.vetoed:
        verdict = VERDICT_FAIL
    elif total_stories == 0:
        verdict = VERDICT_FAIL  # a PRD with no parseable stories is not a spec
    elif len(failed) == 0 and not prd_level_hit:
        verdict = VERDICT_PASS
    elif len(failed) <= allowed:
        verdict = VERDICT_POI
    else:
        verdict = VERDICT_FAIL

    confidence = agg
    if core_veto.vetoed or verdict == VERDICT_FAIL:
        confidence = min(confidence, 0.5)   # force below escalation threshold 0.7
    elif verdict == VERDICT_POI:
        confidence = min(confidence, 0.85)

    return GateResult(
        verdict=verdict,
        aggregate=agg,
        requirement_confidence=round(confidence, 4),
        failed_stories=failed,
        allowed_failures=allowed,
        total_stories=total_stories,
        core_veto=core_veto,
        dimensions=dimensions,
        judge_pending=judge_pending,
    )
