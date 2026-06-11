# req-dev-lite sessions/

每次 req-dev-lite 会话结束后（阶段 8）自动写一份 retrospective 到这个文件夹。

## 用途

- 给 retro 聚合提供数据（≥3 次同向信号后才提议改 SKILL.md）
- 给人类 review 历史决策与反模式趋势
- 给团队跨成员协作（git track 后多机器多会话能汇总）

## 与 req-dev full 版的关系

`skills/req-dev/sessions/` 和本文件夹是**两套独立**的 retro 池子，互不混读。

- 跑 `req-dev`（full） → 写到 `skills/req-dev/sessions/`
- 跑 `req-dev-lite`（本 skill） → 写到 `skills/req-dev-lite/sessions/`

`req-dev-retro` skill 已扩展为**同时读两个 sessions/**，但信号池**按 skill 来源分**：
- lite session 的信号 → 只改 lite 的 SKILL.md / references / templates
- full session 的信号 → 只改 full 的 SKILL.md / references / templates
- 不交叉污染。方法论改动想跨 skill 传播需用户在 retro 时显式确认（diff 会单独提议每个 skill 各一份）。

## 不是用途

- ❌ 不是原始转录存档（隐私 + git 体积）
- ❌ 不是任务追踪器（任务用 PRD 末尾 Open Items 表格）
- ❌ 不是 agent 自动改 skill 的依据（必须经 retro skill 人审）

## 文件命名

```
YYYY-MM-DD-HHMM-{slug}.md
```

- `slug` 用 kebab-case，简写 PRD 主题（例：`todo-tag-filter`）
- 时间用会话**开始**时间（不是结束时间，方便排序）
- 续跑会话用**新的开始时间**命名（不是原 slug 时间），并在 frontmatter `resumed_from` 字段填原 session_id

## 模板

见 `_template.md`。每个新会话**复制**该模板填写，不要直接改模板。

## 改进闭环

```
req-dev-lite 跑完 → 阶段 8 自动写 retro → sessions/*.md
                                              ↓
                              （N 个会话累积）
                                              ↓
用户手动触发 retro skill（指定本 sessions/ 路径） → 聚合 ≥3 次同向信号
                                              ↓
                                  输出 diff 提议给用户
                                              ↓
                  用户 yes → 应用到 SKILL.md / templates
                  用户 no  → 写进 retro 的 proposals-log.md 拒绝段（避免重复提议）
                  用户改  → 应用修改版
```

## git 策略

本文件夹 **track**（不进 .gitignore）。原因：
- 多机器多会话能汇总
- 团队成员能看到彼此的会话反馈
- 文件只含结构化数据，无 PII 风险

如果某次会话含敏感信息（公司机密/客户名/合同金额），retro 写入时**应**打码或省略，而不是把整个文件加入 .gitignore。
