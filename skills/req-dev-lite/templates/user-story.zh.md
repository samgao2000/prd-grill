# User Story 模板

> Fork 自 `skills/req-dev/templates/user-story.md`（2026-05-18）。lite 版的 INVEST / Gherkin / Cockburn / Volere 自检规则与 full 版没有差异；只有"三桶归属"段的桶 C 字段说明不同（lite 用 OI-NNN 表格编号，full 用 issue 链接）。
>
> 两边模板更新时**需手动同步**。若两边漂移，以本文件为准（lite 视角）。

每条 user story 用这个格式。带的注释说明每段为什么必要——保留这些注释直到用户已经熟练。

```markdown
## US-NNN：[简短标题]

<!-- 标题：动宾结构，描述用户能做什么。例：「查看累计可用积分」 -->

### Story
作为 <具体角色>，
我希望 <动作 + 对象>，
以便 <可观察的价值>。

<!-- 角色必须具体到岗位，不是「用户」。
     价值必须可观察，不是「方便」「更好」。
     例 ✓：作为首次开户的 18-25 岁用户，我希望在身份验证失败时看到具体哪一步出错，以便我能立即修正而不是重新走完整流程。
     例 ✗：作为用户，我希望操作更方便，以便更好体验。
-->

### 追溯（Traceability）
- 上游 Why：[阶段 1 钉死的业务目标编号 / OKR-XX-X]
- 上游 Who：[阶段 1 钉死的角色]
- 上游 How：[期望行为改变：X → Y]

<!-- 不能填 → 这条 story 越界（[Overreach]）或追溯断了，回阶段 1 -->

### INVEST 检查（30 秒过审）
- [ ] Independent — 不依赖其他未交付 story
- [ ] Negotiable — 实现方式还可以谈
- [ ] Valuable — 对追溯的 Who 有可见价值
- [ ] Estimable — 工程能估出工作量
- [ ] Small — 一个 sprint 内可完成
- [ ] Testable — 有可验证完成标准

### 验收标准（Gherkin，至少 1 个例子，必须含真实数值）

```gherkin
Scenario: [描述场景，名词性]
  Given [初始状态，具体到字段值]
    And [其他前置条件]
  When [用户动作，具体到点击/输入/调用]
  Then [可观察结果，具体到展示文字/数据变化/状态码]
    And [其他可观察结果]
```

<!-- 必须含真实数值。
     例 ✓：Given 用户余额为 ¥100.00 When 提现金额 ¥150.00 Then 显示「余额不足，可提现金额 ¥100」
     例 ✗：Given 用户余额不足 When 用户提现 Then 提示余额不足
-->

### 不开心路径（Cockburn Extensions）

主流程步骤：
1. [步骤]
2. [步骤]
...

Extensions：
- 1a. [步骤 1 失败/超时/取消] → [具体行为]
- 1b. [其他分支] → [具体行为]
- 2a. [步骤 2 失败] → [具体行为]
...

<!-- 漏一个 → [Gap]，回阶段 2 -->

### Volere QG 自检
- [ ] 可测试 — QA 能直接据此写测试用例
- [ ] 可追溯 — 上游 Why/Who 已填
- [ ] 无方案语言 — 没说 Redis/React/某具体技术
- [ ] 无 weasel word — 没说 user-friendly / fast / 友好 / 高性能 等

### 三桶归属
- [ ] 桶 A：本 story 有 Gherkin AC（含真实数值）
- [ ] 桶 B：有 outcome metric 关联（在 PRD 主文档）
- [ ] 桶 C：本 story 依赖未决事项（**lite 版**：列 Open Items 表格的 OI-NNN 编号，不是 issue 链接）

<!-- 三桶都不归 → 不要进 PRD -->
```
