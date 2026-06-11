from prd_gate import checks
from prd_gate.parser import parse_prd


def _by_dim(results):
    return {r.dimension: r for r in results}


def test_good_prd_passes_deterministic_floor(good_prd_file):
    prd = parse_prd(good_prd_file)
    dims = _by_dim(checks.run_deterministic(prd))
    for name in ("testable", "traceable", "solution_free", "no_weasel", "gap", "unowned"):
        assert dims[name].score == 1.0, (name, dims[name].failures)
    assert not checks.check_core_anchor(prd).vetoed


def test_bad_prd_fails_where_expected(bad_prd_file):
    prd = parse_prd(bad_prd_file)
    dims = _by_dim(checks.run_deterministic(prd))
    # US-001: no gherkin at all; US-002: gherkin without real values
    assert dims["testable"].score == 0.0
    failed_units = {f.unit for f in dims["testable"].failures}
    assert failed_units == {"US-001", "US-002"}
    # US-001 missing 追溯 entirely; US-002 placeholder Why/Who
    assert dims["traceable"].score == 0.0
    # weasel: 快速/友好/高性能 in US-001, 合理 in US-002
    assert dims["no_weasel"].score == 0.0
    # Redis in US-001 prose
    assert dims["solution_free"].score == 0.5
    assert dims["solution_free"].failures[0].unit == "US-001"
    # no Extensions anywhere
    assert dims["gap"].score == 0.0
    # OI row both TBD
    assert dims["unowned"].score == 0.0


def test_bad_prd_core_veto(bad_prd_file):
    veto = checks.check_core_anchor(parse_prd(bad_prd_file))
    assert veto.vetoed
    assert any("Why" in r for r in veto.reasons)


def test_fail_fast_is_not_a_weasel_word(tmp_path):
    from prd_gate.parser import parse_prd
    prd_text = """\
## 3. User Stories

### US-001：启动校验

**作为** 运维，**我希望** SECRET_KEY 未配置时应用 fail-fast 退出，**以便** 不带病运行。

**追溯**：Why=OKR-1, Who=运维

```gherkin
Given SECRET_KEY 未配置
When 启动应用
Then 进程退出码为 1
```

**Extensions**：
- 1a. 配置为空串 → 同样退出码 1
"""
    p = tmp_path / "p.md"
    p.write_text(prd_text, encoding="utf-8")
    prd = parse_prd(p)
    dims = _by_dim(checks.run_deterministic(prd))
    assert dims["no_weasel"].score == 1.0, dims["no_weasel"].failures
