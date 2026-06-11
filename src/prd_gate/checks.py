"""Deterministic (non-LLM) checks. Single anchor: skills/req-dev/references/quality-gateway.md.

Each check returns a DimensionResult with score in [0,1] = fraction of
applicable units passing, plus cited evidence for every failure.
严判优先 (ADR-002 spirit): when in doubt, a unit fails here and the LLM
judge may NOT raise a deterministic failure back to pass — merge takes min().
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .parser import ParsedPRD, Story, is_placeholder

# Lexicon lifted verbatim from references/quality-gateway.md (Volere Q4).
WEASEL_WORDS: tuple[str, ...] = (
    "user-friendly", "用户友好", "友好提示",
    "快速", "速度快", "迅速",
    "合适", "恰当", "合理",
    "灵活", "健壮", "可扩展",
    "直观", "高性能", "高可用", "易用",
    "robust", "scalable", "intuitive", "flexible",
)
# English words needing word boundaries to avoid false hits inside other words.
_WEASEL_EN_BOUNDED: tuple[str, ...] = ("fast", "quick", "simple", "appropriate", "reasonable")

# Signal lexicon for solution language (Volere Q3). Deterministic *signal*,
# final call belongs to the LLM judge; in no-judge mode signal = verdict.
SOLUTION_TERMS: tuple[str, ...] = (
    "redis", "react", "vue", "angular", "mongodb", "postgres", "mysql", "sqlite",
    "kafka", "rabbitmq", "docker", "kubernetes", "k8s", "elasticsearch",
    "微服务", "缓存", "数据库表", "消息队列", "索引", "中间件",
)

_REAL_VALUE_RE = re.compile(r"[0-9０-９]|[¥$€％%]|「[^」]+」")


@dataclass
class Finding:
    unit: str          # e.g. "US-001" or "OI row 2" or "PRD"
    detail: str


@dataclass
class DimensionResult:
    dimension: str
    score: float                      # 0..1
    judged_by: str                    # "deterministic" | "llm" | "merged"
    applicable: int
    failures: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.score >= 1.0


def _ratio(n_pass: int, n_total: int) -> float:
    return 1.0 if n_total == 0 else round(n_pass / n_total, 4)


# ------------------------------------------------------------- Volere Q1

def check_testable(prd: ParsedPRD) -> DimensionResult:
    """Story has >=1 Gherkin block with Given/When/Then AND a real value."""
    fails: list[Finding] = []
    for st in prd.stories:
        ok = False
        for g in st.gherkin_blocks:
            has_gwt = all(k in g for k in ("Given", "When", "Then"))
            if has_gwt and _REAL_VALUE_RE.search(g):
                ok = True
                break
        if not ok:
            why = "no Gherkin block" if not st.gherkin_blocks else \
                  "Gherkin lacks Given/When/Then or contains no real value (digit/¥/quoted literal)"
            fails.append(Finding(st.story_id, why))
    return DimensionResult("testable", _ratio(len(prd.stories) - len(fails), len(prd.stories)),
                           "deterministic", len(prd.stories), fails)


# ------------------------------------------------------------- Volere Q2

def check_traceable(prd: ParsedPRD) -> DimensionResult:
    fails: list[Finding] = []
    for st in prd.stories:
        if st.trace_why is None or st.trace_who is None:
            fails.append(Finding(st.story_id, "missing 追溯 Why=/Who= line"))
        elif is_placeholder(st.trace_why) or is_placeholder(st.trace_who):
            fails.append(Finding(st.story_id,
                                 f"placeholder traceability: Why={st.trace_why!r} Who={st.trace_who!r}"))
    return DimensionResult("traceable", _ratio(len(prd.stories) - len(fails), len(prd.stories)),
                           "deterministic", len(prd.stories), fails)


# ------------------------------------------------------------- Volere Q3 (signal)

def check_solution_language(prd: ParsedPRD) -> DimensionResult:
    fails: list[Finding] = []
    for st in prd.stories:
        text = st.prose.lower()
        hits = sorted({t for t in SOLUTION_TERMS if t in text})
        if hits:
            fails.append(Finding(st.story_id, f"solution terms in story prose: {', '.join(hits)}"))
    return DimensionResult("solution_free", _ratio(len(prd.stories) - len(fails), len(prd.stories)),
                           "deterministic", len(prd.stories), fails)


# ------------------------------------------------------------- Volere Q4

def check_weasel_words(prd: ParsedPRD) -> DimensionResult:
    fails: list[Finding] = []
    for st in prd.stories:
        text = st.prose
        low = text.lower()
        hits = sorted({w for w in WEASEL_WORDS if w in low})
        # "fail-fast" / "fail fast" is concrete, testable behavior, not a
        # weasel word (found via dogfooding on the CRM PRD, 2026-06-10).
        hits += sorted({w for w in _WEASEL_EN_BOUNDED
                        if re.search(rf"(?<!fail[- ])\b{w}\b", low)})
        if hits:
            fails.append(Finding(st.story_id, f"weasel words: {', '.join(hits)}"))
    return DimensionResult("no_weasel", _ratio(len(prd.stories) - len(fails), len(prd.stories)),
                           "deterministic", len(prd.stories), fails)


# ------------------------------------------------------------- [Gap] proxy

def check_extensions_present(prd: ParsedPRD) -> DimensionResult:
    """Deterministic floor for [Gap]: every story enumerates >=1 unhappy path
    (Cockburn Extensions). Whether the enumeration is *complete* is the
    LLM judge's question."""
    fails: list[Finding] = []
    for st in prd.stories:
        if st.extension_count == 0:
            fails.append(Finding(st.story_id, "no Cockburn Extensions (unhappy paths) enumerated"))
    return DimensionResult("gap", _ratio(len(prd.stories) - len(fails), len(prd.stories)),
                           "deterministic", len(prd.stories), fails)


# ------------------------------------------------------------- [Unowned]

def check_unowned(prd: ParsedPRD) -> DimensionResult:
    """prd-local.md rule: owner=TBD must carry a deadline; deadline=TBD must
    carry an owner; both TBD (or empty) = fail."""
    fails: list[Finding] = []
    date_re = re.compile(r"20\d{2}-\d{2}-\d{2}")
    for i, oi in enumerate(prd.open_items, 1):
        owner_ok = bool(oi.owner) and not (is_placeholder(oi.owner) and not date_re.search(oi.owner))
        deadline_ok = bool(date_re.search(oi.deadline))
        if not (owner_ok or deadline_ok) or (not oi.owner.strip() and not oi.deadline.strip()):
            fails.append(Finding(f"OI row {i}", f"owner={oi.owner!r} deadline={oi.deadline!r}"))
        elif not owner_ok:
            fails.append(Finding(f"OI row {i}", f"no usable owner: {oi.owner!r}"))
        elif not deadline_ok:
            fails.append(Finding(f"OI row {i}", f"no concrete deadline: {oi.deadline!r}"))
    return DimensionResult("unowned", _ratio(len(prd.open_items) - len(fails), len(prd.open_items)),
                           "deterministic", len(prd.open_items), fails)


# ------------------------------------------------------------- core veto

@dataclass
class CoreVeto:
    vetoed: bool
    reasons: list[str]


def check_core_anchor(prd: ParsedPRD) -> CoreVeto:
    """阶段 5 hard rule: Why/Who 一票否决 — regardless of story pass ratio."""
    a = prd.core_anchor
    reasons: list[str] = []
    if a.why is None or is_placeholder(a.why):
        reasons.append(f"core Why missing or placeholder: {a.why!r}")
    else:
        if not a.has_baseline:
            reasons.append("core Why lacks 基线 (baseline)")
        if not a.has_target:
            reasons.append("core Why lacks 目标 (target)")
        if not a.has_deadline:
            reasons.append("core Why lacks 截止 (deadline)")
    if a.who is None or is_placeholder(a.who):
        reasons.append(f"core Who missing or placeholder: {a.who!r}")
    return CoreVeto(vetoed=bool(reasons), reasons=reasons)


DETERMINISTIC_CHECKS = (
    check_testable,
    check_traceable,
    check_solution_language,
    check_weasel_words,
    check_extensions_present,
    check_unowned,
)


def run_deterministic(prd: ParsedPRD) -> list[DimensionResult]:
    return [fn(prd) for fn in DETERMINISTIC_CHECKS]
