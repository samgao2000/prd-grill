---
name: auto-dev-lite
description: |
  Autonomous software development pipeline (LITE 版，无 GitHub 依赖，
  git 可选)。从本地 markdown issue 文件驱动到 git commit（有 git 时）
  或 runs/ledger.md 台账（无 git 时），全程 Claude AFK 端到端，
  不需要用户切 terminal 跑 cli。当用户说「用 auto-dev-lite 跑 CRM」
  「local pipeline 走起」「不上 GitHub 跑 auto-dev」时触发。
disable-model-invocation: false
---

# Auto-Dev Lite — Skill

## 触发

  - "用 auto-dev-lite 跑 X"
  - "AFK 实现 PRD"
  - "本地 pipeline 走起"
  - "不上 GitHub 跑 auto-dev"
  - "从 PRD 启动 auto-dev-lite"（隐含触发 step 0.5 自动 import）
  - "把 PRD 转成 issues 跑"

## 与 auto-dev 的关系

| 维度 | auto-dev (full) | auto-dev-lite |
|---|---|---|
| Issue 来源 | GitHub Issues (gh CLI) | 本地 `<target>/local-issues/*.md`（已存在文件 **或** 由 step 0.5 从 `<target>/docs/prd/` 自动 import） |
| Status 流转 | gh issue label `status:*` | issue 文件 frontmatter `status:` 字段 |
| Branch + PR | `auto-dev/run-X` 分支 → gh pr create → merge | **git 可选**：有 `.git/` → 直接 commit 到 main（单分支）；无 git → 每 issue 追加 `runs/ledger.md` 台账条目。trailer 两种模式都写 |
| User-in-loop | 用户 terminal 跑 `python -m auto_dev.cli` | 完全 AFK，Claude 端到端 |
| 适合场景 | 团队协作、issue tracker 权威 | 单人练手、target 项目 git 历史在本地 |
| 复用 auto_dev 模块 | 是（tier/escalation/reviewer/trailer/cost_meter/run_log/kill_switch/acceptance） | 是（同上，跳过 github_client） |

## 核心约束（与 auto-dev full 共享）

1. **Acceptance test immutability**：含 `# AUTO_DEV_ACCEPTANCE: immutable` 标记的文件**永不修改**，
   即便修一行就能让测试通过。测试错了 → 标 `blocked` + 注解，由人改。
2. **Kill switch**：每个主要 step 之间检查 `runs/<run_id>.kill`，存在则中止。
3. **Tier-based 风险控制**：low/medium 自动 commit；high 标 `ready-for-review` 不 commit。
4. **Cost ceiling**：每个 run 默认 $50；超限 hard-stop。
5. **Trailer**：每个 commit（或无 git 时的 ledger 条目）含 `Auto-Dev-Lite-Trailer` 块（run_id/issue_id/tier/files_touched/+/-）。无论哪种模式，**每个 issue 必须留下一条可追溯记录**——丢 trailer 即丢审计链。

## 本地 issue 文件格式

`<target_project>/local-issues/00N-slug.md`：

```markdown
---
id: US-001
title: 单 admin 登录/登出
status: ready          # ready | in_progress | done | blocked | needs-review
tier: medium           # low | medium | high (Claude 初评，可在 step 3 改)
depends_on: []         # [US-NNN, ...]
acceptance_tests: tests/test_us001_login.py    # 写完测试后填
run_id: null           # 跑起来时填
---

# US-001: 单 admin 登录/登出

[完整 user story body，含 INVEST/Gherkin/Cockburn Extensions/Volere QG]
```

**State machine**：
- `ready` → `in_progress`（开跑时）
- `in_progress` → `done`（pytest 通过 + commit 完成）
- `in_progress` → `blocked`（acceptance test 错 / pipeline 无法继续）
- `in_progress` → `needs-review`（tier=high，不自动 merge）

## Run procedure (per issue, AFK)

### 0. 前置检查

- **git 模式探测**（git 是可选项，不是前置条件）：
  - `<target>/.git/` 存在 → `git_mode = tracked`：step 8 用 git commit
  - 不存在 → `git_mode = ledger`：step 8 改写 `runs/ledger.md` 台账；**不要**擅自 `git init`（是否引入版本控制是用户的决定）。开跑前打一行提示：「无 git 仓库，启用 ledger 模式；无法回滚单个 issue 的改动，建议（但不强制）先 git init」
- 探测 `<target>/runs/` 不存在则 lazy 创建
- 读 `<target>/PROJECT_CONTEXT.md` 若存在
- 探测 `<target>/local-issues/` 是否存在且**含 `*.md`** 文件（`.imported.md` 不算）
- 探测 `<target>/docs/prd/` 是否存在且含 `*.md`
- **分支决策**：
  - `local-issues/` 有 issues → 跳过 step 0.5，直接进 step 1
  - `local-issues/` 空 **且** `docs/prd/` 有 PRD → 自动进 step 0.5 import
  - 两者都空 → **hard-stop**：报告"既无现有 issues 也无 PRD，请先跑 req-dev-lite 生成 PRD"

### 0.5. PRD import（仅 local-issues/ 空时自动触发）

把 req-dev-lite 产出的 `docs/prd/YYYY-MM-DD-{slug}.md` 自动转成 `local-issues/*.md`，闭合"PRD → 自动实现"链路。完整规则见 [`references/prd-import-rules.md`](references/prd-import-rules.md)；这里只列**关键摘要**：

**源选择**：取 `<target>/docs/prd/` 下按文件名日期最新一份；多份同日按字母序最后；frontmatter `status: partial` 警告 + 继续。

**三桶映射**（章节锚点对齐 `req-dev-lite/templates/prd-local.md` @ 2026-06-10；中英双语锚点均可，见 references）：

| PRD 章节 | 桶 | 落点 | issue status |
|---|---|---|---|
| `## 3. User Stories（桶 A）` 下的 `### US-NNN：<title>`（冒号可能是全/半角） | A | `local-issues/00N-{slug}.md`（id 字段 = PRD 原 `US-NNN`） | `ready` |
| `## 1. Problem Statement` 下的 `### Outcome Metrics（桶 B）` 表 | B | `<target>/PROJECT_CONTEXT.md` 的 `## Reference Metrics` 段（lazy 创建） | N/A |
| `## 8. Open Items（桶 C ...）` 9 列表中每行 | C | `local-issues/00N-OI-NNN-{slug}.md`（id 字段 = PRD 原 `OI-NNN`） | `blocked`（不会被 step 1 选中） |
| `## 5. Testing Decisions`（SBE 实现 a/b/c） | 配置 | `PROJECT_CONTEXT.md` 的 `## Testing` 段 → 覆盖 step 5 默认 pytest | N/A |

**硬约束**（详见 references）：
- 桶 A body **6 字段逐字拷贝**（作为/追溯/INVEST/Gherkin/Extensions/Volere QG/三桶归属），不重写不简化
- 桶 C 用 PRD 原 `OI-NNN`，status 必为 `blocked`，body 含 9 列原值 + `## How to unblock`
- 桶 B **不**写成 issue，只追加进 PROJECT_CONTEXT.md
- PRD `final_gate_verdict: FAIL` / `not_reached` → **hard-stop**（终审未过不应进实现）
- ID 冲突 / PRD 解析失败 / 三桶全空 → **hard-stop**，不写 partial 文件

**完成后**：写 import log `<target>/local-issues/.imported.md` + 打印总结给用户，然后进 step 1。

### 1. 选下一个 issue

扫 `local-issues/*.md`，按规则选下一个：
- status == `ready`
- **所有 `depends_on` 已 `done`**
- 编号最小者优先

若无候选 → 全部 done，进收尾报告。

### 2. 改 status 到 in_progress，初始化 run

- 修改 issue 文件 frontmatter `status: in_progress`
- 生成 `run_id` = `YYYYMMDDHHMMSS-<6char-rand>`
- 修改 `run_id` 字段
- 创建 `runs/<run_id>/log.jsonl`
- 写第一条事件 `{"event": "issue_fetched", "issue_id": ..., "ts": ...}`

### 3. Tier classify (重新评估)

- 解析 user story body，识别 `planned_paths`（要碰的文件清单）
- 应用 `tier_classifier` 规则：
  - `low`: 仅 comments / docs / config / 单一新文件
  - `medium`: 多文件实现、含逻辑改动、含 schema migration
  - `high`: 跨 ≥3 模块 / 涉及 auth/payment/data-loss 边界 / 含外部 API
- 更新 issue 文件 `tier:` 字段
- 写 `{"event": "tier_classified", "tier": ...}`

### 4. **Claude 担任 M3：写实现 + 测试**

a. **先写 acceptance tests**（从 Gherkin AC 直翻译为 pytest 函数）：
   - 文件含 `# AUTO_DEV_ACCEPTANCE: immutable` 顶部注释
   - 每个 Gherkin Scenario → 一个 test 函数，函数名匹配 scenario
   - 包含 Cockburn Extensions 的分支测试
   - 更新 issue 文件 `acceptance_tests:` 字段
b. **再写实现**：
   - 读相关代码上下文（避免重复造轮）
   - 计划要写/改的文件
   - 用 Write/Edit/bash heredoc 写代码
   - **绝不修改** acceptance test 文件
c. **必要时跑 alembic migration**（schema 改动）

### 5. 跑 pytest（子进程，绝不 in-process）

```python
# 必须 subprocess：in-process 跑 pytest 时，stdout capture 与被测代码的
# ThreadPoolExecutor 在 Windows 上会互相等待造成 deadlock（实测踩过）
import subprocess
result = subprocess.run(
    ["pytest", "--tb=short", "-q"],
    cwd=target_root,
    capture_output=True,
    text=True,
    timeout=300,
)
```

退出码：
- `0` 或 `5`（无测试也算 pass）→ 继续 step 6
- 其他 → hard-stop：
  - issue status → `blocked`
  - 写 `{"event": "pytest_failed", "exit_code": ..., "stderr_tail": ...}`
  - 给 issue body 追加 `## Block reason\n<stderr tail>`
  - 跳到下一个 issue（不阻塞 pipeline，blocked 是 review queue）

### 6. M4 自评 (single-LLM self-review)

> **设计说明——为什么 v1 只用单 LLM。** M4 的原始设计是多 LLM 评审：两个以上
> 独立模型评审同一份 diff，用发现集合的重叠度做 **capture-recapture（捕获-再捕获）**
> 估算——一种源自野生动物种群统计的方法，Watts Humphrey 在其 Personal Software
> Process（PSP）工作中将它用于软件审查，估算尚未发现的遗留缺陷数。刻意推迟的原因：
> 强制要求第二个模型会抬高只有单一 LLM 的用户的使用门槛。因此 v1 采用单 LLM 自评，
> 并在每条评审记录里显式标注 `single_llm: true`——将来多 LLM 评审落地时，两类记录
> 可以区分。该特性列入未来增强计划，用于提升评审效能。

Claude 读自己刚写的 diff，自检：
- 任何明显 correctness 缺陷？（off-by-one、空指针、错误处理缺失）
- 任何 security smell？（明文密码、SQL injection、unescaped HTML、PII 泄露）
- 任何 spec 违反？对照 Gherkin AC 每条
- 任何 acceptance test 被改？（绝对禁止；命中即 hard-stop）

构造 `ReviewReport`：
```python
{
    "single_llm": True,
    "blockers": [...],
    "minor": [...],
    "verdict": "pass" | "fail"
}
```

若 `blockers != []` → hard-stop，同 step 5 failure 处理。

### 7. M5 Escalation decide

```python
state = {
    "cost_spent_usd": <估算>,
    "cost_ceiling_usd": 50.0,
    "test_failure_history": [...],  # 本 run 内 retry 次数
    "new_dependencies": [...],       # pyproject 新增 deps
    "security_findings": [],
    "files_outside_planned_scope": [...],
    "arch_conflicts": False,
    # 来自 PRD frontmatter（step 0.5 import 时记录）：
    # gate_mode=prd-gate → 用 gate_confidence 原值；
    # gate_mode=self-reported/缺省 → min(verdict 映射值, 0.85)
    "requirement_confidence": 0.0,
}
```

决策：
- `hard_stop`：status → `blocked`
- `soft_escalate`：status → `needs-review`，跳下个 issue
- 否则：继续

### 8. 留痕（git commit 或 ledger entry，按 step 0 的 git_mode）

**`git_mode = tracked`**：

```bash
git add -A
git commit -m "$(cat <<'CMSG'
US-XXX: <title>

<short description>

Auto-Dev-Lite-Trailer
---
run_id: <run_id>
issue_id: US-XXX
tier: <tier>
review: single-llm-self-only
cost_usd: <est>
files_touched: <list>
lines: +A -B
trailer_version: lite-1
CMSG
)"
```

**不开 PR / branch**，直接 commit 到 main。

**`git_mode = ledger`**：向 `<target>/runs/ledger.md` **追加**（永不改写历史条目）：

```markdown
## L-NNN — US-XXX: <title>

- completed: <ISO timestamp>
- run_id: <run_id>
- tier: <tier>
- review: single-llm-self-only
- cost_usd: <est>
- files_touched:
  - path/a.py (+A1/-B1)
  - path/b.py (+A2/-B2)
- trailer_version: lite-1-ledger
```

`L-NNN` 单调递增（读文件尾取最大值 +1）。ledger 模式的已知限制（写进收尾报告）：无法 diff/回滚单个 issue；audit 链只到文件粒度。

### 9. 写 done 状态

- issue 文件 `status: done`
- 写 `{"event": "issue_done", "commit_sha": ...}`（ledger 模式写 `"ledger_id": "L-NNN"` 代替 `commit_sha`）
- 跳回 step 1（处理下一个 ready issue）

### 10. 排放校准记录（强制收尾步骤）

run 结束（含 run-all 全部完成或中止清理时），**必须**执行记录排放：
`python -m prd_gate calib add --run runs/<run_id> --prd <PRD 路径>`。
每个 run 恰好一条记录（gate 分数 + 返工结果配对，喂校准分析）。`prd_gate` 未安装时跳过并在收尾报告注明"calibration record not emitted (prd_gate absent)"。规则详见 PRD `docs/prd/2026-06-10-calibration-run-logger.md`。

## Run-all 模式

用户说"跑完所有 ready issue"时：
- 循环执行 step 1-9 直到无 ready issue
- 每个 issue 结束打一行 summary：`✅ US-XXX done in N min, +A/-B lines, commit abc1234`（ledger 模式：`..., ledger L-007`）
- 全部完成后打 final report，含累计耗时 / 累计成本估算 / blocked 列表

## 项目级集成 (PROJECT_CONTEXT.md)

target 项目可在 root 放 `PROJECT_CONTEXT.md`，含：
- target 语言/栈选择
- 测试命令（覆盖默认 pytest）
- 跑 migration 的命令（如 `alembic upgrade head`）
- 部署 smoke 命令

skill 在 step 0 读这个文件，覆盖默认行为。

## 反模式自检

- ❌ 偷偷修改 acceptance test 让它通过 → hard-stop
- ❌ pytest in-process（stdout capture + 线程池在 Windows 会 deadlock）→ 一律 subprocess
- ❌ 编辑器类工具写长文件可能静默截断 → 用 bash heredoc 写 >200 行的文件，写完 `ast.parse`（Python）或语法检查验证完整性
- ❌ 跨 issue 写代码（一个 issue 改 5 个 user story 的代码）→ 违反 INVEST Independent
- ❌ 不写 trailer → 失去可追溯性
- ❌ step 0.5 把桶 B（outcome metrics）或桶 C（open items）误标 `status: ready` → 它们没有 Gherkin AC，跑了一定挂；桶 B 不进 issue，桶 C 永远 `blocked`
- ❌ step 0.5 重写 PRD body 让它更"漂亮" → 破坏溯源，桶 A 必须逐字拷贝

## 模块来源（两级 fallback）

1. 若 `auto_dev` 包已 `pip install -e` 安装（full 版同仓库场景），直接 import：

```python
from auto_dev.modules.tier_classifier import classify, ClassificationMetadata
from auto_dev.modules.escalation import decide, RunState
from auto_dev.modules.trailer import build as build_trailer
from auto_dev.modules.cost_meter import CostMeter
from auto_dev.run_log import RunLog, new_run_id
from auto_dev.kill_switch import KillSwitch
```

2. 未安装（standalone 发行场景）→ 用本 skill 自带的 `references/inlined-helpers.py`
   （纯 stdlib 简化等价版：tier 分级 / escalation 决策含 requirement_confidence
   阈值 0.7 / trailer 构造 / run_id / ledger 追加）。两者语义一致，
   inlined 版规则更粗（关键词启发式），分歧时以 full 版为准。

## 文件清单

- `SKILL.md` — 本文件
- `references/prd-import-rules.md` — step 0.5 完整 PRD import 规则：源选择、三桶映射、frontmatter 格式、edge cases、failure modes、import log 格式
- `references/issue-template.md` — 本地 issue 文件模板（同上方"本地 issue 文件格式"段）
- `references/inlined-helpers.py` — 无 auto_dev 包时的 stdlib fallback 实现
- `sessions/` — 跑完后的 retro 文件（同 req-dev-lite 模式）

## 与 req-dev-lite 的串联

完整 AFK 链路：

```
用户想法 (人在场)
  ↓ req-dev-lite 拷问（必须人答问）
docs/prd/YYYY-MM-DD-{slug}.md（含三桶）
  ↓ auto-dev-lite step 0.5 自动 import（无人介入）
local-issues/*.md（桶 A ready + 桶 C blocked）
  ↓ auto-dev-lite step 1-9 循环（无人介入）
git commit 序列（或 ledger 条目序列）+ retro
```

req-dev-lite 阶段 7 落地 PRD 后**就停**，不会自动触发 auto-dev-lite——保留用户决定何时启动实现的权力。auto-dev-lite 启动时若发现 PRD 已存在且 local-issues/ 空，step 0.5 自动接力。

PRD 格式变更（如 req-dev-lite 改了 `templates/prd-local.md` 的章节结构）需要同步更新 `references/prd-import-rules.md` 的章节锚点。当前对齐版本：**req-dev-lite 2026-06-10 lite 版**（完整契约见 `references/prd-import-rules.md` 末尾「与 req-dev-lite 的契约」节，对应方在 [`../req-dev-lite/SKILL.md`](../req-dev-lite/SKILL.md) 的「下游消费者契约」节）。
