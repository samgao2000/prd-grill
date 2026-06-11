"""Stdlib-only fallback helpers for auto-dev-lite (used when the full
`auto_dev` package is not installed).

Semantics mirror auto_dev.modules.{tier_classifier, escalation, trailer}
in simplified form: keyword heuristics instead of the full rule engine.
Where the two disagree, the full package is authoritative.

No third-party imports. Python >= 3.10.
"""

from __future__ import annotations

import datetime as _dt
import random
import re
import string
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------- run id

def new_run_id() -> str:
    ts = _dt.datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{ts}-{suffix}"


# --------------------------------------------------------------- tier

_HIGH_RISK_PAT = re.compile(
    r"auth|login|password|session|payment|billing|invoice|migrat|drop\b|delete.*table|"
    r"secret|token|crypt|external.*api|webhook", re.IGNORECASE)
_LOW_RISK_SUFFIXES = (".md", ".rst", ".txt", ".cfg", ".ini", ".toml", ".json", ".yaml", ".yml")


def classify_tier(planned_paths: list[str], story_text: str = "",
                  all_comments_only: bool = False) -> str:
    """Return 'low' | 'medium' | 'high'. Conservative: ambiguity escalates."""
    if all_comments_only:
        return "low"
    if _HIGH_RISK_PAT.search(story_text) or any(_HIGH_RISK_PAT.search(p) for p in planned_paths):
        return "high"
    modules = {Path(p).parts[0] for p in planned_paths if Path(p).parts}
    if len(modules) >= 3:
        return "high"
    if all(p.endswith(_LOW_RISK_SUFFIXES) for p in planned_paths) and planned_paths:
        return "low"
    if len(planned_paths) <= 1:
        return "low"
    return "medium"


# --------------------------------------------------------------- escalation

@dataclass
class RunState:
    cost_spent_usd: float = 0.0
    cost_ceiling_usd: float = 50.0
    test_failure_count: int = 0          # retries within this run
    test_failure_ceiling: int = 3
    new_dependencies: tuple[str, ...] = ()
    security_findings: tuple[str, ...] = ()
    files_outside_planned_scope: tuple[str, ...] = ()
    scope_creep_threshold: int = 3
    arch_conflicts: tuple[str, ...] = ()
    requirement_confidence: float = 1.0  # from PRD frontmatter gate_confidence
    confidence_threshold: float = 0.7


@dataclass
class Decision:
    action: str                          # "continue" | "soft_escalate" | "hard_stop"
    reason: str = ""
    findings: tuple[str, ...] = ()


def decide(s: RunState) -> Decision:
    """Ordered checks; first hit wins. Mirrors auto_dev.modules.escalation."""
    if s.cost_spent_usd >= s.cost_ceiling_usd:
        return Decision("hard_stop", f"cost ceiling: {s.cost_spent_usd:.2f} >= {s.cost_ceiling_usd:.2f}")
    if s.security_findings:
        return Decision("hard_stop", "security findings in diff", tuple(s.security_findings))
    if s.test_failure_count >= s.test_failure_ceiling:
        return Decision("hard_stop", f"{s.test_failure_count} consecutive test failures")
    if s.new_dependencies:
        return Decision("soft_escalate", "new dependencies need human sign-off", tuple(s.new_dependencies))
    if s.arch_conflicts:
        return Decision("soft_escalate", "architecture conflicts", tuple(s.arch_conflicts))
    if len(s.files_outside_planned_scope) > s.scope_creep_threshold:
        return Decision("soft_escalate",
                        f"scope creep: {len(s.files_outside_planned_scope)} files outside plan",
                        tuple(s.files_outside_planned_scope))
    if s.requirement_confidence < s.confidence_threshold:
        return Decision("soft_escalate",
                        f"low requirement confidence ({s.requirement_confidence:.2f} < "
                        f"{s.confidence_threshold:.2f}) — spec quality gate flagged this PRD")
    return Decision("continue")


# --------------------------------------------------------------- trailer

def build_trailer(*, run_id: str, issue_id: str, tier: str, cost_usd: float,
                  files_touched: list[str], lines_added: int, lines_removed: int,
                  review: str = "single-llm-self-only",
                  version: str = "lite-1") -> str:
    files = ", ".join(files_touched)
    return (
        "Auto-Dev-Lite-Trailer\n---\n"
        f"run_id: {run_id}\nissue_id: {issue_id}\ntier: {tier}\n"
        f"review: {review}\ncost_usd: {cost_usd:.2f}\n"
        f"files_touched: {files}\nlines: +{lines_added} -{lines_removed}\n"
        f"trailer_version: {version}\n"
    )


# --------------------------------------------------------------- ledger (no-git mode)

def append_ledger(target_root: Path, *, issue_id: str, title: str, run_id: str,
                  tier: str, cost_usd: float, files_touched: list[tuple[str, int, int]],
                  review: str = "single-llm-self-only") -> str:
    """Append an entry to runs/ledger.md; returns the ledger id 'L-NNN'.
    Never rewrites existing entries."""
    ledger = target_root / "runs" / "ledger.md"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    text = ledger.read_text(encoding="utf-8") if ledger.exists() else "# Auto-Dev-Lite Ledger\n"
    last = max((int(m.group(1)) for m in re.finditer(r"^## L-(\d+)", text, re.MULTILINE)), default=0)
    lid = f"L-{last + 1:03d}"
    files_md = "\n".join(f"  - {p} (+{a}/-{r})" for p, a, r in files_touched)
    entry = (
        f"\n## {lid} — {issue_id}: {title}\n\n"
        f"- completed: {_dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"- run_id: {run_id}\n- tier: {tier}\n- review: {review}\n"
        f"- cost_usd: {cost_usd:.2f}\n- files_touched:\n{files_md}\n"
        f"- trailer_version: lite-1-ledger\n"
    )
    ledger.write_text(text + entry, encoding="utf-8")
    return lid


# --------------------------------------------------------------- kill switch

def kill_requested(target_root: Path, run_id: str) -> bool:
    return (target_root / "runs" / f"{run_id}.kill").exists()
