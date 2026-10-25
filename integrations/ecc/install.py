#!/usr/bin/env python3
"""Install the prd-grill ECC integration WITHOUT the Claude Code plugin path.

Use this when ECC was installed manually (./install.sh) or you want the pieces
under a project's .claude/ instead of the user's ~/.claude/.
If you installed prd-grill via `/plugin install prd-grill@prd-grill`, you do
not need this script: the plugin already ships the agent and the hook.

What it does (idempotent, stdlib only, never deletes anything):
  1. copies agents/prd-judge.md           -> <root>/agents/prd-judge.md
  2. copies hooks/prd-gate-guard.py       -> <root>/hooks/prd-gate-guard.py
  3. copies skills/{req-dev-lite,prd-gate,auto-dev-lite} -> <root>/skills/
  4. merges two hook entries into <root>/settings.json (UserPromptSubmit,
     PreToolUse:Skill) pointing at the copied guard script
  5. prints the ECC install hint; it does NOT install or modify ECC

<root> is ~/.claude (default) or ./.claude with --project.

Usage:
  python integrations/ecc/install.py            # user scope
  python integrations/ecc/install.py --project  # project scope (run in the project)
  python integrations/ecc/install.py --dry-run
  python integrations/ecc/install.py --uninstall
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = ("req-dev-lite", "prd-gate", "auto-dev-lite")
MARK = "prd-gate-guard.py"  # substring that identifies our hook entries


def guard_command(root: Path) -> str:
    script = (root / "hooks" / "prd-gate-guard.py").as_posix()
    return f'"$(command -v python3 || command -v python)" "{script}"'


def copy(src: Path, dst: Path, dry: bool, log: list[str]) -> None:
    log.append(f"copy  {src.relative_to(REPO)} -> {dst}")
    if dry:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError as e:
        sys.exit(f"refusing to touch malformed {path}: {e}")


def strip_ours(hooks: dict) -> dict:
    out = {}
    for event, groups in hooks.items():
        kept = []
        for g in groups:
            inner = [h for h in g.get("hooks", []) if MARK not in h.get("command", "")]
            if inner:
                kept.append({**g, "hooks": inner})
        if kept:
            out[event] = kept
    return out


def merge_hooks(settings: dict, root: Path) -> dict:
    hooks = strip_ours(settings.get("hooks", {}))
    cmd = {"type": "command", "command": guard_command(root), "timeout": 10}
    hooks.setdefault("UserPromptSubmit", []).append({"hooks": [cmd]})
    hooks.setdefault("PreToolUse", []).append({"matcher": "Skill", "hooks": [cmd]})
    return {**settings, "hooks": hooks}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", action="store_true", help="install into ./.claude instead of ~/.claude")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true", help="remove our hook entries from settings.json (files are left in place)")
    a = ap.parse_args()

    root = Path.cwd() / ".claude" if a.project else Path.home() / ".claude"
    settings_path = root / "settings.json"
    log: list[str] = []

    settings = load_settings(settings_path)
    if a.uninstall:
        new = {**settings, "hooks": strip_ours(settings.get("hooks", {}))}
        if not new["hooks"]:
            new.pop("hooks")
        log.append(f"write {settings_path} (hook entries removed)")
        if not a.dry_run:
            settings_path.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("\n".join(log)); return 0

    copy(REPO / "agents" / "prd-judge.md", root / "agents" / "prd-judge.md", a.dry_run, log)
    copy(REPO / "hooks" / "prd-gate-guard.py", root / "hooks" / "prd-gate-guard.py", a.dry_run, log)
    for s in SKILLS:
        copy(REPO / "skills" / s, root / "skills" / s, a.dry_run, log)

    new = merge_hooks(settings, root)
    log.append(f"write {settings_path} (2 hook entries, idempotent)")
    if not a.dry_run:
        root.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\n".join(log))
    print(
        "\nDone. ECC itself is not touched by this script. If ECC is not installed yet:\n"
        "  npx ecc-universal@latest setup        (Claude Code)\n"
        "Then in a project with docs/prd/: '/ecc:plan ...' is blocked until the newest PRD\n"
        "carries final_gate_verdict PASS* with gate_mode: prd-gate. Set PRD_GATE_GUARD=off to disable."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
