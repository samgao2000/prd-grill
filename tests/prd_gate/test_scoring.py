import math

from prd_gate.checks import CoreVeto, DimensionResult, Finding
from prd_gate import scoring


def _dim(name, score, fail_units=()):
    return DimensionResult(name, score, "deterministic", 5,
                           [Finding(u, "x") for u in fail_units])


NO_VETO = CoreVeto(vetoed=False, reasons=[])
VETO = CoreVeto(vetoed=True, reasons=["core Why missing"])


def test_all_pass_is_pass():
    dims = [_dim(n, 1.0) for n in scoring.WEIGHTS]
    r = scoring.decide(dims, NO_VETO, total_stories=5)
    assert r.verdict == scoring.VERDICT_PASS
    assert r.aggregate == 1.0
    assert r.requirement_confidence == 1.0


def test_within_20pct_is_pass_with_open_items():
    # 1 of 10 stories fails testable -> allowed = floor(10*0.2) = 2
    dims = [_dim(n, 1.0) for n in scoring.WEIGHTS if n != "testable"]
    dims.append(_dim("testable", 0.9, ["US-003"]))
    r = scoring.decide(dims, NO_VETO, total_stories=10)
    assert r.verdict == scoring.VERDICT_POI
    assert r.failed_stories == ["US-003"]
    assert r.requirement_confidence <= 0.85


def test_small_prd_has_zero_allowance():
    # 4 stories -> floor(0.8) = 0 -> any failure is FAIL (matches 阶段 5 table)
    dims = [_dim(n, 1.0) for n in scoring.WEIGHTS if n != "testable"]
    dims.append(_dim("testable", 0.75, ["US-002"]))
    r = scoring.decide(dims, NO_VETO, total_stories=4)
    assert r.allowed_failures == 0
    assert r.verdict == scoring.VERDICT_FAIL
    assert r.requirement_confidence <= 0.5


def test_core_veto_overrides_perfect_scores():
    dims = [_dim(n, 1.0) for n in scoring.WEIGHTS]
    r = scoring.decide(dims, VETO, total_stories=5)
    assert r.verdict == scoring.VERDICT_FAIL
    assert r.requirement_confidence <= 0.5  # forces soft_escalate (threshold 0.7)


def test_zero_stories_is_fail():
    r = scoring.decide([_dim("unowned", 1.0)], NO_VETO, total_stories=0)
    assert r.verdict == scoring.VERDICT_FAIL


def test_aggregate_is_weighted():
    dims = [_dim("contradiction", 0.0), _dim("redundancy", 1.0)]
    agg = scoring.aggregate_score(dims)
    assert math.isclose(agg, 0.75 / (1.5 + 0.75), abs_tol=1e-4)
