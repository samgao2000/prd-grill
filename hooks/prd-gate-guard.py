#!/usr/bin/env python3
"""prd-gate-guard — a Claude Code hook that refuses to start planning or
building from a PRD that never passed the independent gate.

Fires on two events (see hooks.json):
  UserPromptSubmit  — the user typed /plan, /ecc:plan, /tdd, /multi-plan ...
  PreToolUse:Skill  — the model invoked a planning/build skill
                      (plan, tdd-workflow, product-capability, auto-dev-lite ...)

Decision (stdlib only, no prd_gate import needed):
  * PRD_GATE_GUARD=off                       -> exit 0, silent
  * no docs/prd/ directory in the project    -> advisory on stderr, exit 0
        (PRD_GATE_GUARD=strict turns this into a block)
  * docs/prd/ exists:
        newest PRD has final_gate_verdict in {PASS, PASS-WITH-OPEN-ITEMS}
        and gate_mode == prd-gate            -> exit 0, one-line OK on stderr
        anything else                        -> exit 2 (block) with the reason
  * PRD_GATE_GUARD_PRD=<path> overrides "newest PRD".

Exit 2 is Claude Code's blocking code: the stderr text is shown to the model
(PreToolUse) or to the user (UserPromptSubmit). Exit 0 never blocks.

This is enforcement by mechanism for the one thing the gate's README admits
is otherwise enforced by discipline: that nobody builds from an ungated spec.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PASS_VERDICTS = {"PASS", "PASS-WITH-OPEN-ITEMS"}

PROMPT_TRIGGERS = re.compile(
    r"^\s*/(?:ecc:)?(?:plan|tdd|multi-plan|multi-execute|auto-dev-lite|build)\b",
    re.IGNORECASE,
)
SKILL_TRIGGERS = {
    "plan", "ecc:plan", "tdd-workflow", "ecc:tdd-workflow",
    "product-capability", "ecc:product-capability",
    "auto-dev-lite", "prd-grill:auto-dev-lite",
    "multi-plan", "multi-execute",
}
# Skills that are part of the gate itself must never be blocked by the gate.
SKILL_ALLOWLIST = {"req-dev-lite", "prd-gate", "prd-grill:req-dev-lite", "prd-grill:prd-gate"}


def read_event() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def _should_check(ev: dict) -> bool:
    name = ev.get("hook_event_name", "")
    if name == "UserPromptSubmit":
        return bool(PROMPT_TRIGGERS.match(ev.get("prompt", "") or ""))
    if name == "PreToolUse" and ev.get("tool_name") == "Skill":
        skill = str((ev.get("tool_input") or {}).get("skill", "")).strip().lower()
        if skill in SKILL_ALLOWLIST:
            return False
        return skill in SKILL_TRIGGERS
    return False


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML-ish frontmatter reader: top-level `key: value` lines only.
    The PRD template is flat at the top level, so this is sufficient and avoids
    a PyYAML dependency inside a hook."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out: dict = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*(?:#.*)?$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def pick_prd(prd_dir: Path) -> Path | None:
    override = os.environ.get("PRD_GATE_GUARD_PRD")
    if override:
        p = Path(override)
        return p if p.is_file() else None
    cands = [p for p in prd_dir.glob("*.md")
             if not p.name.endswith((".gate.md", "-snapshot.md"))
             and ".judge" not in p.name]
    if not cands:
        return None
    # filenames start with YYYY-MM-DD; fall back to mtime on ties
    cands.sort(key=lambda p: (p.name[:10], p.stat().st_mtime))
    return cands[-1]


def main() -> int:
    mode = os.environ.get("PRD_GATE_GUARD", "").lower()
    if mode == "off":
        return 0
    ev = read_event()
    if not _should_check(ev):
        return 0

    root = Path(ev.get("cwd") or os.getcwd())
    prd_dir = root / "docs" / "prd"
    if not prd_dir.is_dir():
        msg = ("[prd-gate-guard] no docs/prd/ in this project — planning without a "
               "gated PRD. Run req-dev-lite then prd-gate first, or set "
               "PRD_GATE_GUARD=off to silence.")
        print(msg, file=sys.stderr)
        return 2 if mode == "strict" else 0

    prd = pick_prd(prd_dir)
    if prd is None:
        print("[prd-gate-guard] docs/prd/ exists but holds no PRD. Run req-dev-lite.",
              file=sys.stderr)
        return 2

    fm = parse_frontmatter(prd.read_text(encoding="utf-8", errors="replace"))
    verdict = fm.get("final_gate_verdict", "not_reached")
    gate_mode = fm.get("gate_mode", "self-reported")
    conf = fm.get("gate_confidence", "")

    if verdict in PASS_VERDICTS and gate_mode == "prd-gate":
        print(f"[prd-gate-guard] OK {prd.name}: {verdict} (gate_confidence={conf or '?'})",
              file=sys.stderr)
        return 0

    if verdict in PASS_VERDICTS:  # passed, but only self-graded
        print(f"[prd-gate-guard] BLOCKED {prd.name}: verdict {verdict} is "
              f"gate_mode={gate_mode}. The author model graded its own PRD. Run "
              f"`prd-gate score --prd {prd}` + the prd-judge agent + `prd-gate merge`, "
              f"then retry.", file=sys.stderr)
        return 2

    print(f"[prd-gate-guard] BLOCKED {prd.name}: final_gate_verdict={verdict}. "
          f"A FAIL or unscored PRD must not enter planning or implementation. "
          f"Rework per {prd.with_suffix('')}.gate.md, re-gate, then retry.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
