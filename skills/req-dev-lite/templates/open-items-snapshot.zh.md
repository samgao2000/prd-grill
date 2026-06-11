# Open Items Snapshot 模板（lite 版）

会话结束时生成。输出到 `<project_root>/docs/prd/{slug}-snapshot.md`。

**与 req-dev full 版的差异**：
- 不引用 issue tracker 链接（lite 没有 issues）
- 桶 C 的权威载体是 **PRD 文件末尾的 Open Items 表格**，snapshot 仅做会话历史追溯 + resume 状态
- 同一 slug 多次跑（含续跑）共用同一份 snapshot，每次跑结束**覆盖更新**（不按时间戳建新文件，避免 docs/prd/ 膨胀）

```markdown
# 需求开发会话快照（lite）- {slug}

**对应 PRD**：[YYYY-MM-DD-{slug}.md](./YYYY-MM-DD-{slug}.md)
**Slug**：{kebab-case-slug}（用于续跑识别）
**首次会话**：YYYY-MM-DD HH:MM
**最近更新**：YYYY-MM-DD HH:MM
**累计会话次数**：N（含原 session + 续跑）
**累计耗时**：约 NN 分钟
**启用方法清单**：Mom Test + Impact Mapping + 5 Whys + SBE + Cockburn Extensions + INVEST + Volere QG（+ 可选模块 X/Y/Z）
**终审三态结果**：PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached

---

## Resume 信息（仅当最近会话被 Stop 时填写；completed 则全部 N/A）

- **Status**：completed | paused | aborted
- **Stop reason**：`user_initiated` | `agent_failed` | `not_applicable`
- **Pending stage**：N（中断时所在阶段 1/2/2.5/3/4/4.5/5；completed 时 N/A）
- **Pending items**（中断阶段内未答清的问题，条目级；同时已写入 PRD 的 Open Items 表格并标 `[resumable]`）：
  - [ ] [具体问题 1] — 期待答案形状：[Recommended answer 简述]
  - [ ] [具体问题 2] — 期待答案形状：[同上]
- **Resumable slug**：{slug}（用户日后说"继续 req-dev-lite {slug}"时 agent 据此找回本 snapshot）
- **续跑指引**：日后续跑时 agent 先读本段，从 pending_stage 续，**优先问 pending_items**，不重头来过

---

## 三桶统计（最近一次会话）

- 桶 A（Gherkin AC，进 PRD User Stories）：N 条
- 桶 B（Outcome Metric，进 PRD Problem Statement）：N 条
- 桶 C（Open Items，进 PRD 末尾表格）：N 条
- 丢弃（不归三桶，进 PRD Out of Scope）：N 条

---

## 桶 C 摘要（详情见 PRD 文件 § 8 Open Items）

> 这里只是会话视角的快速索引，权威载体是 PRD 文件。两边数据冲突时以 PRD 为准。

| OI-ID | 标题 | 拦截阶段 | Owner | 答复截止 | 当前状态 |
|---|---|---|---|---|---|
| OI-001 | <简述> | 阶段 X | @user 或 [TBD] | YYYY-MM-DD | open / `[resumable]` / resolved / still-open |
| OI-002 | … | … | … | … | … |

---

## 已解决决策（仅供历史追溯，正式记录在 PRD 的 Implementation Decisions）

会话期间达成共识但**未触发新 ADR**的决策列在这里：

### D-001：<简短描述>
- **决策**：<结论>
- **依据**：<为什么这么决定，对应阶段几>

### D-002：……

---

## 命中过的反模式（教训记录）

会话期间触发过的反模式（用于团队学习；详细计数在 retro 文件里）：

- [ ] 客套话陷阱 — N 次
- [ ] 未来时陷阱 — N 次
- [ ] 方案伪装成需求 — N 次（哪些方案被 5 Whys 降级了？列出）
- [ ] 抽象 AC — N 次（最初哪些 weasel word？修正为？）
- [ ] happy path 陷阱 — N 次

---

## 会话历史（按时间倒序）

> 每跑一次（含续跑）追加一条。

### Run 2 (resumed) — YYYY-MM-DD HH:MM
- Status: completed
- Resumed from: YYYY-MM-DD-HHMM-{slug}（首次 session）
- 解决了 OI-NNN, OI-MMM
- 新增 OI-XXX

### Run 1 — YYYY-MM-DD HH:MM
- Status: paused（user_initiated）
- 卡在阶段 X
- 产出 N 条 user stories，N 条 OI

---

## 下次会话准备

- [ ] OI-XXX 负责人答复 → 入下次会话开场
- [ ] OI-YYY 数据待查 → 跑完 SQL 后入下次会话
- [ ] 阶段 1 钉死的 Why/Who/How 已锁，不再开会重审
```
