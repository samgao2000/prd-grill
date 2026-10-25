---
name: prd-gate
description: >
  独立 PRD 质量闸门 — req-dev「spec produced」与 auto-dev「build started」之间的
  可测量关卡。对 PRD 按 11 维度（Volere 4 问 + 7 标签）打分: 确定性检查 +
  fresh-context LLM judge, 输出 .gate.json (机器可读) + .gate.md (人读) +
  verdict (PASS / PASS-WITH-OPEN-ITEMS / FAIL) + requirement_confidence
  (喂给 auto_dev escalation M5, 阈值 0.7)。
  Triggers: "跑 prd-gate", "给这个 PRD 打分", "gate 这个 PRD", "score this PRD",
  "PRD 质量检查", "/prd-gate"。
disable-model-invocation: false
metadata:
  origin: prd-grill
  author: Sam Gao
  homepage: https://github.com/samgao2000/prd-grill
---

# prd-gate — 独立 PRD 质量闸门

## 何时触发（When to Activate）

- `docs/prd/` 里已有 PRD，有人准备据此规划或开发。先过闸门，verdict 决定能否开工。
- 用户说「跑 prd-gate」「给这个 PRD 打分」「gate 这个 PRD」「/prd-gate」。
- req-dev-lite 阶段 7 到达落地步骤（装有 `prd_gate` 时强制）。
- PRD frontmatter 写着 `gate_mode: self-reported`，或缺少 `final_gate_verdict`——它只被作者模型自评过。
- **不要**在写 PRD 的那个会话里运行判官。判官必须是全新上下文的子智能体（在 ECC 中即 `prd-judge` agent）；复用写作上下文会无声地毁掉闸门。

## 为什么存在

req-dev 阶段 5 的终审是**作者模型在同一对话里给自己打分**——系统性偏向 PASS。
本闸门把同一套判定标准（单一锚点：`skills/req-dev/references/quality-gateway.md`）
拆成两层独立执行：

1. **确定性层**（Python，零 LLM）：Gherkin 真实数值、追溯锚点 `Why=/Who=`、
   weasel-word 词表、Cockburn Extensions 存在性、Open Items owner+deadline、
   核心 Why/Who 一票否决。可复现、可回归测试。
2. **独立 judge 层**（fresh-context LLM）：Contradiction / Gap / Fallacy /
   Redundancy / Dangling / Overreach / Solution-language——需要领域判断的维度。
   judge **只看 PRD 文件 + 锚点文档**，不看引出 PRD 的对话。

合并规则：**严判优先**——两层都打分的维度取 `min()`（同 plan-eval ADR-002 精神）。

## 调用方式

### 在 Cowork / Claude Code 会话内（推荐路径）

Bash 子进程内嵌套 SDK 调用会被 `CLAUDECODE=1` 拒绝，所以 judge 层由
fresh-context subagent 完成：

1. `python -m prd_gate score --prd docs/prd/<file>.md`
   → 输出确定性层报告 + `<file>.judge-tasks.json`（exit 2 = 已经 FAIL，先回炉再说）
2. 起一个 **fresh-context subagent**，输入**只有**：PRD 文件 + `skills/req-dev/references/quality-gateway.md` + judge-tasks.json。
   **禁止**给它本会话对话历史。它按 result_schema 写 `<file>.judge-results.json`。
3. `python -m prd_gate merge --prd docs/prd/<file>.md --judge-results <file>.judge-results.json`
   → 最终 `.gate.json` / `.gate.md`，含 verdict + requirement_confidence + frontmatter patch。
4. 把 frontmatter patch 抄进 PRD 开头（值不许手改）。

### 其他 agent（Cursor、Windsurf、Codex CLI、Gemini CLI 等）

judge-tasks/merge 流程厂商中立：任何够格的 LLM 都能当 judge。你唯一要自己保证的
是**上下文隔离**——开一个全新会话，只喂三个文件（PRD、锚点、judge-tasks.json），
把回答存为 `<prd>.judge-results.json`（裸 JSON；容忍代码栅栏和前后缀文字），再跑
`merge`。复用写 PRD 的那个会话会无声地摧毁闸门的独立性。

### 终端直跑（带 API key）

```bash
ANTHROPIC_API_KEY=... python -m prd_gate score --prd docs/prd/x.md --judge api
```

CI / 测试: `PRD_GATE_MOCK=1`（judge 层返回全过 stub，只测管道）。

## 输出契约

- `<prd>.gate.json` — schema `prd-gate/v1`：per-dimension score (0..1) + 引证
  failures + verdict + aggregate（加权，权重见 `src/prd_gate/scoring.py`）+
  `requirement_confidence`
- `<prd>.gate.md` — 人读报告 + frontmatter patch 块
- exit code: 0 = PASS / PASS-WITH-OPEN-ITEMS，2 = FAIL

verdict 规则复刻 req-dev 阶段 5：允许失败数 = `floor(N×0.2)`；核心 Why/Who
一票否决（veto → confidence 压到 ≤0.5，必触发 M5 soft-escalate）。

## 下游消费者

| 消费者 | 读什么 | 行为 |
|---|---|---|
| `to-issues` | PRD frontmatter `final_gate_verdict` | FAIL / not_reached / 缺失 → 拒绝切票 |
| `auto-dev` (M5) | `gate_confidence` | < 0.7 → soft-escalate（映射规则见 auto-dev SKILL.md 步骤 8） |
| `auto-dev-lite` | `final_gate_verdict` | FAIL / not_reached → hard-stop（原有行为，不变） |

## 已知限制（v1）

- **独立性靠纪律保证，不靠技术保证。** 没有任何机制能阻止用户把作者对话喂给 judge，工具也检测不出来。闸门把诚实评审做得容易且可审计，但无法让不诚实评审变得不可能。
- `--judge api` 目前仅支持 Anthropic API（judge-tasks/merge 流程支持任何厂商）。
- 确定性词表（weasel word、方案语言信号）只覆盖中英文；其他语言的这些维度依赖 judge 层。
- `calib add` 按 auto-dev-lite 的 run-log 事件词表取数；其他构建系统需要按该事件契约写适配。


- judge 维度的分数仍是 LLM 判断——可信度来自 fresh context + 单一锚点 + 强制引证，不是来自魔法。复核 Evidence 段，别只看分数。
- 解析器契约 = `prd-local.md` / `user-story.md` / `prd-extension.md` 真实模板。手写的自由格式 PRD 可能解析出 0 stories → 直接 FAIL（这是 feature：不合契约的 spec 本来就不该进流水线）。
- 还没有 gate-vs-下游结果的校准数据（gate 分数是否预测 escalation/返工率）。积累 ≥10 个带 gate 报告的 run 后做相关性分析——这是 v2 的 headline。

## 相关文件

- `src/prd_gate/` — parser / checks / judge / scoring / report / cli
- `tests/prd_gate/` — 16 个回归测试（含好/坏 PRD fixtures）
- `skills/req-dev/references/quality-gateway.md` — 判定单一锚点（先于本工具存在，本工具是它的执行器）
