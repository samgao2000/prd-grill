"""prd-gate CLI.

Usage:
  python -m prd_gate score --prd docs/prd/x.md [--judge none|api] [--anchor path]
  python -m prd_gate merge --prd docs/prd/x.md --judge-results x.judge-results.json

`score --judge none` (default) runs the deterministic floor and emits
<prd>.judge-tasks.json for a fresh-context agent to answer; verdict is
marked judge_pending. `merge` combines both layers into the final report.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import calib as _calib
from . import checks, judge, report, scoring
from .parser import parse_prd

DEFAULT_ANCHOR = "skills/req-dev-lite/references/quality-gateway.md"


def resolve_anchor(arg: str) -> Path:
    """Use the user's anchor when it exists; otherwise fall back to the copy
    packaged inside prd_gate (so pip-installed users outside the repo never
    reference a non-existent rubric path)."""
    cand = Path(arg)
    if cand.exists():
        return cand.resolve()
    packaged = Path(__file__).parent / "data" / "quality-gateway.md"
    print(f"note: anchor {arg!r} not found; using the packaged rubric {packaged}",
          file=sys.stderr)
    return packaged


def _utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _outputs(prd_path: Path) -> tuple[Path, Path, Path]:
    base = prd_path.with_suffix("")
    return (Path(f"{base}.gate.json"), Path(f"{base}.gate.md"),
            Path(f"{base}.judge-tasks.json"))


def cmd_score(args: argparse.Namespace) -> int:
    prd_path = Path(args.prd)
    prd = parse_prd(prd_path)
    det = checks.run_deterministic(prd)
    veto = checks.check_core_anchor(prd)
    json_out, md_out, tasks_out = _outputs(prd_path)

    anchor = resolve_anchor(args.anchor)
    if args.judge == "api":
        anchor_text = anchor.read_text(encoding="utf-8")
        judged = judge.judge_via_api(prd, anchor_text)
        dims = judge.merge(det, judged)
        result = scoring.decide(dims, veto, len(prd.stories), judge_pending=False)
        mode = ("deterministic+mock-judge"
                if any(d.judged_by in ("mock", "merged-mock") for d in dims)
                else "deterministic+api-judge")
    else:
        result = scoring.decide(det, veto, len(prd.stories), judge_pending=True)
        judge.write_judge_tasks(prd, str(anchor), tasks_out)
        mode = "deterministic-only"

    report.write_json(str(prd_path), result, mode, json_out)
    report.write_markdown(str(prd_path), result, mode, md_out)
    print(report.to_markdown(str(prd_path), result, mode))
    if result.judge_pending:
        print(f"[prd-gate] judge tasks written to {tasks_out} — answer them in a "
              f"FRESH context, save as {prd_path.with_suffix('')}.judge-results.json, "
              f"then run `merge`.", file=sys.stderr)
    return 0 if result.verdict != scoring.VERDICT_FAIL else 2


def cmd_merge(args: argparse.Namespace) -> int:
    prd_path = Path(args.prd)
    prd = parse_prd(prd_path)
    det = checks.run_deterministic(prd)
    veto = checks.check_core_anchor(prd)
    judged = judge.load_judge_results(Path(args.judge_results))
    dims = judge.merge(det, judged)
    result = scoring.decide(dims, veto, len(prd.stories), judge_pending=False)
    json_out, md_out, _ = _outputs(prd_path)
    mode = "deterministic+fresh-context-judge"
    report.write_json(str(prd_path), result, mode, json_out)
    report.write_markdown(str(prd_path), result, mode, md_out)
    print(report.to_markdown(str(prd_path), result, mode))
    return 0 if result.verdict != scoring.VERDICT_FAIL else 2


def main(argv: list[str] | None = None) -> int:
    _utf8_console()
    p = argparse.ArgumentParser(prog="prd-gate", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    ps = sub.add_parser("score", help="run deterministic checks (+ optional api judge)")
    ps.add_argument("--prd", required=True)
    ps.add_argument("--judge", choices=["none", "api"], default="none")
    ps.add_argument("--anchor", default=DEFAULT_ANCHOR)
    ps.set_defaults(func=cmd_score)

    pm = sub.add_parser("merge", help="merge fresh-context judge results into final report")
    pm.add_argument("--prd", required=True)
    pm.add_argument("--judge-results", required=True)
    pm.set_defaults(func=cmd_merge)

    pc = sub.add_parser("calib", help="calibration run logger (score vs rework pairing)")
    csub = pc.add_subparsers(dest="calib_command", required=True)
    ca = csub.add_parser("add", help="validate + append one run's paired record")
    ca.add_argument("--run", required=True, help="run directory containing log.jsonl")
    ca.add_argument("--prd", help="source PRD (frontmatter supplies gate fields)")
    ca.add_argument("--record", help="pre-built record JSON file (validated, not derived)")
    ca.set_defaults(func=_calib_add)
    cr = csub.add_parser("report", help="paired table + correlation + exclusions")
    cr.add_argument("--target", default=".", help="target project root (default: cwd)")
    cr.set_defaults(func=_calib_report)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())


def _calib_add(args):
    return _calib.cmd_add(args)


def _calib_report(args):
    return _calib.cmd_report(args)
