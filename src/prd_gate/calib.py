"""Calibration run logger (US-001..003 of docs/prd/2026-06-10-calibration-run-logger.md).

Pairs each pipeline run's gate scores with its rework outcomes so the
score-vs-rework correlation can be computed (target: >=10 paired runs).

Storage (D-002): runs/calibration.jsonl, append-only, one JSON object per line.
Corruption policy (D-005): quarantine-and-continue -> runs/calibration.quarantine.jsonl.
Weights (D-004): retry 1, blocked 3, needs-review 2 — stored in every record.
"""

from __future__ import annotations

import datetime as _dt
import json
import math
import sys
from pathlib import Path

from .parser import parse_frontmatter

SCHEMA = "calib/v1"
WEIGHTS = {"retry": 1, "blocked": 3, "needs_review": 2}
RUN_STATUSES = ("completed", "aborted")
GATE_MODES = ("prd-gate", "self-reported")
DATASET_NAME = "calibration.jsonl"
QUARANTINE_NAME = "calibration.quarantine.jsonl"


class CalibError(Exception):
    """Validation / input error: emission is rejected, nothing is appended."""


# --------------------------------------------------------------- derivation

def outcomes_from_log(log_path: Path) -> tuple[dict, str]:
    """Derive outcome counts per the PRD's Measurement definitions.
    Returns (outcomes, run_status). run_status = aborted when no run_finished event."""
    if not log_path.exists():
        raise CalibError(f"missing run artifact: {log_path}")
    issues: set[str] = set()
    retries = blocked = needs_review = 0
    finished = False
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError as e:
            raise CalibError(f"corrupted run log line: {e}") from e
        kind = ev.get("event")
        if kind == "issue_fetched":
            issues.add(ev.get("issue_id", "?"))
        elif kind == "pytest_failed":
            retries += 1
        elif kind == "issue_blocked":
            blocked += 1
        elif kind == "issue_needs_review":
            needs_review += 1
        elif kind == "run_finished":
            finished = True
    outcomes = {"total_issues": len(issues), "retry_cycles": retries,
                "blocked": blocked, "needs_review": needs_review}
    return outcomes, ("completed" if finished else "aborted")


def rework_rate(outcomes: dict, weights: dict = WEIGHTS) -> float:
    total = outcomes["total_issues"]
    if total <= 0:
        raise CalibError("total_issues must be positive to compute rework_rate")
    raw = (outcomes["retry_cycles"] * weights["retry"]
           + outcomes["blocked"] * weights["blocked"]
           + outcomes["needs_review"] * weights["needs_review"])
    return round(raw / total, 4)


def gate_block_from_prd(prd_path: Path) -> dict:
    """Read gate fields per US-001 ext 1b/1c. Precedence: declared gate_mode governs."""
    fm = parse_frontmatter(prd_path.read_text(encoding="utf-8"))
    mode = fm.get("gate_mode", "self-reported") or "self-reported"
    if mode == "prd-gate":
        report_name = fm.get("gate_report")
        aggregate = fm.get("gate_aggregate")
        if not report_name or not aggregate:
            raise CalibError(
                "PRD declares gate_mode prd-gate but gate artifacts are incomplete "
                f"(gate_report={report_name!r}, gate_aggregate={aggregate!r})")
        report_path = (prd_path.parent / report_name)
        if not report_path.exists():
            raise CalibError(f"PRD declares gate_mode prd-gate but the gate report is unreadable: {report_path}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if "mock" in str(report.get("mode", "")) or any(
                "mock" in str(v.get("judged_by", "")) for v in report["dimensions"].values()):
            raise CalibError(
                "gate report was produced with the mock judge (CI stub); "
                "mock verdicts are not admissible as calibration data")
        dims = {k: v["score"] for k, v in report["dimensions"].items()}
        return {"gate_mode": "prd-gate", "gate_aggregate": float(aggregate),
                "gate_confidence": float(fm.get("gate_confidence") or 0.0),
                "gate_dimensions": dims}
    print("warning: PRD is not independently gated; record written as self-reported "
          "(excluded from correlation)", file=sys.stderr)
    return {"gate_mode": "self-reported", "gate_aggregate": None,
            "gate_confidence": None, "gate_dimensions": None}


# --------------------------------------------------------------- validation

def validate_record(rec: dict) -> None:
    """US-002: reject malformed records at append time."""
    for field in ("schema", "run_id", "run_status", "gate_mode", "outcomes",
                  "weights", "rework_rate"):
        if field not in rec:
            raise CalibError(f"missing required field: {field}")
    if rec["run_status"] not in RUN_STATUSES:
        raise CalibError(f"illegal run_status {rec['run_status']!r}; legal: {RUN_STATUSES}")
    if rec["gate_mode"] not in GATE_MODES:
        raise CalibError(f"illegal gate_mode {rec['gate_mode']!r}; legal: {GATE_MODES}")
    for k, v in rec["outcomes"].items():
        if not isinstance(v, int) or v < 0:
            raise CalibError(f"outcome field {k} must be a non-negative integer, got {v!r}")
    if rec["gate_mode"] == "prd-gate":
        for field in ("gate_aggregate", "gate_confidence", "gate_dimensions"):
            if rec.get(field) is None:
                raise CalibError(f"gate_mode prd-gate requires {field}")
    computed = rework_rate(rec["outcomes"], rec["weights"])
    if abs(computed - float(rec["rework_rate"])) > 1e-6:
        raise CalibError(f"rework_rate {rec['rework_rate']} != computed {computed}")


# --------------------------------------------------------------- dataset io

def _dataset_paths(target_root: Path) -> tuple[Path, Path]:
    runs = target_root / "runs"
    return runs / DATASET_NAME, runs / QUARANTINE_NAME


def load_dataset(ds: Path) -> tuple[list[dict], list[tuple[int, str]]]:
    """Returns (valid_records, corrupted [(position, line), ...])."""
    if not ds.exists():
        return [], []
    records, corrupted = [], []
    for i, line in enumerate(ds.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            corrupted.append((i, line))
    return records, corrupted


def quarantine_and_rewrite(ds: Path, q: Path, records: list[dict],
                           corrupted: list[tuple[int, str]]) -> None:
    """D-005 quarantine-and-continue: corrupted lines move to the quarantine file."""
    with q.open("a", encoding="utf-8") as f:
        for pos, line in corrupted:
            f.write(json.dumps({"quarantined_at": _dt.datetime.now().isoformat(timespec="seconds"),
                                "original_position": pos, "raw": line}) + "\n")
    ds.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
                  encoding="utf-8")
    for pos, _ in corrupted:
        print(f"quarantined: 1 record at position {pos}")


def append_record(target_root: Path, rec: dict) -> Path:
    validate_record(rec)
    ds, q = _dataset_paths(target_root)
    ds.parent.mkdir(parents=True, exist_ok=True)
    records, corrupted = load_dataset(ds)
    if corrupted:
        quarantine_and_rewrite(ds, q, records, corrupted)
    if any(r.get("run_id") == rec["run_id"] for r in records):
        raise CalibError(f"duplicate run_id {rec['run_id']!r}: emission rejected")
    with ds.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return ds


def build_record(run_dir: Path, prd_path: Path) -> dict:
    outcomes, run_status = outcomes_from_log(run_dir / "log.jsonl")
    fm = parse_frontmatter(prd_path.read_text(encoding="utf-8"))
    rec = {"schema": SCHEMA, "run_id": run_dir.name, "run_status": run_status,
           "prd": str(prd_path), "prd_slug": fm.get("slug"),
           "recorded_at": _dt.datetime.now().isoformat(timespec="seconds")}
    rec.update(gate_block_from_prd(prd_path))
    rec["outcomes"] = outcomes
    rec["weights"] = dict(WEIGHTS)
    rec["rework_rate"] = rework_rate(outcomes)
    rec["human_minutes"] = None
    return rec


# --------------------------------------------------------------- statistics

def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def _ranks(v: list[float]) -> list[float]:
    order = sorted(range(len(v)), key=lambda i: v[i])
    ranks = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(_ranks(xs), _ranks(ys))


# --------------------------------------------------------------- report

def report(target_root: Path) -> int:
    ds, q = _dataset_paths(target_root)
    if not ds.exists():
        print("error: no calibration dataset found; record at least one run first "
              "(see US-001 record-emission step)", file=sys.stderr)
        return 2
    records, corrupted = load_dataset(ds)
    for pos, _ in corrupted:
        print(f"corrupted: 1 record at position {pos} (quarantined at next append)")
    valid = [r for r in records
             if r.get("run_status") == "completed" and r.get("gate_mode") == "prd-gate"]
    n_aborted = sum(1 for r in records if r.get("run_status") != "completed")
    n_self = sum(1 for r in records
                 if r.get("run_status") == "completed" and r.get("gate_mode") != "prd-gate")

    print(f"paired records: {len(valid)}")
    print(f"{'run_id':<28}{'gate_aggregate':>15}{'rework_rate':>13}")
    for r in valid:
        print(f"{r['run_id']:<28}{r['gate_aggregate']:>15.4f}{r['rework_rate']:>13.4f}")
    print(f"excluded: {n_aborted} aborted, {n_self} self-reported")
    qn = len(load_dataset(q)[0]) if q.exists() else 0
    if qn:
        print(f"quarantined: {qn}")

    # unrecorded runs (US-003 ext 4b)
    runs_dir = target_root / "runs"
    recorded = {r.get("run_id") for r in records}
    unrecorded = sorted(d.name for d in runs_dir.iterdir()
                        if d.is_dir() and (d / "log.jsonl").exists() and d.name not in recorded) \
        if runs_dir.exists() else []
    if unrecorded:
        print("unrecorded runs: " + ", ".join(unrecorded))

    if len(valid) < 3:
        print("n < 3: correlation not computed")
        return 0
    xs = [float(r["gate_aggregate"]) for r in valid]
    ys = [float(r["rework_rate"]) for r in valid]
    pr, sr = pearson(xs, ys), spearman(xs, ys)
    if pr is None or sr is None:
        print("zero variance in a column: correlation not computed")
        return 0
    print(f"Pearson r = {pr:.4f}")
    print(f"Spearman rho = {sr:.4f}")
    return 0


# --------------------------------------------------------------- cli entry

def cmd_add(args) -> int:
    target_root = Path(args.run).resolve().parent.parent
    try:
        if getattr(args, "record", None):
            rec = json.loads(Path(args.record).read_text(encoding="utf-8"))
        else:
            rec = build_record(Path(args.run), Path(args.prd))
        ds = append_record(target_root, rec)
    except CalibError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"recorded {rec['run_id']} -> {ds} (rework_rate {rec['rework_rate']}, "
          f"gate_mode {rec['gate_mode']}, run_status {rec['run_status']})")
    return 0


def cmd_report(args) -> int:
    return report(Path(args.target).resolve())
