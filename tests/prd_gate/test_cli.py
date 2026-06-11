import json

from prd_gate.cli import main
from prd_gate.judge import JUDGE_DIMENSIONS


def test_score_good_prd_emits_reports_and_judge_tasks(good_prd_file, capsys):
    rc = main(["score", "--prd", str(good_prd_file)])
    assert rc == 0
    base = good_prd_file.with_suffix("")
    gate = json.loads((base.parent / (base.name + ".gate.json")).read_text(encoding="utf-8"))
    assert gate["schema"] == "prd-gate/v1"
    assert gate["judge_pending"] is True
    assert gate["verdict"] == "PASS"
    assert gate["requirement_confidence"] == 1.0
    tasks = json.loads((base.parent / (base.name + ".judge-tasks.json")).read_text(encoding="utf-8"))
    assert {t["dimension"] for t in tasks["tasks"]} == set(JUDGE_DIMENSIONS)
    assert "FRESH context" in tasks["independence_rule"]


def test_score_bad_prd_exits_2(bad_prd_file):
    rc = main(["score", "--prd", str(bad_prd_file)])
    assert rc == 2
    gate = json.loads(bad_prd_file.with_suffix("").with_suffix("").parent
                      .joinpath("2026-06-10-bad.gate.json").read_text(encoding="utf-8"))
    assert gate["verdict"] == "FAIL"
    assert gate["core_veto"]["vetoed"] is True
    assert gate["requirement_confidence"] <= 0.5


def test_merge_with_judge_results(good_prd_file, tmp_path):
    # all-pass judge except gap finds an incomplete extension on US-002
    results = {
        dim: {"score": 1.0, "applicable": 2, "failures": []}
        for dim in JUDGE_DIMENSIONS
    }
    results["gap"] = {"score": 0.5, "applicable": 2,
                      "failures": [{"unit": "US-002", "detail": "no branch for Slack API down"}]}
    jr = tmp_path / "judge-results.json"
    jr.write_text(json.dumps(results), encoding="utf-8")
    rc = main(["merge", "--prd", str(good_prd_file), "--judge-results", str(jr)])
    base = good_prd_file.with_suffix("")
    gate = json.loads((base.parent / (base.name + ".gate.json")).read_text(encoding="utf-8"))
    assert gate["judge_pending"] is False
    # 严判优先: merged gap = min(1.0 deterministic, 0.5 judge)
    assert gate["dimensions"]["gap"]["score"] == 0.5
    assert gate["dimensions"]["gap"]["judged_by"] == "merged"
    # 2 stories, 1 failed, allowed = floor(0.4) = 0 -> FAIL
    assert gate["verdict"] == "FAIL"
    assert rc == 2


def test_judge_is_authoritative_for_solution_free(good_prd_file, tmp_path):
    # deterministic would not flag the good PRD; simulate the inverse case at
    # unit level: judge clears a deterministic solution_free signal.
    from prd_gate.checks import DimensionResult, Finding
    from prd_gate.judge import merge
    det = [DimensionResult("solution_free", 0.5, "deterministic", 2,
                           [Finding("US-002", "solution terms: sqlite")])]
    judged = {"solution_free": DimensionResult("solution_free", 1.0, "llm", 2, [])}
    out = {d.dimension: d for d in merge(det, judged)}
    assert out["solution_free"].score == 1.0          # judge overrides signal
    assert len(out["solution_free"].failures) == 1    # evidence stays auditable
    # contrast: non-authoritative dim keeps min()
    det2 = [DimensionResult("gap", 1.0, "deterministic", 2, [])]
    judged2 = {"gap": DimensionResult("gap", 0.5, "llm", 2, [Finding("US-001", "x")])}
    out2 = {d.dimension: d for d in merge(det2, judged2)}
    assert out2["gap"].score == 0.5
