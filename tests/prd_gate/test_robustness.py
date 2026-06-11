"""Regression tests for pre-publish hardening (non-Claude / external-user paths)."""
import json
import os
from pathlib import Path

import pytest

from prd_gate.cli import main, resolve_anchor
from prd_gate.judge import JUDGE_DIMENSIONS, _extract_json_object, load_judge_results


def _results_payload():
    return {dim: {"score": 1.0, "applicable": 2, "failures": []} for dim in JUDGE_DIMENSIONS}


def test_judge_results_with_code_fence(tmp_path):
    f = tmp_path / "r.json"
    f.write_text("```json\n" + json.dumps(_results_payload()) + "\n```", encoding="utf-8")
    assert set(load_judge_results(f)) == set(JUDGE_DIMENSIONS)


def test_judge_results_with_prose_and_nuls(tmp_path):
    f = tmp_path / "r.json"
    f.write_text("Here are my results:\n" + json.dumps(_results_payload()) + "\nDone!\x00\x00",
                 encoding="utf-8")
    assert set(load_judge_results(f)) == set(JUDGE_DIMENSIONS)


def test_judge_results_without_json_fails_actionably():
    with pytest.raises(ValueError, match="no JSON object"):
        _extract_json_object("the PRD looks fine to me")


def test_zero_story_prd_report_carries_parsing_hint(tmp_path, capsys):
    prd = tmp_path / "freeform.md"
    prd.write_text("# My PRD\n\nWe should build a thing that does stuff.\n", encoding="utf-8")
    rc = main(["score", "--prd", str(prd)])
    assert rc == 2  # FAIL by design
    out = capsys.readouterr().out
    assert "Parsing note" in out
    assert "prd-local.en.md" in out


def test_anchor_falls_back_to_packaged_copy(tmp_path, capsys):
    a = resolve_anchor(str(tmp_path / "nope" / "missing.md"))
    assert a.exists()
    assert a.name == "quality-gateway.md"
    assert "packaged rubric" in capsys.readouterr().err


def test_mock_judge_is_disclosed_in_report_mode(tmp_path, monkeypatch, good_prd_file):
    monkeypatch.setenv("PRD_GATE_MOCK", "1")
    rc = main(["score", "--prd", str(good_prd_file), "--judge", "api"])
    assert rc == 0
    base = good_prd_file.with_suffix("")
    gate = json.loads((base.parent / (base.name + ".gate.json")).read_text(encoding="utf-8"))
    assert "mock" in gate["mode"]
    assert all("mock" in d["judged_by"] for d in gate["dimensions"].values()
               if d["judged_by"] not in ("deterministic",))


def test_calib_rejects_mock_gate_report(tmp_path, capsys):
    from test_calib_us001 import make_run, GATE_DIMS
    rd = make_run(tmp_path)
    prd = tmp_path / "docs" / "prd" / "p.md"
    prd.parent.mkdir(parents=True)
    prd.write_text("---\ntitle: P\nslug: p\ngate_mode: prd-gate\ngate_aggregate: 0.9\n"
                   "gate_confidence: 0.85\ngate_report: p.gate.json\n---\n# P\n", encoding="utf-8")
    (prd.parent / "p.gate.json").write_text(json.dumps(
        {"mode": "deterministic+mock-judge",
         "dimensions": {d: {"score": 1.0, "judged_by": "merged-mock"} for d in GATE_DIMS}}),
        encoding="utf-8")
    rc = main(["calib", "add", "--run", str(rd), "--prd", str(prd)])
    assert rc == 2
    assert "not admissible" in capsys.readouterr().err
