# AUTO_DEV_ACCEPTANCE: immutable
"""Acceptance tests for US-003: One-command correlation report with explicit exclusions.
Hand-translated from the Gherkin AC in docs/prd/2026-06-10-calibration-run-logger.md."""
import json
import time
from pathlib import Path

from prd_gate.cli import main

from test_calib_us001 import GATE_DIMS


def write_dataset(root: Path, rows) -> Path:
    ds = root / "runs" / "calibration.jsonl"
    ds.parent.mkdir(parents=True, exist_ok=True)
    with ds.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return ds


def rec(i, status="completed", mode="prd-gate", agg=None, rework=None):
    agg = 0.80 + i * 0.02 if agg is None else agg
    rework = round(1.5 - i * 0.12, 4) if rework is None else rework
    return {"schema": "calib/v1", "run_id": f"r-{i:02d}", "run_status": status,
            "gate_mode": mode,
            "gate_aggregate": agg if mode == "prd-gate" else None,
            "gate_confidence": 0.85 if mode == "prd-gate" else None,
            "gate_dimensions": {d: 1.0 for d in GATE_DIMS} if mode == "prd-gate" else None,
            "outcomes": {"total_issues": 8, "retry_cycles": 0, "blocked": 0, "needs_review": 0},
            "weights": {"retry": 1, "blocked": 3, "needs_review": 2},
            "rework_rate": rework, "human_minutes": None}


def test_report_correlates_only_valid_and_names_exclusions(tmp_path, capsys):
    rows = [rec(i) for i in range(10)]
    rows.append(rec(10, status="aborted"))
    rows.append(rec(11, mode="self-reported"))
    write_dataset(tmp_path, rows)
    t0 = time.monotonic()
    rc = main(["calib", "report", "--target", str(tmp_path)])
    elapsed = time.monotonic() - t0
    assert rc == 0
    out = capsys.readouterr().out
    table_rows = [l for l in out.splitlines() if l.startswith("r-")]
    assert len(table_rows) == 10
    assert "Pearson r" in out and "Spearman rho" in out
    assert "excluded: 1 aborted, 1 self-reported" in out
    assert elapsed < 60


def test_ext_1a_fewer_than_three_pairs_suppresses_correlation(tmp_path, capsys):
    write_dataset(tmp_path, [rec(0), rec(1)])
    assert main(["calib", "report", "--target", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "n < 3: correlation not computed" in out
    assert "Pearson" not in out


def test_ext_1b_zero_variance_suppresses_correlation(tmp_path, capsys):
    write_dataset(tmp_path, [rec(i, agg=0.9) for i in range(4)])
    assert main(["calib", "report", "--target", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "correlation not computed" in out


def test_ext_2a_missing_dataset_fails_with_guidance(tmp_path, capsys):
    rc = main(["calib", "report", "--target", str(tmp_path)])
    assert rc == 2
    assert "record at least one run" in capsys.readouterr().err


def test_ext_3a_all_records_excluded_summary_still_printed(tmp_path, capsys):
    write_dataset(tmp_path, [rec(0, status="aborted"), rec(1, mode="self-reported")])
    assert main(["calib", "report", "--target", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "excluded: 1 aborted, 1 self-reported" in out
    assert len([l for l in out.splitlines() if l.startswith("r-")]) == 0


def test_ext_4a_quarantine_disclosed(tmp_path, capsys):
    write_dataset(tmp_path, [rec(i) for i in range(3)])
    q = tmp_path / "runs" / "calibration.quarantine.jsonl"
    q.write_text(json.dumps({"original_position": 9, "raw": "x"}) + "\n", encoding="utf-8")
    assert main(["calib", "report", "--target", str(tmp_path)]) == 0
    assert "quarantined: 1" in capsys.readouterr().out


def test_ext_4b_unrecorded_runs_listed(tmp_path, capsys):
    write_dataset(tmp_path, [rec(i) for i in range(3)])
    orphan = tmp_path / "runs" / "20260611-orphan"
    orphan.mkdir()
    (orphan / "log.jsonl").write_text('{"event": "issue_fetched", "issue_id": "US-001"}\n', encoding="utf-8")
    assert main(["calib", "report", "--target", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "unrecorded runs: 20260611-orphan" in out


def test_ext_4c_corrupted_record_excluded_and_disclosed(tmp_path, capsys):
    ds = write_dataset(tmp_path, [rec(i) for i in range(4)])
    with ds.open("a", encoding="utf-8") as f:
        f.write('{"half": \n')
    assert main(["calib", "report", "--target", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "corrupted: 1 record at position 5 (quarantined at next append)" in out
    assert len([l for l in out.splitlines() if l.startswith("r-")]) == 4
