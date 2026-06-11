---
session_id: YYYY-MM-DD-HHMM-{slug}
date_start: YYYY-MM-DD HH:MM
date_end: YYYY-MM-DD HH:MM
duration_minutes: NN
slug: {kebab-case-slug}
status: completed | paused | aborted | escalated
stop_reason: not_applicable | user_initiated | agent_failed
pending_stage: N | null   # 仅当 status=paused 时填阶段编号
resumed_from: YYYY-MM-DD-HHMM-{原 slug} | null   # 仅当本 session 是续跑时填
prd_file: docs/prd/YYYY-MM-DD-{slug}.md | null   # lite 版：本地路径，不是 issue
snapshot_file: docs/prd/{slug}-snapshot.md | null
final_gate_verdict: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached
---

> **status / stop_reason 对照表**：
> - `completed` + `not_applicable`：正常跑完三桶归位 + 终审过
> - `paused` + `user_initiated`：用户主动停（疲劳/优先级/时间），意图续跑
> - `paused` + `agent_failed`：agent 没问到位陷死循环，进 retro 改进信号
> - `aborted` + 任一：会话作废不续跑（如需求被砍）
> - `escalated` + 任一：升级到人为决策不再走本 skill

# Retrospective: {简短标题}

> 这是 req-dev-**lite** 版的 retro。lite 版 PRD 落地为本地文件而非 issue，retro 字段的 `prd_file` / `snapshot_file` 走本地路径。其余字段与 req-dev full 版一致。

## 启用方法

**核心（必跑）**：
- [x] Mom Test
- [x] Impact Mapping
- [x] 5 Whys
- [x] Specification by Example (Gherkin)
- [x] Cockburn Extensions
- [x] INVEST
- [x] Volere QG

**可选（按信号触发）**：
- [ ] Event Storming — 触发信号：[填] | 未触发
- [ ] JTBD/ODI — 触发信号：[填] | 未触发
- [ ] KAOS 目标树 — 触发信号：[填] | 未触发
- [ ] Continuous Discovery / OST — 触发信号：[填] | 未触发
- [ ] Critical Decision Method — 触发信号：[填] | 未触发

## 阶段耗时（估算）

| 阶段 | 耗时（min） | 备注 |
|---|---|---|
| 1 开场四问 | | |
| 2 拷问循环 | | |
| 2.5 5 Whys 拦截 | | 触发次数：N |
| 3 领域校准 | | CONTEXT.md inline 更新次数：N |
| 4 结构化 user stories | | |
| 4.5 不开心路径 | | |
| 5 终审 | | 通过轮次：N/3 |
| 6 三桶分类 | | |
| 7 落地（写本地 PRD 文件） | | |
| 8 retro（本步） | | 自动写不计入 |

## Stop 场景（仅当 status ≠ completed 时填写）

> `status=completed` 的 session 这一段写 `not_applicable`。

- **Stop reason**：user_initiated | agent_failed
- **Pending stage**：N（中断时所在阶段）
- **触发短语 / 触发情境**：
  - 如 `user_initiated`：用户原话短语（如「先放着」「我累了」「先生成 PRD」）
  - 如 `agent_failed`：agent 自检触发情境（连续 N 轮无法推进 / 死循环 / 用户答案反复绕开）
- **Pending items 数量**：N 条进桶 C（在 PRD 末尾 Open Items 表格中标 `[resumable]`）
- **Resume 路径**：续跑时用户该说「继续 req-dev-lite {slug}」，agent 读 `docs/prd/{slug}-snapshot.md` 的 Resume 段
- **如果是 agent_failed**：本条 stop 同时是 retro 的[SIG-N]改进信号源，**必须**在下方"改进信号候选"段标记对应 SIG

---

## 三桶统计

| 桶 | 数量 | 占比 |
|---|---|---|
| A（Gherkin AC，进 PRD User Stories） | N | NN% |
| B（Outcome Metric，进 PRD Problem Statement） | N | NN% |
| C（Open Items，进 PRD § 8 表格） | N | NN% |
| 丢弃（进 PRD § 6 Out of Scope） | N | NN% |

> 桶 C 占比 >30% 是异常信号——说明需求成熟度不够，下次会话开场前应先解决遗留 open items。
> 若是 paused 状态，桶 C 占比包含 pending_items（中断时未答清的部分），不要因高占比误判为成熟度问题。

## 反模式命中次数

| 反模式 | 命中次数 | 备注（哪些方案被降级了/哪些 weasel word 被修） |
|---|---|---|
| 客套话陷阱 | N | |
| 未来时陷阱 | N | |
| 方案伪装成需求 | N | 5 Whys 把 [方案 X] 降级为 outcome [Y] |
| 抽象 AC | N | weasel words 修：[列表] |
| happy path 陷阱 | N | 阶段 4.5 补了哪些分支 |

## 卡点（Friction Points）

> 会话中**卡 >2 轮**才推进的步骤。记录哪卡了、为什么卡、最终怎么过的。

### Friction-1
- **阶段**：
- **现象**：用户对 [某问题/某概念] 反复无法给具体答案
- **原因**：用户不理解 | agent 问得不清 | 方法不适用 | 项目上下文缺失 | 其他
- **如何破**：换问法 / 给例子 / 查代码 / 跳到下一题先做 / 其他
- **如果方法本身可疑**：标 [SIG-N]，进改进信号段

### Friction-2
...

## 用户原话反馈

> 直接引语，**不要改写**。仅打码 PII（人名/邮箱）。

- "..." （阶段 N）
- "..." （阶段 N）

## Agent 自评

### 好用的问句
- [ ] 阶段 X 问的「...」用户秒回，效果好
- [ ] 阶段 Y 的代码交叉验证一下子穿透了一个伪装的需求

### 难用/有问题的问句
- [ ] 阶段 X 问的「...」用户绕了 3 轮才理解 → 候选信号 [SIG-N]
- [ ] 阶段 Y 漏问了 [...]，事后才意识到

### 是否过度问
- [ ] 阶段 X 问了 N 个本可以查代码解决的问题
- [ ] 某条 user story 已经够清晰还在追加问句

### lite 特有自评
- [ ] 用户曾问"为什么不发 issue"——说明 lite 选错了，应该用 req-dev full 版。记录触发情境以便 retro 改 description 触发条件
- [ ] PRD 末尾 Open Items 表格 owner=TBD 的条目超过 24h 没补全——说明 owner 字段的强制性宣讲不够，标 [SIG-N]

## 改进信号候选

> ⚠️ **不**直接修改 SKILL.md/templates。这里只标信号。retro skill 聚合 ≥3 次同向信号才提议改。

格式：`[SIG-N] 描述 + 证据 + 建议改进方向`

- [SIG-1] 阶段 X 问句「...」频繁让用户困惑。建议改为「...」或拆成两个子问。证据：本会话 friction-1。
- [SIG-2] 可选模块 [X] 触发条件不清晰，本次本应该启用但没启用。建议在 methods.md §X 加触发示例。证据：本会话阶段 1 应启用未启用，导致阶段 3 补救耗时 N 分钟。
- [SIG-3] ...

## 元数据备注

任何不属于上面段的内容（项目特殊情况、用户当天状态、外部干扰等）写在这里。
