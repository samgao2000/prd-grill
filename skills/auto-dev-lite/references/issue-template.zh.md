# 本地 issue 文件模板

每个 issue 一个文件：`<target_project>/local-issues/00N-{slug}.md`。
编号 `00N` 决定 step 1 的执行顺序（编号最小的 ready issue 先跑）。

```markdown
---
id: US-001                 # 与 PRD 的 US-NNN 一致（step 0.5 import 时逐字保留）
title: <issue 简短标题>
status: ready              # ready | in_progress | done | blocked | needs-review
tier: medium               # low | medium | high（Claude 初评，step 3 重评可改）
depends_on: []             # [US-NNN, ...]，全部 done 才会被选中
acceptance_tests: null     # 写完测试后填，如 tests/test_us001_login.py
run_id: null               # 开跑时填
---

# US-001: <issue 标题>

[完整 user story body。step 0.5 import 时从 PRD 逐字拷贝 7 字段：
**作为/我希望/以便** → **追溯** → **INVEST** → **Gherkin AC** →
**Extensions（不开心路径）** → **Volere QG** → **三桶归属**]
```

## Status 语义（state machine）

| 转移 | 触发 |
|---|---|
| `ready` → `in_progress` | step 2 开跑 |
| `in_progress` → `done` | pytest 通过 + commit/ledger 完成 |
| `in_progress` → `blocked` | acceptance test 失败 hard-stop / pipeline 无法继续；body 追加 `## Block reason` |
| `in_progress` → `needs-review` | tier=high（不自动 commit）或 M5 soft_escalate |

## 桶 C（Open Items）issue 的差异

- 文件名：`00N-OI-NNN-{slug}.md`，`id` 用 PRD 原 `OI-NNN`
- `status` 恒为 `blocked`（没有 Gherkin AC，永远不该被 step 1 选中）
- body 含 PRD Open Items 表的 9 列原值 + `## How to unblock`
