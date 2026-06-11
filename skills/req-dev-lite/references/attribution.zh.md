# 引用源与安全审查

req-dev skill **不引入任何可执行代码**，只引用以下来源的**概念、句式、模板**。每条引用都列出：源、内容、修改、安全审查结论。

最后审查日期：2026-06-10（全部外部源经 web 复核）

---

## 引用清单

### 1. Rob Fitzpatrick — *The Mom Test*（书，2013）

- **引用内容**：三规则（谈生活/问过去/少说多听）、禁用问句清单、强制问句模板
- **使用位置**：`SKILL.md` 阶段 2、`references/question-bank.md` §1-2
- **我的修改**：中文化；补充「以后/将来」等中文未来时禁用；新增「为什么至今没修」量化痛苦问句
- **安全审查**：
  - ☑ 无外链 / 无脚本 / 无可执行代码
  - ☑ 无 PII（书中举例都是公开案例：Slack、Buffer 等）
  - ☑ 版权：方法学概念非受版权保护，且本 skill 用作教学/工作流，不复制原文段落

---

### 2. Gojko Adzic — *Impact Mapping*（书，2012）+ *Specification by Example*（书，2011）

- **引用内容**：Impact Mapping 四层（Why/Who/How/What）；SBE 哲学「写不出失败的具体例子，需求就没成熟」；Gherkin Given-When-Then 格式
- **使用位置**：`SKILL.md` 阶段 1 + 4；`references/methods.md` §2 + §4；`templates/user-story.md`
- **我的修改**：把 Impact Mapping 改为 LLM 对话内的逐步问句；Gherkin 例子用人民币/中文场景
- **安全审查**：
  - ☑ 无外链 / 无脚本
  - ☑ Gherkin 语法属公开标准（Cucumber 项目 MIT）
  - ☑ 方法学概念非受版权保护

---

### 3. Toyota Production System / Sakichi Toyoda — 5 Whys

- **引用内容**：连问 5 层 why 的拷问模板
- **使用位置**：`SKILL.md` 阶段 2.5；`references/question-bank.md` §4
- **我的修改**：与 Ohara 2025 论文的「LLM 拷问 + 确定性验证」分工思路结合；明确 5 Whys 落地为 Ulwick outcome 句式
- **安全审查**：
  - ☑ 公有领域概念
  - ☑ 加了 Minoura 批评（5 Whys 在复杂系统的局限），不盲信

---

### 4. Alistair Cockburn — Use Case Extensions（2000s）

- **引用内容**：主流程 + Extensions（每步失败/超时/并发分支）的枚举方法
- **使用位置**：`SKILL.md` 阶段 4.5；`references/methods.md` §5；`references/question-bank.md` §5
- **我的修改**：补充并发/部分成功/用户取消等更现代的失败模式
- **安全审查**：☑ 方法学，无代码

---

### 5. Suzanne & James Robertson — Volere Requirements Specification Template

- **引用内容**：Quality Gateway 4 问（可测试 / 可追溯 / 无方案语言 / 无 weasel word）
- **使用位置**：`SKILL.md` 阶段 5；`references/quality-gateway.md` §Volere
- **我的修改**：只取 Quality Gateway 这一个机制（4 个 testpoint），不引入也不分发完整 Volere 模板原文
- **版权声明（按 Volere 要求保留）**：概念引自 the Volere Requirements Specification Template, copyright © 1995–2019 the Atlantic Systems Guild Limited（volere.org）。模板本身的商业性销售/分发需 Guild 书面许可；本 skill 不复制模板任何段落，仅以自有文字实现 Quality Gateway 检查思想并注明出处。
- **安全审查（2026-06-10 web 复核）**：
  - ☑ volere.org 条款：模板可为需求工作修改/拷贝，须保留版权声明；不得未经许可作商业销售
  - ☑ 本 skill 不分发模板原文，仅引用概念 + 注明出处 → 合规

---

### 6. Bill Wake — INVEST（2003，文章）

- **引用内容**：六字检查（Independent / Negotiable / Valuable / Estimable / Small / Testable）
- **使用位置**：`SKILL.md` 阶段 4；`templates/user-story.md`
- **安全审查**：☑ 公共方法学概念

---

### 7. Tony Ulwick — Outcome-Driven Innovation outcome 句式

- **引用内容**：「最小化/最大化 [动词][对象][约束]」句式
- **使用位置**：`SKILL.md` 阶段 2.5（5 Whys 落点）；`references/methods.md` §9
- **安全审查**：☑ 句式属公共方法，未引用 Strategyn 专属调研流程

---

### 8. carollrollroll/prd-skill on GitHub

- **GitHub**：https://github.com/carollrollroll/prd-skill
- **License**：**MIT**（2026-06-10 web 复核确认；此前 2026-05-10 用户人工确认）
- **引用内容**：7 个审查标签（Contradiction / Gap / Fallacy / Redundancy / Dangling / Overreach / Unowned）
- **使用位置**：`SKILL.md` 阶段 5；`references/quality-gateway.md` §7 标签审查
- **我的修改**：标签名保留原文；判定标准和修复方法是我重写的；中文判定问句
- **安全审查**：
  - ☑ **LICENSE 已由用户确认通过**（2026-05-10）。当前引用方式（仅借用 7 个英文标签名 + 自写判定）属合理使用。
  - ☑ 无代码 copy / 无 prompt 原文 copy
  - ☑ 无外链嵌入到 skill 内

---

### 9. wiveu/prd-skill-agent on GitHub

- **GitHub**：https://github.com/wiveu/prd-skill-agent
- **License**：**MIT**（2026-06-10 web 复核确认）
- **引用内容**：「PRD 是 decision log 不是 wish list」的设计哲学（README 原句：A good PRD is not a wish list — it's a decision log）
- **使用位置**：影响 `SKILL.md` 阶段 7 + `templates/open-items.md`
- **我的修改**：仅借用核心理念，没有复制其 question-bank 或 SKILL.md 原文
- **安全审查**：
  - ☑ **LICENSE 已由用户确认通过**（2026-05-10）
  - ☑ 仅借用哲学/结构概念

---

### 10. C.A. O'Hara — Agentic Architecture Mediation for LLM Assistants（TechRxiv preprint，2025-12）

- **来源（2026-06-10 复核更正）**：TechRxiv preprint, DOI 10.36227/techrxiv.176583345.56962463（数据集另见 IEEE DataPort）。**注意：此前误标为 "IEEE Software 2025"，现更正为 preprint**——引用时请按 preprint 对待，结论尚未经期刊同行评审定稿。
- **引用内容**：「LLM 负责拷问对话，验证由确定性规则做」的分工思路；multi-agent 5 Whys 拦截 solution-jumping
- **结论强度（更正措辞）**：论文**报告**在 6 个行业反模式上 100% 检出 solution mismatch（平均 $0.01/session）——样本量小，是支持性证据而非"证明"
- **使用位置**：`SKILL.md` 阶段 2.5 设计依据；`methods.md` §3 注释；`question-bank.md` §4
- **安全审查**：☑ 学术 preprint 方法学引用，已注明来源与证据强度

---

## 安全审查总结

| 检查项 | 状态 |
|---|---|
| 无外部 URL 嵌入到 skill 文件中（除 attribution.md 自身的 GitHub 链接） | ☑ |
| 无可执行代码（shell / python / js） | ☑ |
| 无可加载远程内容的指令 | ☑ |
| 无对其他 repo 的 git submodule / git clone 引用 | ☑ |
| 无 PII / 商业敏感数据 | ☑ |
| 无 API key / secret 占位符 | ☑ |
| 所有引用源都标注 | ☑ |
| 商业许可证 | ☑ 用户已确认通过（2026-05-10） |

## 用户行动项

☑ **已完成 2026-05-10**：用户已确认 carollrollroll/prd-skill 与 wiveu/prd-skill-agent 的许可证状态，当前引用方式 OK，无需调整。

后续如这两个 repo 的 LICENSE 发生变化（例如改为 GPL/AGPL），请回头复审本文件相关条目。
