# AUTO_DEV_ACCEPTANCE: immutable
"""Acceptance tests for US-001: Emit one validated calibration record per completed run.
Hand-translated from the Gherkin AC in docs/prd/2026-06-10-calibration-run-logger.md."""
import json
from pathlib import Path

import pytest

from prd_gate.cli import main

GATE_DIMS = ["contradiction", "dangling", "fallacy", "gap", "no_weasel", "overreach",
             "redundancy", "solution_free", "testable", "traceable", "unowned"]


def make_run(root: Path, run_id="20260610-a1b2c3", issues=8, retries=2, blocked=1,
             needs_review=1, finished=True) -> Path:
    rd = root / "runs" / run_id
    rd.mkdir(parents=True)
    with (rd / "log.jsonl").open("w", encoding="utf-8") as f:
        def ev(e, **kw):
            f.write(json.dumps({"event": e, **kw}) + "\n")
        for i in range(issues):
            ev("issue_fetched", issue_id=f"US-{i+1:03d}")
        for _ in range(retries):
            ev("pytest_failed", issue_id="US-002")
        for i in range(blocked):
            ev("issue_blocked", issue_id=f"US-{i+1:03d}")
        for i in range(needs_review):
            ev("issue_needs_review", issue_id=f"US-{i+2:03d}")
        if finished:
            ev("run_finished", terminal_state="done")
    return rd


def make_prd(root: Path, gated=True, with_report=True) -> Path:
    prd = root / "docs" / "prd" / "2026-06-10-sample.md"
    prd.parent.mkdir(parents=True)
    if gated:
        fm = ("---\ntitle: Sample\nslug: sample\ngate_mode: prd-gate\n"
              "final_gate_verdict: PASS-WITH-OPEN-ITEMS\ngate_aggregate: 0.97\n"
              "gate_confidence: 0.85\ngate_report: sample.gate.json\n---\n# Sample\n")
        if with_report:
            (prd.parent / "sample.gate.json").write_text(json.dumps(
                {"dimensions": {d: {"score": 1.0} for d in GATE_DIMS}}), encoding="utf-8")
    else:
        fm = "---\ntitle: Sample\nslug: sample\n---\n# Sample\n"
    prd.write_text(fm, encoding="utf-8")
    return prd


def seed_dataset(root: Path, n=4) -> Path:
    ds = root / "runs" / "calibration.jsonl"
    ds.parent.mkdir(parents=True, exist_ok=True)
    with ds.open("w", encoding="utf-8") as f:
        for i in range(n):
            f.write(json.dumps({"schema": "calib/v1", "run_id": f"seed-{i}",
                                "run_status": "completed", "gate_mode": "prd-gate",
                                "gate_aggregate": 0.9, "gate_confidence": 0.85,
                                "gate_dimensions": {d: 1.0 for d in GATE_DIMS},
                                "outcomes": {"total_issues": 4, "retry_cycles": 0,
                                             "blocked": 0, "needs_review": 0},
                                "weights": {"retry": 1, "blocked": 3, "needs_review": 2},
                                "rework_rate": 0.0, "human_minutes": None}) + "\n")
    return ds


def test_completed_run_appends_exactly_one_record(tmp_path):
    rd = make_run(tmp_path)
    prd = make_prd(tmp_path)
    ds = seed_dataset(tmp_path, n=4)
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 0
    rows = [json.loads(l) for l in ds.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 5
    new = rows[-1]
    assert new["rework_rate"] == pytest.approx(0.875)  # (2 + 1*3 + 1*2) / 8
    assert new["run_status"] == "completed"
    assert new["gate_mode"] == "prd-gate"
    assert sorted(new["gate_dimensions"].keys()) == sorted(GATE_DIMS)


def test_ext_1a_missing_event_log_rejected(tmp_path):
    rd = tmp_path / "runs" / "20260610-a1b2c3"
    rd.mkdir(parents=True)  # no log.jsonl
    prd = make_prd(tmp_path)
    ds = seed_dataset(tmp_path, n=1)
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 2
    assert len(ds.read_text(encoding="utf-8").splitlines()) == 1


def test_ext_1b_ungated_prd_written_as_self_reported(tmp_path, capsys):
    rd = make_run(tmp_path)
    prd = make_prd(tmp_path, gated=False)
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 0
    ds = tmp_path / "runs" / "calibration.jsonl"
    row = json.loads(ds.read_text(encoding="utf-8").splitlines()[-1])
    assert row["gate_mode"] == "self-reported"
    assert row["gate_aggregate"] is None
    assert row["gate_confidence"] is None
    assert row["gate_dimensions"] is None
    assert "warning" in capsys.readouterr().err.lower()


def test_ext_1c_gated_prd_without_report_rejected(tmp_path):
    rd = make_run(tmp_path)
    prd = make_prd(tmp_path, gated=True, with_report=False)
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 2
    assert not (tmp_path / "runs" / "calibration.jsonl").exists()


def test_ext_2a_dataset_created_when_absent(tmp_path):
    rd = make_run(tmp_path)
    prd = make_prd(tmp_path)
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 0
    rows = (tmp_path / "runs" / "calibration.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1


def test_ext_2b_duplicate_run_id_rejected(tmp_path):
    rd = make_run(tmp_path)
    prd = make_prd(tmp_path)
    assert main(["calib", "add", "--run", str(rd), "--prd", str(prd)]) == 0
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 2
    rows = (tmp_path / "runs" / "calibration.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1


def test_ext_3a_aborted_run_recorded_as_aborted(tmp_path):
    rd = make_run(tmp_path, finished=False)  # no run_finished event => aborted
    prd = make_prd(tmp_path)
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 0
    row = json.loads((tmp_path / "runs" / "calibration.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert row["run_status"] == "aborted"
