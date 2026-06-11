# 本地 PRD 模板（req-dev-lite）

阶段 7 用本模板生成 PRD markdown 文件。输出到 `<project_root>/docs/prd/YYYY-MM-DD-{slug}.md`。

**关键差异（与 req-dev full 版的 PRD）**：
- 桶 C（未决事项）写入末尾 `## Open Items` 章节，**不**开 issue
- frontmatter 含 `status` 字段（`complete` / `partial`），标识是否经过完整三桶归位
- 文件本身就是权威载体，不依赖 issue tracker

复制下面整段（从 `---` frontmatter 起到文末），填空。

```markdown
---
title: <PRD 标题>
slug: <kebab-case-slug>
created: YYYY-MM-DD
author: <填用户名或留空>
status: complete | partial   # partial = 用户中途 Stop，基于已答清部分落地
final_gate_verdict: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached
gate_mode: prd-gate | self-reported   # prd-gate = 独立闸门跑过 merge；self-reported = 阶段 5 自审（无独立验证）
gate_aggregate:    # 仅 gate_mode: prd-gate 时填，抄 .gate.json 的 aggregate
gate_confidence:   # 仅 gate_mode: prd-gate 时填，抄 .gate.json 的 requirement_confidence
gate_report:       # 仅 gate_mode: prd-gate 时填，.gate.json 相对路径
methods: [Mom Test, Impact Mapping, 5 Whys, SBE, Cockburn, INVEST, Volere QG]
session_id: YYYY-MM-DD-HHMM-{slug}   # 对应 skills/req-dev-lite/sessions/ 下的 retro 文件
snapshot: docs/prd/{slug}-snapshot.md
---

# <PRD 标题>

> 一句话摘要：<用户原话或贴近原话的一句>

## 1. Problem Statement

### 业务目标（来自 Impact Mapping）

- **Why**：<阶段 1 钉死的业务目标 + 量化指标>
  - 基线：<当前指标值>
  - 目标：<目标指标值>
  - 截止：YYYY-MM-DD
- **Who**：<具体角色，到岗位粒度>
- **How**：<X 行为 → Y 行为>

### Outcome Metrics（桶 B）

| Metric | 当前 | 目标 | 测量方法 |
|---|---|---|---|
| <指标 1> | X | Y | <描述> |
| <指标 2> | X | Y | <描述> |

### 现状与痛点

<会话期间用 Mom Test 挖出的真实场景 anecdote，过去时具体例子，不接受"以后会"假设>

- <Anecdote 1：上次发生时间 + 具体步骤 + 代价>
- <Anecdote 2：……>

---

## 2. Solution（候选方案，非锁定）

> 5 Whys 拦截器已把方案降级为「候选实现」，不锁死。

- **方案 A**：<简述> — <为什么 fit>
- **方案 B**：<简述> — <为什么 fit>
- **暂不考虑**：<被 5 Whys 拍掉的方案 + 拍掉理由>

---

## 3. User Stories（桶 A）

每条用 `templates/user-story.md` 的完整结构（INVEST + Gherkin + Cockburn Extensions + Volere QG 自检 + 三桶归属）。**禁止**省略为一行 "As a..., I want..."。

### US-001：<简短标题>

**作为** <具体角色>，**我希望** <动作 + 对象>，**以便** <可观察的价值>。

**追溯**：Why=<OKR-XX>, Who=<角色>, How=<X → Y>

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**（必须含真实数值）：
```gherkin
Scenario: <场景名>
  Given <初始状态，具体到字段值>
    And <其他前置>
  When <用户动作，具体到点击/输入>
  Then <可观察结果，具体到文字/数据/状态码>
    And <其他可观察结果>
```

**Extensions（不开心路径）**：
- 1a. <步骤 1 失败/超时> → <具体行为>
- 2a. <步骤 2 失败> → <具体行为>

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A（含 Gherkin 且数值具体）

---

### US-002：……

---

## 4. Implementation Decisions

### 决策记录（Decision Log）

| ID | 决策 | 备选方案 | 选定理由 | 关联 ADR |
|---|---|---|---|---|
| D-001 | <简述> | <备选> | <理由> | <ADR-NNNN 路径 或 N/A> |
| D-002 | … | … | … | … |

> 何时开 ADR：决策同时满足（1）难逆 + （2）没上下文会让未来读者困惑 + （3）有真实权衡。三条缺一不开。

---

## 5. Testing Decisions

### 不开心路径覆盖率

每条 user story 的 Extensions 都需要至少一条对应测试：

| Story | 主流程测试 | Extensions 测试 | 覆盖率 |
|---|---|---|---|
| US-001 | T-001 | T-001a, T-001b | 2/2 |

### Specification by Example 一致性

QA 测试用例与 Gherkin AC **逐字符对齐**——QA 不重写 AC，直接用 Gherkin 跑测试。

实现选项：
- (a) Cucumber/Behave 自动跑 Gherkin（核心流程推荐）
- (b) 手工把 Gherkin 翻译成测试代码（简单流程）
- (c) Gherkin 仅作为 spec，测试代码独立写但 review 对照（项目阻力大时退路）

---

## 6. Out of Scope

### 明确丢弃的需求（不归三桶之一）

会话期间提出但被丢弃的，附理由：

- <需求 X>：丢弃理由 [Overreach / Fallacy / 无法测试 / 用户撤回 / 其他]
- <需求 Y>：……

> 让未来读者知道「我们考虑过 X 但没做」，避免下个 sprint 又有人提同样的事。

---

## 7. Further Notes

### 会话元数据

- 拷问会话日期：YYYY-MM-DD
- 启用方法：<Mom Test, Impact Mapping, 5 Whys, SBE, Cockburn, INVEST, Volere QG> + 可选 <X, Y>
- 会话耗时：约 NN 分钟
- 终审通过轮次：N/3
- 关联 snapshot：[<slug>-snapshot.md](./<slug>-snapshot.md)
- 关联 retro：[skills/req-dev-lite/sessions/YYYY-MM-DD-HHMM-{slug}.md](../../skills/req-dev-lite/sessions/YYYY-MM-DD-HHMM-{slug}.md)

---

## 8. Open Items（桶 C — 未决事项，本地版替代 issue tracker）

每条**必须**有 owner + deadline + 触发上下文 + 目前最佳假设。无 owner 或无 deadline 的条目 **24h 内补全否则砍**，不许长期挂着。

| ID | 标题 | 拦截阶段 | 类型 | Owner | 答复截止 | 目前最佳假设 | 影响范围 | 状态 |
|---|---|---|---|---|---|---|---|---|
| OI-001 | <问题简述> | 阶段 X | 决策待定/数据待查/干系人对齐/技术验证/法律合规/其他 | @user 或 [TBD-by-YYYY-MM-DD] | YYYY-MM-DD | <PRD fallback 假设> | <影响哪几条 story / 哪些 AC> | open / `[resumable]` / resolved / still-open |
| OI-002 | … | … | … | … | … | … | … | … |

**状态字段说明**：
- `open` — 正常未决，等 owner 答复
- `[resumable]` — 用户中途 Stop 时标记，备注会附上"原本卡在阶段 N"。续跑会话结束后必须更新为 `resolved` 或 `still-open`
- `resolved` — 已答复，决策已并入 PRD 主体（同时在 Decision Log 加一行）
- `still-open` — 答复后仍无法收敛，回炉到下次会话

### 已解决决策（仅供历史追溯）

会话期间达成共识但**未触发新 ADR**的决策列在这里：

- **D-901**：<简短描述> — 依据：<阶段几达成>
- **D-902**：……
```

## 模板使用规则

1. **不要省略章节**——即使某段无内容也写 "无" 或 "N/A"，保留章节标题。让未来读者一眼看出"我们考虑过这个维度"。
2. **不要把 Open Items 移到 PRD 开头**——它是末尾，作为「PRD 落地后还欠的债」清单存在。开头放 Problem Statement 是为了让读者先看到 Why。
3. **桶 C 字段缺失视为不合格**——owner=TBD 必须带 deadline；deadline=TBD 必须带 owner。两个都 TBD 的条目不许进 PRD，回阶段 6 重新归类（或丢弃）。
4. **PRD 文件名必须含日期**——`docs/prd/2026-05-18-todo-tag-filter.md` 而不是 `docs/prd/todo-tag-filter.md`。同一主题多次迭代时日期是版本锚点。
