"""LLM-as-judge layer for the dimensions that need domain judgment.

Independence rule: the judge sees ONLY (a) the PRD text and (b) the anchor
doc (quality-gateway.md). It must NOT see the elicitation conversation —
that is the whole point: the author-model grading its own homework is what
this gate replaces.

Three ways to obtain judge results:
1. mode=api   — anthropic SDK call (env ANTHROPIC_API_KEY); PRD_GATE_MOCK=1
                returns an all-pass stub (CI). Mirrors plan_eval.judge.
2. mode=tasks — emit judge-tasks.json; a *fresh-context* agent session
                answers them and writes judge-results.json; then `merge`.
                This is the path Cowork/Claude Code uses (no nested SDK
                calls from a Bash subprocess — CLAUDECODE=1 restriction).
3. merge      — combine deterministic results with judge-results.json.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .checks import DimensionResult, Finding
from .parser import ParsedPRD

# Dimensions owned by the judge. solution_free and gap also have a
# deterministic signal; merge() takes min(deterministic, judge) — 严判优先.
JUDGE_DIMENSIONS: tuple[str, ...] = (
    "contradiction", "gap", "fallacy", "redundancy",
    "dangling", "overreach", "solution_free",
)

_DIMENSION_QUESTIONS: dict[str, str] = {
    "contradiction": "Can you construct a scenario where two stories cannot both hold? Cite story pairs.",
    "gap": "Lay the stories on a timeline. Does any state jump to the next without the intermediate step/actor/duration defined? Is each story's Extensions list complete for its main-flow steps?",
    "fallacy": "Does the Problem Statement justify需求 with social proof, vague '有用户反馈', or unquantified claims? Cite lines.",
    "redundancy": "Do any two stories describe the same behavior in different words? Cite pairs to merge.",
    "dangling": "Does any story mention an entity/actor/data with no owner, trigger, or rule source?",
    "overreach": "Does any story exceed the PRD-level Why? Compare each story's 追溯 Why to the core Why.",
    "solution_free": "Does any story prescribe implementation (tech choice, storage, framework) instead of what/who/why?",
}


@dataclass
class JudgeTask:
    dimension: str
    question: str
    anchor: str
    scoring_rule: str


def build_judge_tasks(prd: ParsedPRD, anchor_path: str) -> list[dict]:
    tasks = [
        asdict(JudgeTask(
            dimension=dim,
            question=_DIMENSION_QUESTIONS[dim],
            anchor=anchor_path,
            scoring_rule=(
                "score = (stories with zero hits) / (total stories); "
                "PRD-level dimensions (contradiction/redundancy/fallacy): "
                "score = 1.0 if zero hits else 1 - hits/total_stories (floor 0). "
                "Every hit MUST cite the story id or line. No hit, no deduction."
            ),
        ))
        for dim in JUDGE_DIMENSIONS
    ]
    return tasks


def write_judge_tasks(prd: ParsedPRD, anchor_path: str, out: Path) -> Path:
    payload = {
        "prd": prd.path,
        "independence_rule": (
            "Judge in a FRESH context. Read ONLY the PRD file and the anchor doc. "
            "Do NOT use the elicitation conversation, even if available."
        ),
        "result_schema": {
            "<dimension>": {"score": "float 0..1", "failures": [{"unit": "US-xxx|PRD", "detail": "evidence"}]}
        },
        "tasks": build_judge_tasks(prd, anchor_path),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _extract_json_object(raw: str) -> dict:
    """Tolerant extraction: judges (human or LLM, any vendor) wrap JSON in code
    fences, prose, trailing NULs or whitespace. Find and decode the first JSON
    object; fail with a actionable message otherwise."""
    cleaned = raw.replace("\x00", "").strip()
    if cleaned.startswith("```"):
        first_nl = cleaned.find("\n")
        cleaned = cleaned[first_nl + 1:] if first_nl != -1 else cleaned
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3]
    start = cleaned.find("{")
    if start == -1:
        raise ValueError(
            "judge-results contains no JSON object. Expected a single JSON object "
            "mapping each dimension to {score, applicable, failures}.")
    obj, _ = json.JSONDecoder().raw_decode(cleaned[start:])
    if not isinstance(obj, dict):
        raise ValueError("judge-results top level must be a JSON object")
    return obj


def load_judge_results(path: Path) -> dict[str, DimensionResult]:
    raw = _extract_json_object(path.read_text(encoding="utf-8"))
    out: dict[str, DimensionResult] = {}
    for dim, r in raw.items():
        if dim not in JUDGE_DIMENSIONS:
            continue
        out[dim] = DimensionResult(
            dimension=dim,
            score=max(0.0, min(1.0, float(r["score"]))),
            judged_by="llm",
            applicable=int(r.get("applicable", 0)),
            failures=[Finding(f.get("unit", "?"), f.get("detail", "")) for f in r.get("failures", [])],
        )
    missing = set(JUDGE_DIMENSIONS) - set(out)
    if missing:
        raise ValueError(f"judge-results missing dimensions: {sorted(missing)}")
    return out


# Dimensions where the deterministic layer is only a *signal* and the judge
# has final authority (lexicon hits like "SQLite" may be legitimate context;
# whether a story prescribes implementation needs judgment).
JUDGE_AUTHORITATIVE: tuple[str, ...] = ("solution_free",)


def merge(deterministic: list[DimensionResult],
          judged: dict[str, DimensionResult]) -> list[DimensionResult]:
    """严判优先: where both layers scored a dimension, keep min(score) and
    the union of cited failures — except JUDGE_AUTHORITATIVE dimensions,
    where the judge's score replaces the deterministic signal (deterministic
    evidence is still carried so the judge's call is auditable)."""
    merged: dict[str, DimensionResult] = {d.dimension: d for d in deterministic}
    for dim, jr in judged.items():
        if dim in merged:
            det = merged[dim]
            score = jr.score if dim in JUDGE_AUTHORITATIVE else min(det.score, jr.score)
            judged_by = "merged-mock" if jr.judged_by == "mock" else "merged"
            merged[dim] = DimensionResult(
                dimension=dim, score=score, judged_by=judged_by,
                applicable=max(det.applicable, jr.applicable),
                failures=det.failures + jr.failures,
            )
        else:
            merged[dim] = jr
    return list(merged.values())


# ---------------------------------------------------------------- api mode

def judge_via_api(prd: ParsedPRD, anchor_text: str) -> dict[str, DimensionResult]:
    """plan_eval-style direct call. Stubbed all-pass under PRD_GATE_MOCK=1."""
    if os.environ.get("PRD_GATE_MOCK") == "1":
        # CI stub. judged_by="mock" propagates into the report so a mock
        # verdict can never masquerade as a real one (calib rejects it).
        return {
            dim: DimensionResult(dim, 1.0, "mock", len(prd.stories), [])
            for dim in JUDGE_DIMENSIONS
        }
    import anthropic  # deferred import; dependency already in pyproject

    client = anthropic.Anthropic()
    system = (
        "You are an independent requirements-quality judge. Judge ONLY from the PRD "
        "and the anchor rubric below. Output strict JSON matching the result schema. "
        "Every deduction must cite a story id or line. 严判优先: ambiguous = fail.\n\n"
        "ANCHOR RUBRIC:\n" + anchor_text
    )
    user = json.dumps({
        "tasks": build_judge_tasks(prd, "inline"),
        "result_schema": {"<dimension>": {"score": 0.0, "failures": [{"unit": "", "detail": ""}]}},
        "prd_markdown": prd.text,
    }, ensure_ascii=False)
    resp = client.messages.create(
        model=os.environ.get("PRD_GATE_MODEL", "claude-sonnet-4-6"),
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = resp.content[0].text
    start, end = text.find("{"), text.rfind("}") + 1
    raw = json.loads(text[start:end])
    return {
        dim: DimensionResult(
            dimension=dim,
            score=max(0.0, min(1.0, float(r["score"]))),
            judged_by="llm",
            applicable=len(prd.stories),
            failures=[Finding(f.get("unit", "?"), f.get("detail", "")) for f in r.get("failures", [])],
        )
        for dim, r in raw.items() if dim in JUDGE_DIMENSIONS
    }
