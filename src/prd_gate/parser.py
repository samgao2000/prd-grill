"""Parse a req-dev / req-dev-lite PRD markdown file into structured pieces.

Format contract (source of truth — real templates, not descriptions):
- skills/req-dev-lite/templates/prd-local.md   (lite PRD, frontmatter + US blocks + Open Items table)
- skills/req-dev/templates/user-story.md       (full-path story block fields)
- skills/req-dev/templates/prd-extension.md    (full-path PRD extension fields)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- frontmatter

_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML-ish key: value frontmatter parser (no nesting needed)."""
    m = _FM_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.split("#", 1)[0].strip()
    return out


# ---------------------------------------------------------------- stories

_US_HEADER_RE = re.compile(r"^#{2,4}\s*(US-[0-9A-Za-z]+)\s*[：:]\s*(.*)$", re.MULTILINE)
_GHERKIN_RE = re.compile(r"```gherkin\s*\n(.*?)```", re.DOTALL)
# inline form: **追溯**：Why=OKR-Q2-1, Who=主动用户, How=...
_TRACE_INLINE_RE = re.compile(
    r"\*?\*?(?:追溯|Traceability)\*?\*?(?:（Traceability）)?\s*[：:]\s*"
    r"Why\s*=\s*([^,，\n]+)[,，]\s*Who\s*=\s*([^,，\n]+)"
)
# list form (user-story.md): - 上游 Why：[...]  /  - 上游 Who：[...]
_TRACE_WHY_LIST_RE = re.compile(r"上游\s*Why\s*[：:]\s*(.+)")
_TRACE_WHO_LIST_RE = re.compile(r"上游\s*Who\s*[：:]\s*(.+)")
_EXT_ITEM_RE = re.compile(r"^\s*-\s*\d+[a-z]\.\s+\S", re.MULTILINE)

# placeholder forms that mean "template not filled in"
_PLACEHOLDER_RE = re.compile(
    r"<[^>]*>|\[[^\]]*\]|OKR-XX|XXX|YYYY-MM-DD|TBD\b|待定|待填|占位",
)


def is_placeholder(value: str) -> bool:
    v = value.strip()
    if not v or v in {"-", "—", "N/A", "n/a"}:
        return True
    return bool(_PLACEHOLDER_RE.search(v))


@dataclass
class Story:
    story_id: str
    title: str
    body: str
    gherkin_blocks: list[str] = field(default_factory=list)
    trace_why: str | None = None
    trace_who: str | None = None
    extension_count: int = 0

    @property
    def prose(self) -> str:
        """Story body with gherkin fences removed (for weasel/solution scans
        the AC examples often legitimately quote UI strings)."""
        return _GHERKIN_RE.sub("", self.body)


def parse_stories(text: str) -> list[Story]:
    headers = list(_US_HEADER_RE.finditer(text))
    stories: list[Story] = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else _next_section_end(text, start)
        body = text[start:end]
        st = Story(story_id=m.group(1), title=m.group(2).strip(), body=body)
        st.gherkin_blocks = [g.strip() for g in _GHERKIN_RE.findall(body)]
        ti = _TRACE_INLINE_RE.search(body)
        if ti:
            st.trace_why, st.trace_who = ti.group(1).strip(), ti.group(2).strip()
        else:
            w = _TRACE_WHY_LIST_RE.search(body)
            h = _TRACE_WHO_LIST_RE.search(body)
            st.trace_why = w.group(1).strip() if w else None
            st.trace_who = h.group(1).strip() if h else None
        st.extension_count = len(_EXT_ITEM_RE.findall(body))
        stories.append(st)
    return stories


def _next_section_end(text: str, start: int) -> int:
    """A trailing story runs until the next top-level '## N.' section header."""
    m = re.compile(r"^## \d+\.", re.MULTILINE).search(text, start)
    return m.start() if m else len(text)


# ---------------------------------------------------------------- open items

@dataclass
class OpenItem:
    raw_row: str
    owner: str
    deadline: str


_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def parse_open_items(text: str) -> list[OpenItem]:
    sec = _find_section(text, r"Open Items")
    if not sec:
        return []
    rows = [ln for ln in sec.splitlines() if ln.strip().startswith("|")]
    if len(rows) < 3:  # header + separator + >=1 data row
        return []
    header = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]

    def col_idx(*names: str) -> int | None:
        for i, h in enumerate(header):
            if any(n in h for n in names):
                return i
        return None

    oi_owner = col_idx("owner", "负责人")
    oi_dl = col_idx("截止", "deadline")
    items: list[OpenItem] = []
    for row in rows[2:]:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(set(c) <= {"-", " ", ":"} for c in cells):
            continue
        owner = cells[oi_owner] if oi_owner is not None and oi_owner < len(cells) else ""
        deadline = cells[oi_dl] if oi_dl is not None and oi_dl < len(cells) else ""
        items.append(OpenItem(raw_row=row.strip(), owner=owner, deadline=deadline))
    return items


def _find_section(text: str, title_pattern: str) -> str | None:
    m = re.compile(rf"^##[^\n]*{title_pattern}[^\n]*$", re.MULTILINE | re.IGNORECASE).search(text)
    if not m:
        return None
    nxt = re.compile(r"^## ", re.MULTILINE).search(text, m.end())
    return text[m.end(): nxt.start() if nxt else len(text)]


# ---------------------------------------------------------------- core anchor

@dataclass
class CoreAnchor:
    why: str | None
    who: str | None
    has_baseline: bool
    has_target: bool
    has_deadline: bool


_WHY_RE = re.compile(r"\*\*Why\*\*\s*[|：:]\s*(.+)")
_WHO_RE = re.compile(r"\*\*Who\*\*\s*[|：:]\s*(.+)")


def parse_core_anchor(text: str) -> CoreAnchor:
    why_m = _WHY_RE.search(text)
    who_m = _WHO_RE.search(text)
    # baseline/target/deadline may be sub-bullets or inline in the Why cell
    probe_start = why_m.start() if why_m else 0
    probe = text[probe_start: probe_start + 600]
    return CoreAnchor(
        why=why_m.group(1).strip() if why_m else None,
        who=who_m.group(1).strip() if who_m else None,
        has_baseline=("基线" in probe or "baseline" in probe.lower()),
        has_target=("目标" in probe or "target" in probe.lower()),
        has_deadline=bool(_DATE_RE.search(probe)) or "截止" in probe,
    )


# ---------------------------------------------------------------- top level

@dataclass
class ParsedPRD:
    path: str
    text: str
    frontmatter: dict[str, str]
    stories: list[Story]
    open_items: list[OpenItem]
    core_anchor: CoreAnchor


def parse_prd(path: str | Path) -> ParsedPRD:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return ParsedPRD(
        path=str(p),
        text=text,
        frontmatter=parse_frontmatter(text),
        stories=parse_stories(text),
        open_items=parse_open_items(text),
        core_anchor=parse_core_anchor(text),
    )
