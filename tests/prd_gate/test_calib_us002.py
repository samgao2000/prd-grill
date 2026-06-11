# AUTO_DEV_ACCEPTANCE: immutable
"""Acceptance tests for US-002: Reject malformed records at append time.
Hand-translated from the Gherkin AC in docs/prd/2026-06-10-calibration-run-logger.md."""
import json
from pathlib import Path

from prd_gate.cli import main

from test_calib_us001 import GATE_DIMS, make_run, make_prd, seed_dataset


def candidate(run_id="cand-1", rework_rate=0.875, **over):
    rec = {"schema": "calib/v1", "run_id": run_id, "run_status": "completed",
           "gate_mode": "prd-gate", "gate_aggregate": 0.97, "gate_confidence": 0.85,
           "gate_dimensions": {d: 1.0 for d in GATE_DIMS},
           "outcomes": {"total_issues": 8, "retry_cycles": 2, "blocked": 1, "needs_review": 1},
           "weights": {"retry": 1, "blocked": 3, "needs_review": 2},
           "rework_rate": rework_rate, "human_minutes": None}
    rec.update(over)
    return rec


def add_record(tmp_path, rec):
    rd = tmp_path / "runs" / "dummy"
    rd.mkdir(parents=True, exist_ok=True)
    rf = tmp_path / "candidate.json"
    rf.write_text(json.dumps(rec), encoding="utf-8")
    return main(["calib", "add", "--run", str(rd), "--record", str(rf)])


def test_inconsistent_rework_arithmetic_rejected(tmp_path, capsys):
    ds = seed_dataset(tmp_path, n=2)
    rc = add_record(tmp_path, candidate(rework_rate=0.5))
    assert rc == 2
    err = capsys.readouterr().err
    assert "rework_rate 0.5 != computed 0.875" in err
    assert len(ds.read_text(encoding="utf-8").splitlines()) == 2


def test_ext_1a_illegal_run_status_rejected(tmp_path, capsys):
    rc = add_record(tmp_path, candidate(run_status="exploded"))
    assert rc == 2
    assert "completed" in capsys.readouterr().err  # legal values listed


def test_ext_1b_illegal_gate_mode_rejected(tmp_path, capsys):
    rc = add_record(tmp_path, candidate(gate_mode="maybe"))
    assert rc == 2
    assert "self-reported" in capsys.readouterr().err


def test_ext_2a_negative_count_rejected(tmp_path, capsys):
    rec = candidate()
    rec["outcomes"]["blocked"] = -1
    rc = add_record(tmp_path, rec)
    assert rc == 2
    assert "blocked" in capsys.readouterr().err


def test_ext_3a_corrupted_record_quarantined_and_append_continues(tmp_path, capsys):
    ds = seed_dataset(tmp_path, n=2)
    with ds.open("a", encoding="utf-8") as f:
        f.write('{"schema": "calib/v1", "run_id": "half-written\n')
    rc = add_record(tmp_path, candidate())
    assert rc == 0
    out = capsys.readouterr().out
    assert "quarantined: 1 record at position 3" in out
    rows = [json.loads(l) for l in ds.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 3  # 2 seeds + the new record; corrupted line moved out
    q = tmp_path / "runs" / "calibration.quarantine.jsonl"
    assert q.exists() and len(q.read_text(encoding="utf-8").splitlines()) == 1
