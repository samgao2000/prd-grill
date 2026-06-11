"""Serialize a GateResult to (a) machine-readable JSON, (b) human markdown,
(c) a frontmatter patch block to paste into the PRD."""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from .scoring import GateResult


def to_json_dict(prd_path: str, result: GateResult, mode: str) -> dict:
    return {
        "schema": "prd-gate/v1",
        "prd": prd_path,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": mode,
        "judge_pending": result.judge_pending,
        "verdict": result.verdict,
        "aggregate": result.aggregate,
        "requirement_confidence": result.requirement_confidence,
        "total_stories": result.total_stories,
        "failed_stories": result.failed_stories,
        "allowed_failures": result.allowed_failures,
        "core_veto": {"vetoed": result.core_veto.vetoed, "reasons": result.core_veto.reasons},
        "dimensions": {
            d.dimension: {
                "score": d.score,
                "judged_by": d.judged_by,
                "applicable": d.applicable,
                "failures": [{"unit": f.unit, "detail": f.detail} for f in d.failures],
            }
            for d in sorted(result.dimensions, key=lambda x: x.dimension)
        },
    }


def write_json(prd_path: str, result: GateResult, mode: str, out: Path) -> Path:
    out.write_text(json.dumps(to_json_dict(prd_path, result, mode),
                              ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def to_markdown(prd_path: str, result: GateResult, mode: str) -> str:
    lines = [
        f"# PRD Gate Report — {Path(prd_path).name}",
        "",
        f"- **Verdict**: {result.verdict}" + (" *(judge dimensions pending — deterministic floor only)*" if result.judge_pending else ""),
        f"- **Aggregate score**: {result.aggregate:.2f}",
        f"- **requirement_confidence**: {result.requirement_confidence:.2f} (escalation threshold 0.7)",
        f"- **Stories**: {result.total_stories} total, {len(result.failed_stories)} failed "
        f"(allowed: {result.allowed_failures})" +
        (f" — {', '.join(result.failed_stories)}" if result.failed_stories else ""),
        f"- **Mode**: {mode}",
        "",
    ]
    if result.total_stories == 0:
        lines += [
            "## ⚠ Parsing note",
            "",
            "No user stories were found. This usually means the PRD does not follow",
            "the parsing contract (numbered `## 3. User Stories` section with",
            "`### US-NNN:` headings). A non-conforming PRD fails by design; see",
            "`skills/req-dev-lite/templates/prd-local.en.md` (or `prd-local.md` 中文)",
            "for the expected structure.",
            "",
        ]
    if result.core_veto.vetoed:
        lines += ["## ⛔ Core Why/Who veto (一票否决)", ""]
        lines += [f"- {r}" for r in result.core_veto.reasons]
        lines += [""]
    lines += ["## Dimensions", "", "| Dimension | Score | Judged by | Failures |", "|---|---|---|---|"]
    for d in sorted(result.dimensions, key=lambda x: x.dimension):
        lines.append(f"| {d.dimension} | {d.score:.2f} | {d.judged_by} | {len(d.failures)} |")
    fails = [(d.dimension, f) for d in result.dimensions for f in d.failures]
    if fails:
        lines += ["", "## Evidence", ""]
        for dim, f in fails:
            lines.append(f"- `[{dim}]` **{f.unit}** — {f.detail}")
    lines += [
        "",
        "## Frontmatter patch (paste into PRD)",
        "",
        "```yaml",
        f"final_gate_verdict: {result.verdict}",
        f"gate_aggregate: {result.aggregate}",
        f"gate_confidence: {result.requirement_confidence}",
        f"gate_report: {Path(prd_path).stem}.gate.json",
        "```",
        "",
    ]
    return "\n".join(lines)


def write_markdown(prd_path: str, result: GateResult, mode: str, out: Path) -> Path:
    out.write_text(to_markdown(prd_path, result, mode), encoding="utf-8")
    return out
