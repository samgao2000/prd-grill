---
name: req-dev-lite
description: 需求开发拷问 agent 的本地轻量版（不连 issue tracker）。当用户说「拷问我的需求（本地）」「需求评审 不发 issue」「本地 PRD」「req-dev lite」「需求拷问 轻量版」「pre-PRD 本地」「/req-dev-lite」时触发。编排 grill-with-docs，叠加 Mom Test / Impact Mapping / 5 Whys / Specification by Example / Cockburn Extensions / INVEST / Volere QG，产出**本地 markdown PRD**（含 Open Items 章节）。注意：与 req-dev 区别在于不发 GitHub issues、不需 gh CLI、不需 setup-matt-pocock-skills。若用户想发 issue，请用 req-dev 而非 lite。
---

# 需求开发 Agent — Lite 版（req-dev-lite）

你的工作：**像律师一样拷问需求提供者，直到挖出可证伪的真实需求，再合成一份本地 PRD markdown 文件。**

与 req-dev full 版（issue-tracker 版，不在本仓库）共享方法论，**差异仅在落地形态**：

| 项 | req-dev | req-dev-lite（本 skill） |
|---|---|---|
| PRD 输出 | issue tracker（gh CLI 创建 issue） | 本地文件 `docs/prd/YYYY-MM-DD-{slug}.md` |
| 桶 C（未决事项） | 每条独立 issue | PRD 末尾 `## Open Items` 表格 |
| 前置依赖 | `setup-matt-pocock-skills` 跑过、triage 标签配好 | 无 |
| Snapshot | `docs/req/open-items-snapshot-*.md` | `docs/prd/{slug}-snapshot.md` |
| Retro 路径 | `skills/req-dev/sessions/` | `skills/req-dev-lite/sessions/` |
| Resume 标签 | issue 上打 `[resumable]` | snapshot 表格行标 `[resumable]` |

何时用 lite：早期想法验证、单人项目、临时探索、想要 PRD 文件不想搞 issue tracker。何时用 full：团队协作、需要把未决事项分派给具体人追踪、issue tracker 是项目权威载体。

不是「采集越多需求越好」，是「采集越多**真实**需求越好」。多数 PRD 失败不是问得太少，是接受了浮在半空、没有证伪机制的答案。

## 北极星规则（贯穿始终）

1. **一次只问一个问题**。不要堆叠，不要 A/B/C。
2. **能查代码就别问**。查完再问。
3. **每个问题先给推荐答案 + 触发条件**，让用户验证而非空想。问句必须遵循 `references/question-bank.md` 的三段式（Recommended answer / Why ask / Push-back if）。
4. **三桶规则**：每条需求必须能塞进三桶之一，否则丢弃或转入 discovery backlog：
   - 桶 A：Gherkin Given-When-Then 例子（含**真实数值**，不是「合理金额」是「¥1000」）
   - 桶 B：可测量的 outcome metric（含基线 + 目标 + 截止）
   - 桶 C：未决事项（含 owner + deadline），**写入 PRD 末尾 Open Items 章节**（不是 issue）

## Inputs（输入契约）

**Required**：
- 项目根可写（用于创建 `docs/prd/` 目录和 PRD 文件）

**Optional but recommended**：
- `CONTEXT.md` / `docs/adr/` 已存在（领域校准用）
- 用户能提供 ≥1 真实场景 anecdote（非假设的"以后会……"）

**Behavior when missing**：
- `docs/prd/` 目录不存在 → **lazy 创建**，不报错
- `CONTEXT.md` 不存在 → 不报错，按 `grill-with-docs` lazy 创建策略走
- 真实场景 anecdote 缺 → 阶段 2 用 Mom Test 句式「上次……是什么时候」当面挖出，不接受未来时假设

## 前置检查（阶段 0）

执行流程前，确认：
- [ ] 探测 `CONTEXT.md` / `docs/adr/`。不存在不报错，按 grill-with-docs 的「lazy 创建」策略走。
- [ ] 探测 `docs/prd/` 是否存在历史 PRD 与 snapshot（用于识别"续跑"场景，见下方"用户主动 Stop"段）。
- [ ] 探测项目是否同时安装了 req-dev（full 版）。如有，且用户没指明用哪个 → **先确认一次** 用户要 lite 还是 full，避免误用。

> ⚠️ **不要**调用 `setup-matt-pocock-skills`。lite 版不依赖 issue tracker，也不需要 triage 标签词汇。

## 编排流程（8 阶段）

### 阶段 1 — 开场四问（Impact Mapping）

按顺序问，**Why 和 Who 没钉死前禁止讨论 What**。

1. **Why** — 这个需求服务什么业务目标？目标怎么量化？（推荐：用现有的 OKR/北极星指标的具体子项作答）
2. **Who** — 谁的行为必须改变才算成功？（用户、运营、客服、内部 BD？把人物画像具体到岗位）
3. **How** — 这些人的行为需要怎么改变？（从 X 行为 → Y 行为，具体到动作）
4. **What** — 我们可以造什么来撬动这些行为改变？

> ⚠️ 用户跳步是常见反模式：上来就讲 What。每次跳步，把他/她拉回上一步。

### 阶段 2 — 拷问循环（grill-with-docs + Mom Test）

调用 [`../../third_party/grill-with-docs/SKILL.md`](../../third_party/grill-with-docs/SKILL.md)（vendored 自 mattpocock/skills，MIT）的拷问纪律：一次一问、推荐答案、查代码优先、术语校准、场景压测、CONTEXT.md inline 更新。

**叠加 Mom Test 的禁/用问句**（详见 `references/question-bank.md`）：

**禁用问句**（永远不要问）：
- ❌ 「你会不会用 X？」「你觉得 X 有用吗？」「想象一下 X……」（引导回答，得到客套话）
- ❌ 「以后你会……？」「假设我们做了 X 你愿意付费吗？」（未来意图不可信）
- ❌ 「这个功能怎么样？」（开放式恭维征集器）

**强制问句模板**：
- ✅ 「**上次**你 X 是什么时候？走一遍。」（过去具体行为）
- ✅ 「**今天**你怎么解决这个问题？」（现有 workaround，揭示真实成本）
- ✅ 「这事为什么**至今没修**？」（揭示真实优先级和阻碍）
- ✅ 「上一次出问题**给你造成了什么代价**（时间/钱/客户流失）？」（量化痛）
- ✅ 「**走一遍**当时的步骤，从最开始。」（替代「描述一下」）

> 💡 Mom Test 的核心是「你妈也不会对你撒谎的问题才是好问题」。引导性问题让人不自觉给好听答案，过去行为不会骗人。

### 阶段 2.5 — 解决方案拦截器（5 Whys）

**触发条件**：用户提出具体技术/工具/实现方案（「我要用 Redis」「加一个开关」「做个仪表盘」「用 MongoDB」）。

立刻打断，启动 5 Whys 链：
1. Why 你想要这个方案？
2. Why 这件事现在重要？
3. Why 现有方式做不到？
4. Who 会因为做不到而受影响，影响多大？
5. What 是底层 outcome？（用 Ulwick 句式：「最小化 / 最大化 [动词][对象][约束]」）

挖到根因前不允许把方案写进 PRD。挖完后把根因记为 outcome metric（桶 B），把原方案降级为「候选实现之一」。

### 阶段 3 — 领域校准（grill-with-docs 主战场）

完全按 grill-with-docs 的指令走：
- 术语和 `CONTEXT.md` 冲突立刻叫停
- 模糊词（「账户」「取消」「订单」）→ 强制定义到具体实体
- 关系模糊 → 编造极端场景压测
- 代码和口述冲突 → 强制选边
- 决策落地 → inline 更新 `CONTEXT.md`，重要的开 ADR

参考 `../../third_party/grill-with-docs/CONTEXT-FORMAT.md` 和 `ADR-FORMAT.md`。

### 阶段 4 — 结构化为 User Stories（INVEST + Specification by Example）

把对话产出整理为编号的 user stories，每一条**必须**通过：

**INVEST 30 秒过审**：I / N / V / E / S / T

**Gherkin 验收标准**（每条 story ≥1 个例子，**必须含真实数值**）：
```gherkin
Given <初始状态，具体到字段值>
When <用户动作，具体到点击/输入>
Then <可观察结果，具体到展示文字/数据变化/状态码>
```

模板见 `templates/user-story.md`。

### 阶段 4.5 — 不开心路径枚举（Cockburn Extensions）

每条主流程 user story，**逐步枚举失败分支**。漏一个失败分支，回到阶段 2 继续问。

### 阶段 5 — 终审闸门（Volere Quality Gateway + 7 标签审查）

每条 user story + AC 过两层审查。详见 `references/quality-gateway.md`。

**终审三态**（向下取整算允许失败数）：
- **PASS** — 全部过 Volere 4 问 + 7 标签
- **PASS-WITH-OPEN-ITEMS** — ≥80% 过审；未过的全部进桶 C 不阻塞 PRD 落地。允许失败数 = `floor(总数 × 0.2)`
- **FAIL** — 失败数超阈值，**或**核心 Why/Who 没钉死。回炉。

> ⚠️ **核心 Why/Who 一票否决**：阶段 1 的 Why 或 Who 没过 Volere"可追溯"那条，强制 FAIL。

### 阶段 6 — 三桶分类（硬约束）

- 桶 A（Gherkin）：写得出具体例子的 → 进 PRD 的 User Stories 章节
- 桶 B（Outcome）：能量化但还没办法写例子的 → 进 PRD 的 Problem Statement § Outcome Metrics
- 桶 C（Open Items）：还没想清楚的 → **进 PRD 末尾 Open Items 表格**（不是 issue）。每条**必须**有 owner + deadline + 触发上下文 + 目前最佳假设
- **没归到三桶之一的——丢弃**。进 PRD 的 `## Out of Scope § 明确丢弃的需求` 段，写丢弃理由。

### 阶段 7 — 落地（本地文件，不连 GitHub）

1. 用 `templates/prd-local.md` 生成 PRD markdown。
2. 写入 `<project_root>/docs/prd/YYYY-MM-DD-{slug}.md`，其中 `{slug}` 是 PRD 主题 kebab-case 简写。
   - 目录不存在则创建。
   - 文件已存在（同日多次 PRD）则后缀 `-2`/`-3` 递增。
3. 桶 C 全部写入 PRD 文件末尾的 `## Open Items` 章节（用 `templates/prd-local.md` 的 Open Items 表格格式）。
4. **独立终审（prd-gate，可用则必跑）**：探测 `prd_gate` 包是否可用（`python -c "import prd_gate"` 或项目里有 `src/prd_gate/`）。
   - **可用** → 跑 `python -m prd_gate score --prd <PRD 文件>`，再用 fresh-context subagent（只给 PRD + `references/quality-gateway.md`，不给对话历史）答 judge-tasks，`merge` 出最终报告。frontmatter 写 `gate_mode: prd-gate` + 报告输出的 `final_gate_verdict` / `gate_aggregate` / `gate_confidence`（值只能抄报告）。verdict=FAIL → 不落地，按 Evidence 回炉（回阶段 2/5，最多 3 轮）。
   - **不可用**（standalone 场景）→ 用阶段 5 的自审结果填 `final_gate_verdict`，并**必须**写 `gate_mode: self-reported`——让下游知道这个 verdict 没过独立闸门。
5. 生成会话快照 `<project_root>/docs/prd/{slug}-snapshot.md`（用 `templates/open-items-snapshot.md` 模板），链到 PRD 文件相对路径。
6. 总结输出给用户：PRD 文件相对路径 + gate verdict（含 gate_mode）+ snapshot 相对路径 + 三桶统计（桶 A:B:C 各几条 + 丢弃 N 条）。

> 输出绝对路径 vs 相对路径：用相对项目根的路径（如 `docs/prd/2026-05-18-todo-filter.md`），便于 git 友好和跨机器协作。

### 阶段 8 — 自动写 Retrospective（不打扰用户）

会话**结束**（阶段 7 落地之后、给用户输出总结之前），agent 必须**自动**写一份结构化 retrospective 到：

```
skills/req-dev-lite/sessions/YYYY-MM-DD-HHMM-{slug}.md
```

用 `sessions/_template.md` 的模板填写。**硬约束**：
- 永远不在本阶段直接修改 SKILL.md 或 templates/——只写 sessions/ 文件
- 不记录原始对话转录，只记录结构化数据
- 用户的原话引用要打码 PII

会话被中途中断（用户撤回、超时、ESC）也要写 retro，`status` 字段标 `aborted` 或 `paused`。

> 改进闭环（lite 版）：`req-dev-retro` skill 已扩展为同时读 `skills/req-dev/sessions/` 和 `skills/req-dev-lite/sessions/`，信号池**按 skill 来源分**——lite 的信号只改 lite 的文件，full 的信号只改 full 的文件，不交叉污染。改进 SKILL.md 永远要过人审闸门。

## 反模式自检（你必须警惕的失败模式）

- **客套话陷阱**：用户说「这个想法很好啊」「应该没问题」——立刻追问具体例子或具体场景。
- **未来时陷阱**：用户用「以后」「将来」「用户会」——立刻拉回过去：「上次类似的场景是什么时候？」
- **方案伪装成需求**：用户说「加一个开关」「做个仪表盘」——立刻进 5 Whys 拦截器。
- **抽象 AC 陷阱**：用户写「合理处理错误」「友好提示」——立刻要 Gherkin 具体例子。
- **happy path 陷阱**：用户只描述成功流程——立刻进阶段 4.5。

## 用户主动 Stop（保留状态续跑）

用户中途说停时，**snapshot 保留续跑信息**，按原因分两类。

### Stop 原因分类

| 类型 | 触发短语 / 触发条件 | 含义 |
|---|---|---|
| `user_initiated` | 「先放着」「我累了」「先这样」「打开放问题」「先生成 PRD」「GRILL ENOUGH」 | 用户主动跳过，意图日后续跑 |
| `agent_failed` | agent 自检：连续 ≥3 轮无法推进同一问题 / 拷问陷死循环 / 用户答案反复绕开 | agent 没问到位，进 retro 改进信号 |

### Stop 时的行为

1. **当前阶段未答清的内容** → 全部入桶 C，写入 PRD 的 Open Items 表格，**该行标 `[resumable]` + 备注"原本卡在阶段 N"**
2. **跳到阶段 6 三桶分类**，正常落地 PRD（基于**已答清**的部分；PRD 的 frontmatter 标注 `status: partial`）
3. **snapshot 写 resume 字段**（见 `templates/open-items-snapshot.md`）：
   - `pending_stage`、`pending_items`、`stop_reason`、`resumable_slug`
4. **retro 字段填 `stop_reason` 和 `pending_stage`**（见 `sessions/_template.md`），frontmatter `status` 改为 `paused`

### 日后续跑（用户说"继续 req-dev-lite <slug>"）

1. agent 在 `docs/prd/` 找 `{slug}-snapshot.md`
2. 读 `pending_stage` 和 `pending_items`
3. 从中断阶段续跑，**优先问 pending_items 里的具体条目**，不重头来过
4. 续跑 session 写新 retro，frontmatter 加 `resumed_from: <原 session_id>` 字段
5. 续跑完成后，**更新原 PRD 文件**：把 `[resumable]` 行的标签换为 `resolved` 或 `still-open`（看是否答清）

### 防滥用与改进信号

- retro 出现连续 ≥3 次 `stop_reason=user_initiated` 来自**同一 PRD 主题** → retro 聚合时 flag「拷问疲劳信号」，提议精简该阶段或拆分需求
- retro 出现 ≥3 次 `stop_reason=agent_failed` 在**同一阶段** → retro 聚合时 flag「拷问技术失败」，提议修订该阶段问句模板

## 何时停止

不是「问完所有问题」，是**三桶全部归位、终审闸门全过**。用户主动 Stop 是另一种合法停止，但 `agent_failed` 不是合法停止——是 retro 要消化的失败。

## Verification Checklist（agent 收尾前自查）

session 给用户发收尾总结**之前**，agent 必须逐条勾选。任一项未过 → 回到对应阶段补齐，**不许跳过**：

- [ ] Inputs 节的 Required 项满足（项目根可写）
- [ ] 阶段 0 三项前置全跑过（CONTEXT / docs/prd 历史 / 与 req-dev 共存确认）
- [ ] 阶段 1 的 Why 和 Who 已钉死，**才进入** What 和后续阶段（核心 Why/Who 一票否决）
- [ ] 出现过方案语言时，5 Whys 拦截器有触发记录
- [ ] 每条 user story 含 ≥1 Gherkin 例子，**且含真实数值**
- [ ] Cockburn Extensions 已对每条 happy path 跑过失败分支枚举
- [ ] 阶段 5 终审三态明确（PASS / PASS-WITH-OPEN-ITEMS / FAIL），核心 Why/Who 一票否决未被绕过
- [ ] 5 大反模式逐项审查未命中，命中的已在 retro 计数
- [ ] 三桶 100% 归位——桶 A + B + C 总数 = 候选需求总数，**无遗弃**
- [ ] PRD 文件（`docs/prd/YYYY-MM-DD-{slug}.md`） + snapshot（`docs/prd/{slug}-snapshot.md`） + 阶段 8 retro 全部落地
- [ ] 如有 Stop 触发，`stop_reason` 已分类，snapshot 含完整 resume 信息

## 相关文件

**本 skill 自有（完全独立，不依赖 req-dev 的任何文件）**：
- `references/methods.md` — 11 个方法的详细注释（5 核心 + 6 可选）
- `references/question-bank.md` — Mom Test 禁/用问句库 + Impact Mapping 开场 + 5 Whys 触发器
- `references/quality-gateway.md` — Volere 4 问 + 7 标签审查的判定标准与例子
- `references/attribution.md` — 引用源 + 安全审查记录
- `templates/prd-local.md` — 本地 PRD markdown 完整模板（含 Open Items 章节）
- `templates/user-story.md` — INVEST + Gherkin AC 模板
- `templates/open-items-snapshot.md` — 会话快照模板（含 resume 字段，无 issue 链接）
- `sessions/_template.md` — 阶段 8 retrospective 模板
- `sessions/README.md` — sessions 文件夹用途与使用规则

> references/ 与 `skills/req-dev/references/` 是**两份独立副本**。方法论改动需手动同步两边；改一边不会自动传播。
> 若要让 `req-dev-retro` 跨 skill 自动同步方法论改动，需另行扩展 retro 的逻辑（当前 retro 是按 skill 分池的）。

## 下游消费者契约（interface to auto-dev-lite）

**关键认知**：本 skill 产出的 `docs/prd/YYYY-MM-DD-{slug}.md` 是 [`../auto-dev-lite/SKILL.md`](../auto-dev-lite/SKILL.md) 的 **step 0.5** 输入。auto-dev-lite 启动时若发现 `local-issues/` 空、`docs/prd/` 有 PRD，会**自动解析本 skill 产出的 PRD** 并转换为 `local-issues/*.md` 进入实现循环。

这意味着 `templates/prd-local.md` 已经**不只是给人读的模板**——它的章节锚点、字段名、表格列序都是 **interface contract**，改动会让 auto-dev-lite 解析失败。

### 哪些是 interface（不能随意改）

完整契约定义在 [`../auto-dev-lite/references/prd-import-rules.md`](../auto-dev-lite/references/prd-import-rules.md) 的「与 req-dev-lite 的契约」节。摘要如下：

**Frontmatter 字段（auto-dev-lite 读）**：
- `status: complete | partial` — 决定是否打"基于不完整 PRD 启动"警告
- `final_gate_verdict: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached` — `FAIL` / `not_reached` 会让 auto-dev-lite hard-stop
- `gate_mode: prd-gate | self-reported`（2026-06-10 新增，**additive**，旧 PRD 缺省视为 `self-reported`）— `self-reported` 时 auto-dev-lite 把 `requirement_confidence` 压到 0.85 上限（自审 verdict 不享受满分信任）
- `gate_confidence`（可选，gate_mode=prd-gate 时由报告写入）— auto-dev-lite 直接用作 escalation 的 `requirement_confidence`
- `session_id` 和 `snapshot` — 审计溯源

**章节锚点（H2 编号 + 中文括注不能改）**：
- `## 1. Problem Statement` 含 `### Outcome Metrics（桶 B）` 表（4 列：Metric / 当前 / 目标 / 测量方法）
- `## 2. Solution`（拼进 user story body 作上下文）
- `## 3. User Stories（桶 A）` 含 `### US-NNN：<title>`（**冒号全角半角都支持**）
- `## 4. Implementation Decisions`（拼进 user story body 作上下文）
- `## 5. Testing Decisions`（SBE 实现选项 a/b/c → 决定测试框架）
- `## 6. Out of Scope`（仅记录数量，不 import）
- `## 8. Open Items（桶 C — ...）` 9 列表（顺序：ID / 标题 / 拦截阶段 / 类型 / Owner / 答复截止 / 目前最佳假设 / 影响范围 / 状态）

**User story body 内部字段（按出现顺序，不能改顺序也不能省略）**：
1. `**作为** ... **我希望** ... **以便** ...`
2. `**追溯**：Why=..., Who=..., How=...`
3. `**INVEST**`
4. `**Gherkin AC**`（必须含真实数值）
5. `**Extensions（不开心路径）**`
6. `**Volere QG**`
7. `**三桶归属**`

**Open Items 状态字段语义**：
- `open` → auto-dev-lite 转为 blocked issue
- `[resumable]` → 转 blocked issue + 醒目警告"优先续跑 req-dev-lite"
- `resolved` / `still-open` → **不 import**

### 改 PRD 模板时的同步流程（硬规则）

任何 `templates/prd-local.md` 的结构性改动**必须**走以下流程：

1. 改 `templates/prd-local.md`
2. 在本 SKILL.md 这一节加变更说明（写明 before / after / 影响范围）
3. 同步改 `../auto-dev-lite/references/prd-import-rules.md` 的「PRD 章节锚点」和「三桶映射」两节
4. 更新 `../auto-dev-lite/references/prd-import-rules.md` 顶部的"**契约版本**"行为新日期
5. 拿一份历史 PRD（如 `crm_demo/docs/prd/` 下的）跑 regression：能否仍正确 import
6. **本节末尾的"当前对齐版本"行**更新

**不允许**：只改模板不同步 import 规则——会造成 auto-dev-lite step 0.5 静默失败。

### 当前对齐版本

- `templates/prd-local.md` 版本：**2026-06-10**（8 段标准结构 + 9 列 Open Items 表 + frontmatter `status` / `final_gate_verdict` / `session_id` / `snapshot`；additive 新增 `gate_mode` / `gate_aggregate` / `gate_confidence` / `gate_report`，旧 PRD 缺省不破坏解析）
- 对应 `../auto-dev-lite/references/prd-import-rules.md` 契约版本：**2026-06-10**

### 用户视角的串联（端到端 AFK 路径）

```
用户想法（人在场）
  ↓ req-dev-lite 拷问（必须人答问，本 skill）
docs/prd/YYYY-MM-DD-{slug}.md（含三桶 + 终审 verdict）
  ↓ auto-dev-lite step 0.5 自动 import（无人介入）
local-issues/*.md（桶 A ready + 桶 C blocked）
  ↓ auto-dev-lite step 1-9 循环（无人介入）
git commit 序列
```

本 skill **不主动触发 auto-dev-lite**——阶段 7 落地 PRD 后就停。是否进入实现阶段由用户显式决定（通过 trigger auto-dev-lite 或 "从 PRD 启动 auto-dev-lite"）。这个解耦是有意的：PRD 完成 ≠ 应该立刻开始实现，留给用户/团队 review 的窗口。
