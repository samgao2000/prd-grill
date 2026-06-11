from prd_gate.parser import parse_prd


def test_parses_frontmatter_stories_open_items(good_prd_file):
    prd = parse_prd(good_prd_file)
    assert prd.frontmatter["slug"] == "csm-dashboard"
    assert prd.frontmatter["final_gate_verdict"] == "not_reached"
    assert [s.story_id for s in prd.stories] == ["US-001", "US-002"]
    s1 = prd.stories[0]
    assert s1.trace_why == "OKR-Q2-1"
    assert s1.trace_who == "CSM"
    assert len(s1.gherkin_blocks) == 1
    assert s1.extension_count == 2
    assert len(prd.open_items) == 1
    assert prd.open_items[0].owner == "@lina"
    assert prd.open_items[0].deadline == "2026-06-15"


def test_core_anchor_good(good_prd_file):
    a = parse_prd(good_prd_file).core_anchor
    assert a.why and "OKR" in a.why
    assert a.has_baseline and a.has_target and a.has_deadline


def test_core_anchor_placeholder(bad_prd_file):
    a = parse_prd(bad_prd_file).core_anchor
    assert a.why.startswith("<")


def test_story_prose_excludes_gherkin(bad_prd_file):
    prd = parse_prd(bad_prd_file)
    s2 = prd.stories[1]
    assert "Scenario" not in s2.prose
    assert "合理处理" in s2.prose


def test_english_traceability_line(tmp_path):
    text = """\
## 3. User Stories (Bucket A)

### US-001: View account balance

**As** a mobile banking user, **I want** to see balances on the home screen, **so that** I can judge my spending.

**Traceability**: Why=OKR-Q2-1, Who=Active retail user, How=open account list -> glance home

```gherkin
Given user has 3 accounts totalling $1,240.50
When the home screen loads
Then 3 rows show name + balance to the cent
```

**Extensions (unhappy paths)**:
- 1a. balance fetch times out after 3s -> show retry link
"""
    p = tmp_path / "en.md"
    p.write_text(text, encoding="utf-8")
    prd = parse_prd(p)
    assert prd.stories[0].trace_why == "OKR-Q2-1"
    assert prd.stories[0].trace_who == "Active retail user"
    assert prd.stories[0].extension_count == 1
