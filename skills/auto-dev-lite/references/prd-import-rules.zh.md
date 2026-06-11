# PRD Import Rules (step 0.5)

详细规则文件。供 `SKILL.md` step 0.5 引用，避免主 SKILL.md 过长。

> **契约版本**：对齐 `req-dev-lite/templates/prd-local.md` @ 2026-06-10（含 8 段标准结构 + 9 列 Open Items 表；additive 新增 frontmatter `gate_mode` / `gate_aggregate` / `gate_confidence` / `gate_report`，旧 PRD 缺省按 `gate_mode: self-reported` 处理）。模板如有变更，**必须**同步更新本文件。

## 何时触发（precondition）

step 0 的前置检查同时满足以下两条 → 自动进入 step 0.5；否则跳过 step 0.5 直接进 step 1：

1. `<target>/local-issues/` 为空（目录不存在或目录内**无 `.md` 文件**——`.imported.md` 不算）
2. `<target>/docs/prd/` 存在且**至少有一份 `*.md`** 文件

任一不满足 → 跳过。例如：
- `local-issues/` 已有文件 → 用户已有 issues，无需 import
- `docs/prd/` 不存在 → 没有 PRD 可 import
- 两者都空 → 既无 issues 也无 PRD，hard-stop 在 step 0 让用户先跑 req-dev-lite

## PRD 源选择规则

`<target>/docs/prd/` 可能有多份历史 PRD：

1. 按文件名前缀 `YYYY-MM-DD` 解析日期，取**最新一份**
2. 若多份同日期（含 `-2` / `-3` 后缀）→ 字母序最后一份 + 在 import log 中明确记录
3. 读 frontmatter：
   - `status: complete`（或无 status）→ 正常 import
   - `status: partial` → 警告 + 继续 import（在 import log 和给用户的总结里**明确告知基于不完整 PRD 启动**）
   - 读 `final_gate_verdict`：若为 `FAIL` 或 `not_reached` → **hard-stop**，告知用户 PRD 终审未通过，不应进入实现阶段
   - 读 `gate_mode`（缺省 = `self-reported`）与 `gate_confidence`：
     - `gate_mode: prd-gate` 且有 `gate_confidence` → escalation 的 `requirement_confidence` 直接用该值
     - `gate_mode: self-reported`（或缺省）→ `requirement_confidence = min(按 verdict 映射的值, 0.85)`；映射：PASS → 0.85，PASS-WITH-OPEN-ITEMS → 0.75（自审 verdict 不享受满分信任，但不至于触发 0.7 软升级——除非 verdict 本身可疑）
     - 把 gate_mode 写进 import log，收尾报告里明确告知用户本次 run 的 verdict 是否经过独立闸门
   - 记录 `session_id` 和 `snapshot` 路径到 import log（审计溯源用）
4. 解析失败（既无 `## 3. User Stories` 也无 `## 8. Open Items` 章节）→ **hard-stop**，不写任何 local-issues

## Bilingual anchors（中英双语锚点，2026-06-10 起）

req-dev-lite 提供两份等价模板：`templates/prd-local.md`（中文）与 `templates/prd-local.en.md`（英文）。
**章节编号、US-NNN 标题形状、story 字段顺序、Open Items 列序完全一致**，仅自然语言不同。
解析时下表两列锚点等价，混用（如中文 PRD 含英文字段名）也必须接受：

| 中文锚点 | English anchor |
|---|---|
| `## 3. User Stories（桶 A）` | `## 3. User Stories (Bucket A)` |
| `### Outcome Metrics（桶 B）` | `### Outcome Metrics (Bucket B)` |
| `## 8. Open Items（桶 C ...）` | `## 8. Open Items (Bucket C ...)` |
| `**作为** ... **我希望** ... **以便** ...` | `**As** ... **I want** ... **so that** ...` |
| `**追溯**：Why=..., Who=..., How=...` | `**Traceability**: Why=..., Who=..., How=...` |
| `**Extensions（不开心路径）**` | `**Extensions (unhappy paths)**` |
| `**三桶归属**` | `**Bucket assignment**` |
| Open Items 列 `Owner` / `答复截止` | `Owner` / `Deadline` |

其余锚点（`### US-NNN[:：]`、`**INVEST**`、`**Gherkin AC**`、`**Volere QG**`、frontmatter 字段名）本身语言中立。

## PRD 章节锚点（严格匹配 templates/prd-local.md）

这是 **req-dev-lite ↔ auto-dev-lite 的核心契约**。解析时按下表精确匹配：

| 锚点 regex | 内容来源 | 用途 |
|---|---|---|
| `^## 3\. User Stories.*$` | 桶 A（user stories） | 转 `local-issues/*.md` ready |
| `^### US-(\d{3})[:：]\s*(.+)$` | 单条 user story 的标题 | 提取 ID + title（**冒号可能是全角 `：` 或半角 `:`**） |
| `^### Outcome Metrics.*$`（在 `## 1. Problem Statement` 段内） | 桶 B（metric 表） | 追加进 PROJECT_CONTEXT.md |
| `^## 8\. Open Items.*$` | 桶 C（open items 表） | 转 `local-issues/*-OI-*.md` blocked |
| `^## 5\. Testing Decisions.*$` | SBE 实现选项 (a/b/c) | 提取 + 追加进 PROJECT_CONTEXT.md（覆盖默认 pytest）|
| `^## 2\. Solution.*$` | 候选方案 + 暂不考虑 | 拼进每条 user story body 作"上下文段" |
| `^## 4\. Implementation Decisions.*$` | Decision Log + ADR 链接 | 拼进每条 user story body 作"上下文段" |
| `^## 6\. Out of Scope.*$` | 明确丢弃的需求 | **不 import**，只在 import log 记录"已知 N 条 out-of-scope" |

锚点的 `\.` 是必需的——模板都带编号前缀 `1.` `3.` `5.` `8.` 等。

## 三桶到 local-issues 的映射（修正版）

| PRD 章节 | 桶 | 落点 | issue status |
|---|---|---|---|
| `## 3. User Stories（桶 A）` 下的 `### US-NNN：<title>` | A | `local-issues/00N-{slug}.md`（id 字段 = `US-NNN`） | `ready` |
| `## 1. Problem Statement` 下的 `### Outcome Metrics（桶 B）` 表 | B | `<target>/PROJECT_CONTEXT.md` 的 `## Reference Metrics (from PRD)` 段（lazy 创建） | N/A |
| `## 8. Open Items（桶 C）` 9 列表中每一行 | C | `local-issues/00N-OI-{NNN}-{slug}.md`（id 字段 = `OI-NNN`，**保留 PRD 原 ID**） | `blocked` |
| `## 5. Testing Decisions`（实现选项 (a/b/c)） | 框架配置 | `PROJECT_CONTEXT.md` 的 `## Testing` 段 | N/A |

**文件编号 `00N` 由 import 顺序决定，issue ID 由 PRD 原 ID 决定。两者解耦。**

例：PRD 有 8 个 US（编号 US-001~US-008）和 3 个 Open Item（编号 OI-001~OI-003）→ 生成：
- `001-{slug-of-US-001}.md`（id: US-001）
- `002-{slug-of-US-002}.md`（id: US-002）
- ...
- `008-{slug-of-US-008}.md`（id: US-008）
- `009-OI-001-{slug}.md`（id: OI-001, status: blocked）
- `010-OI-002-{slug}.md`（id: OI-002, status: blocked）
- `011-OI-003-{slug}.md`（id: OI-003, status: blocked）

## 桶 A → User Story issue 文件格式

PRD 模板里每条 user story 的 body 包含 6 个明确字段（按出现顺序）：

```
**作为** <角色>，**我希望** <动作>，**以便** <价值>。
**追溯**：Why=<OKR-XX>, Who=<角色>, How=<X → Y>
**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T
**Gherkin AC**（必须含真实数值）：
  ```gherkin
  Scenario: ...
  ```
**Extensions（不开心路径）**：1a. ... / 2a. ...
**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word
**三桶归属**：桶 A
```

生成的 issue 文件：

```markdown
---
id: US-001                                    # 保留 PRD 原 ID
title: <从 ### 标题提取，去掉 "US-NNN：" 前缀>
status: ready
tier: medium                                  # 默认 medium；step 3 会按 planned_paths 重评
depends_on: []                                # 见下方 depends_on 提取规则
acceptance_tests: null                        # step 4 写完测试时填
run_id: null                                  # step 2 跑起来时填
originated_from: prd_user_story
prd_source: docs/prd/YYYY-MM-DD-{slug}.md     # 溯源链
prd_session_id: <PRD frontmatter 的 session_id>  # 追溯到拷问会话
imported_at: YYYY-MM-DD HH:MM
---

# US-001: <title>

<整段 user story body 从 PRD 直拷贝，6 个字段一字不改>

---

## Context (from PRD § 2 Solution)

<复制 PRD 的 `## 2. Solution` 段，让 step 4 写实现时知道候选方案和被排除的方案>

## Decisions (from PRD § 4 Implementation Decisions)

<复制相关行——只复制 Decision Log 中 "关联 ADR" 列引用本 US 的行；无关联的整段省略>
```

**硬规则**：
- 6 字段 body 必须**逐字拷贝**，不重写、不简化、不补全。
- `## Context` 段：`## 2. Solution` 整段拷过来。如果 PRD 没这段则省略。
- `## Decisions` 段：仅当 PRD 的 Decision Log 有引用本 US 的行时拼接；否则省略。

**`depends_on` 提取规则**（按优先级）：
1. user story body 中显式写 `**前置**：US-NNN, US-MMM` → 提取
2. user story body 中显式写 `Depends on US-NNN` → 提取
3. 无显式声明 → `[]`

（PRD 模板当前不强制 user story 写依赖，所以多数情况下 `depends_on: []`。如果 req-dev-lite 后续扩展强制声明，本规则需更新。）

## 桶 C → Open Item issue 文件格式

PRD 的 Open Items 表 9 列：

```
| ID | 标题 | 拦截阶段 | 类型 | Owner | 答复截止 | 目前最佳假设 | 影响范围 | 状态 |
```

每行生成一份 issue。状态字段为 `[resumable]` 的特殊处理见下方。

```markdown
---
id: OI-001                                    # 保留 PRD 原 ID
title: <从"标题"列提取>
status: blocked                               # 永远 blocked，不进入 step 1 自动队列
tier: medium
depends_on: []
acceptance_tests: null
run_id: null
originated_from: prd_open_item
prd_source: docs/prd/YYYY-MM-DD-{slug}.md
prd_open_item_status: open                    # 从 PRD 状态列读：open / [resumable] / resolved / still-open
intercepted_at_stage: <拦截阶段 列值>
item_type: <类型 列值>
owner: <Owner 列值>
deadline: <答复截止 列值>
affected_scope: <影响范围 列值>
imported_at: YYYY-MM-DD HH:MM
---

# OI-001: <title>

## Origin

Imported from PRD `## 8. Open Items` table on YYYY-MM-DD HH:MM. **Needs human resolution before auto-dev-lite can process.**

PRD 表行原值（逐字保留，便于核对）：

- **拦截阶段**：<value>
- **类型**：<value>
- **Owner**：<value>
- **答复截止**：<value>
- **目前最佳假设**：<value>
- **影响范围**：<value>
- **PRD 中的状态**：<value>

## How to unblock

1. **首选**：与 owner 解决"目前最佳假设"中的不确定性 → 把该决策升级为 user story。在 PRD `## 3. User Stories` 段补一条 `### US-NNN：...` 含完整 INVEST + Gherkin AC → 删除 PRD 中本 Open Item 行 → re-import（见 Re-import 节）。
2. **次选**：直接就地修改本文件：
   - 把 `status:` 从 `blocked` 改为 `ready`
   - 把 `id:` 从 `OI-NNN` 改为合适的 `US-NNN`
   - 在 body 补 Gherkin AC（按 user story 模板）
   - 删除 `## Origin` 段
3. **打回**：若与 owner 沟通后判定本项无法解决或不再需要 → 把 PRD 中本行的"状态"列改为 `resolved` 或砍掉本行 → 删除本 issue 文件。
```

**状态字段特殊处理**：

- PRD 中状态 = `open`（默认）→ 正常 import 为 `status: blocked` 的 issue
- PRD 中状态 = `[resumable]` → 同样 import，但 issue body 顶部加**醒目警告**：「⚠️ 此 Open Item 在 PRD 阶段被用户中途 Stop，标记为 resumable。优先续跑 req-dev-lite 而不是直接转 user story。」
- PRD 中状态 = `resolved` 或 `still-open` → **不 import**（已经在 PRD 主体或新 PRD 解决了）

## 桶 B → PROJECT_CONTEXT.md 写入规则

PRD 中 Outcome Metrics 表格式：

```
| Metric | 当前 | 目标 | 测量方法 |
|---|---|---|---|
| <指标 1> | X | Y | <描述> |
```

### `PROJECT_CONTEXT.md` 不存在 → lazy 创建

```markdown
# Project Context

<!-- Auto-created by auto-dev-lite step 0.5 on YYYY-MM-DD. User can add more sections freely. -->

## Reference Metrics (from PRD)

**Source**: docs/prd/YYYY-MM-DD-{slug}.md (imported YYYY-MM-DD HH:MM)

| Metric | Baseline | Target | Measurement |
|---|---|---|---|
| <指标 1> | X | Y | <描述> |
| <指标 2> | X | Y | <描述> |
```

### `PROJECT_CONTEXT.md` 已存在

按以下顺序：

1. `grep '## Reference Metrics'` 检查是否已有该段
2. **若已有**：在表格末尾追加新行（不删已有的），并在追加块前打 source 注释：
   ```markdown
   <!-- Appended from docs/prd/YYYY-MM-DD-{slug2}.md on YYYY-MM-DD HH:MM -->
   | <new metric> | ... | ... | ... |
   ```
3. **若无**：在文件末尾追加完整 `## Reference Metrics (from PRD)` 段

**绝对不允许**：修改 PROJECT_CONTEXT.md 中用户自己写的其他段落（如 `## Testing` `## Deployment` 等）。

## Testing Decisions → PROJECT_CONTEXT.md `## Testing` 段

PRD 的 `## 5. Testing Decisions` 含三个互斥实现选项：

- (a) Cucumber/Behave 自动跑 Gherkin
- (b) 手工把 Gherkin 翻译成测试代码
- (c) Gherkin 仅作为 spec，测试代码独立写但 review 对照

读 PRD 时检测哪个选项被勾选（搜寻文本中 `(a)` / `(b)` / `(c)` 后的描述句中是否含"采用 / 选定 / 使用"等动词；若不明确则默认 (b)）。

写入 `PROJECT_CONTEXT.md` 的 `## Testing` 段（lazy 创建或追加）：

```markdown
## Testing

<!-- Imported from PRD `## 5. Testing Decisions` on YYYY-MM-DD HH:MM -->

- **SBE 实现选项**：(b) 手工把 Gherkin 翻译成 pytest 测试代码
- **测试命令**：`pytest --tb=short -q`（默认；用户可覆盖）
- **测试目录**：`tests/`
```

若 PRD 选 (a) Cucumber → 测试命令改为 `behave`（或 `cucumber-js`，按项目语言）；若 (c) → 维持 pytest 但在 issue body 加注「Gherkin 仅作为 spec 参考」。

**SKILL.md step 5 已有规则**：读 `PROJECT_CONTEXT.md` 的"测试命令"字段覆盖默认 pytest。本扩展只是确保 step 0.5 把信息正确填进去。

## `## 6. Out of Scope` 处理

**不 import** 任何丢弃需求。只在 import log 里记一行：

```
- Out of scope: PRD 列出 N 条明确丢弃的需求（详见 docs/prd/{slug}.md § 6）
```

理由：丢弃需求是给人读的（避免日后重复提议），不需要进 issue tracker。

## Idempotency 和冲突处理

step 0.5 的设计前提是 `local-issues/` 为空——这是 step 0 的触发条件。但工程上仍要防御几种边界：

| 场景 | 行为 |
|---|---|
| 触发 step 0.5 时发现 `local-issues/` 有同 `US-NNN` 或 `OI-NNN` ID 的文件 | **hard-stop**：报告"已存在 ID 冲突"，列出冲突 ID，让用户先 archive 或 delete |
| `<target>/docs/prd/` 有 ≥2 份 PRD | 取最新一份（按文件名日期）；在 import log 明确记录"忽略了 N 份旧 PRD：<列表>" |
| PRD 没有 `## 3. User Stories` 章节（全是 Open Items） | 桶 A 跳过；只写桶 C；在总结里告知用户 |
| PRD 没有 `## 8. Open Items` 章节 | 桶 C 跳过；只写桶 A；不报错 |
| PRD 没有 Outcome Metrics（表为空或缺章节） | 桶 B 跳过；不写 PROJECT_CONTEXT.md 的 Metrics 段；不报错 |
| PRD 没有 `## 5. Testing Decisions` | 不写 Testing 段；step 5 跑默认 pytest |
| PRD `final_gate_verdict: FAIL` 或 `not_reached` | **hard-stop**：终审未过，不应进实现阶段 |
| PRD 三桶全为空 | **hard-stop**：报告"PRD 没有可 import 的内容"，建议用户重新跑 req-dev-lite |

## Import Log

每次 step 0.5 成功完成后，写一份 `<target>/local-issues/.imported.md`（已存在则追加）：

```markdown
# Import Log

## YYYY-MM-DD HH:MM:SS

- **Source PRD**: docs/prd/YYYY-MM-DD-{slug}.md
- **PRD frontmatter status**: <complete | partial>
- **PRD final_gate_verdict**: <PASS | PASS-WITH-OPEN-ITEMS>
- **PRD session_id**: YYYY-MM-DD-HHMM-{slug}（→ skills/req-dev-lite/sessions/）
- **PRD snapshot**: docs/prd/{slug}-snapshot.md
- **桶 A (User Stories)**: N 条
  - 001-<slug1>.md (US-001)
  - 002-<slug2>.md (US-002)
  - ...
- **桶 B (Outcome Metrics)**: M 条 → PROJECT_CONTEXT.md `## Reference Metrics`
  - <metric 1 name>
  - <metric 2 name>
- **Testing Decisions**: 选 (b) 手工 pytest → PROJECT_CONTEXT.md `## Testing`
- **桶 C (Open Items)**: K 条 (status: blocked)
  - 00X-OI-001-<slug1>.md (OI-001, prd_status: open)
  - 00Y-OI-002-<slug2>.md (OI-002, prd_status: [resumable]) ⚠️
- **Out of scope**: PRD 列出 P 条丢弃需求（仅记录，未 import）
- **跳过 PRD 旧版本**: <列表，若多份>
- **警告**: <如 partial PRD 警告 / resumable OI 警告>
```

## 给用户的 step 0.5 总结输出

import 完成后**必须**打印总结（在进入 step 1 前）：

```
✅ PRD imported: docs/prd/2026-05-19-crm-pilot.md
   桶 A (ready):     8 user stories  → 001-* ~ 008-*
   桶 B (metrics):   2 metrics       → PROJECT_CONTEXT.md § Reference Metrics
   Testing:          (b) pytest      → PROJECT_CONTEXT.md § Testing
   桶 C (blocked):   3 open items    → 009-OI-001-* ~ 011-OI-003-*
   Out of scope:     5 条丢弃需求（仅在 PRD 记录，未 import）

   ⚠️  PRD frontmatter status = partial. 部分需求可能未拷问完整。
       建议跑完后回头继续 req-dev-lite。

Proceeding to step 1 (select next ready issue)...
```

## 反模式自检（step 0.5 特有）

- ❌ **不许在桶 B/C 上加 `status: ready`** — 它们没有 Gherkin AC，跑了一定挂
- ❌ **不许在 import 时改写 PRD body** — 6 字段 user story body 必须逐字拷贝
- ❌ **不许 PRD 解析失败时写 partial local-issues** — 全成功才写，否则 hard-stop
- ❌ **不许覆盖已存在的同 ID issue** — 冲突即 hard-stop
- ❌ **不许动 PROJECT_CONTEXT.md 中 Reference Metrics / Testing 以外的段落** — 用户的其他配置神圣不可侵犯
- ❌ **不许在 step 0.5 跑测试 / 写代码** — 只做格式转换
- ❌ **不许吞掉 `final_gate_verdict: FAIL` 的 PRD** — 终审未过的 PRD 不应进实现阶段

## Re-import（PRD 有更新想再 import 一次）

step 0.5 的 trigger 是 "`local-issues/` 为空"，所以默认情况下 PRD 更新后**不会**自动 re-import。手动路径：

1. 把已 done 的 issue 文件移到 `local-issues/done/`（保留历史）
2. 把 blocked 的 OI 文件按需要处理（删除已废弃的、保留仍待解的）
3. 重启 auto-dev-lite → step 0 检测 local-issues/ 空 → 自动 import 新 PRD

**Future extension**（本期不实现）：加 explicit trigger 短语 "re-import PRD" 强制 re-import，并按 `prd_source` + `id` 做 diff，只追加新增 US，跳过已存在 ID。

## 与 req-dev-lite 的契约（interface contract）

本文件的解析规则**强依赖** `skills/req-dev-lite/templates/prd-local.md` 的结构。下列字段是 interface，**改 PRD 模板必须同步本文件**：

### Interface 字段（不能随意改）

**Frontmatter**：
- `status: complete | partial`（auto-dev-lite 据此决定是否警告）
- `final_gate_verdict: PASS | PASS-WITH-OPEN-ITEMS | FAIL | not_reached`（决定是否 hard-stop）
- `session_id`（审计溯源）
- `snapshot`（审计溯源）

**章节锚点**（H2 必须带编号 + 中文括注）：
- `## 1. Problem Statement`（含 `### Outcome Metrics（桶 B）` 子段）
- `## 2. Solution`
- `## 3. User Stories（桶 A）`（含 `### US-NNN：<title>` 子段）
- `## 4. Implementation Decisions`
- `## 5. Testing Decisions`
- `## 6. Out of Scope`
- `## 8. Open Items（桶 C — 未决事项，本地版替代 issue tracker）`（9 列表）

**user story 内部字段**（按出现顺序）：
1. `**作为** ... **我希望** ... **以便** ...`
2. `**追溯**：Why=..., Who=..., How=...`
3. `**INVEST**`
4. `**Gherkin AC**`
5. `**Extensions（不开心路径）**`
6. `**Volere QG**`
7. `**三桶归属**`

**Open Items 表 9 列顺序**：
`ID | 标题 | 拦截阶段 | 类型 | Owner | 答复截止 | 目前最佳假设 | 影响范围 | 状态`

### 改 PRD 模板时的同步流程

1. 在 `skills/req-dev-lite/templates/prd-local.md` 改完
2. 在 `skills/req-dev-lite/SKILL.md` 的 "下游消费者" 段加变更说明
3. 同步改本文件（`auto-dev-lite/references/prd-import-rules.md`）的"PRD 章节锚点"和"三桶映射"两节
4. 更新本文件顶部的 "**契约版本**" 行为新日期
5. 跑一遍历史 PRD（如 `crm_demo`）做 regression：能否仍正确 import

当前对齐版本：**req-dev-lite 2026-06-10 lite 版**。
