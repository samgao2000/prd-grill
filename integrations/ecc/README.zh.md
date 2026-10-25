# prd-grill + ECC

[English → README.md](README.md)

[ECC](https://github.com/affaan-m/ECC) 给编码智能体一套工程体系：
`plan -> test -> implement -> review -> verify -> remember -> improve`。
这条链上每一道闸门都在**代码产生之后**。没有任何一环检查 plan 所依据的那条需求。

prd-grill 是 `/ecc:plan` 之前的那一步：把需求拷问到可证伪，用独立判官给 PRD 打分，
再通过本集成，拒绝让 ECC 从一份没过闸门的 PRD 开始规划或开发。

```
prd-grill                                  ECC
──────────────────────────────────────     ──────────────────────────────────────
req-dev-lite   （拷问，人回答）
      ↓
prd-gate score （确定性底线）
      ↓
prd-judge      （全新上下文的 agent）   ──► product-capability   （PRD → 工程约束）
      ↓                                          ↓
prd-gate merge → PRD frontmatter        ──► /ecc:plan            （plan 产物）
      │  final_gate_verdict                      ↓
      │  gate_mode: prd-gate            ──► tdd-workflow         （RED → GREEN，证据报告）
      │  gate_confidence                         ↓
      └─ prd-gate-guard 钩子 ───────────►  /code-review、verify、remember
         PRD 为 FAIL / 未评分 / 自评时
         阻断 /ecc:plan、tdd-workflow、
         product-capability
```

ECC 本身一个字节不改。prd-grill 只加三件东西，ECC 的架构里本来就有它们的位置。

## 三件东西

| 件 | 文件 | 对应 ECC 概念 | 作用 |
|---|---|---|---|
| 判官 agent | [`agents/prd-judge.md`](../../agents/prd-judge.md) | agent（独立上下文、受限工具） | 只读 PRD + 锚点准则来回答 `judge-tasks.json`。独立性靠结构保证，不靠口头约定。 |
| 守卫钩子 | [`hooks/prd-gate-guard.py`](../../hooks/prd-gate-guard.py) + [`hooks/hooks.json`](../../hooks/hooks.json) | hook（在模型上下文之外运行，exit 2 阻断） | 遇到 `/plan`、`/ecc:plan`、`/tdd`，或模型调用 `plan` / `tdd-workflow` / `product-capability` / `auto-dev-lite` 时，读最新 `docs/prd/*.md` 的 frontmatter；除非 `final_gate_verdict` 为 `PASS*` **且** `gate_mode: prd-gate`，否则阻断。 |
| 三个 skill | [`skills/`](../../skills) | skill（ECC 的主界面） | 不变。frontmatter 带 `metadata.origin: prd-grill`，并按 ECC 格式补了「何时触发」。 |

守卫补上了闸门 README 里承认的那个缺口——「独立性靠纪律而非技术保证」。自评的 PASS 现在被机制拦下。

## 安装

### Claude Code 插件（推荐）

```
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
/plugin marketplace add samgao2000/prd-grill
/plugin install prd-grill@prd-grill
```

prd-grill 插件自带三个 skill、`prd-judge` agent 和守卫钩子。先后顺序无关，两个插件安装时互不依赖。

### 手动（ECC 用 `./install.sh` 装的，或要装到项目目录）

```bash
git clone https://github.com/samgao2000/prd-grill
python prd-grill/integrations/ecc/install.py            # → ~/.claude
python prd-grill/integrations/ecc/install.py --project  # → ./.claude（在项目目录内运行）
```

幂等。向 `settings.json` 合并两条 hook，拷贝 agent、守卫脚本和三个 skill。
`--dry-run` 只打印计划；`--uninstall` 移除 hook 条目。

### 闸门 CLI

```bash
pip install "prd-grill @ git+https://github.com/samgao2000/prd-grill"
```

纯标准库。确定性层需要它；不装的话 PRD 停留在 `gate_mode: self-reported`，守卫会阻断规划——这正是设计意图。

## 日常流程

```
「拷问我的需求」                               → docs/prd/2026-10-25-billing-alerts.md
prd-gate score --prd docs/prd/2026-10-25-billing-alerts.md
                                               → .judge-tasks.json；若已 FAIL 则 exit 2
「用 prd-judge agent 处理 docs/prd/2026-10-25-billing-alerts.judge-tasks.json」
                                               → .judge-results.json（全新上下文）
prd-gate merge --prd ... --judge-results ...   → .gate.json / .gate.md + frontmatter 补丁
把补丁粘回 PRD

/ecc:plan "按 docs/prd/2026-10-25-billing-alerts.md 做 billing alerts"
                                               → 守卫：OK PASS-WITH-OPEN-ITEMS (gate_confidence=0.85)
tdd-workflow                                   → RED → GREEN，证据报告
```

如果 verdict 是 FAIL，或者跳过了判官，`/ecc:plan` 会返回：

```
[prd-gate-guard] BLOCKED 2026-10-25-billing-alerts.md: verdict PASS is gate_mode=self-reported.
The author model graded its own PRD. Run `prd-gate score` + the prd-judge agent + `prd-gate merge`, then retry.
```

## 守卫的精确行为

| 情形 | 结果 |
|---|---|
| 提示词/skill 不是规划或构建触发 | 放行，静默 |
| 是触发，但项目没有 `docs/prd/` | 放行，stderr 一行提醒（`PRD_GATE_GUARD=strict` → 阻断） |
| 最新 PRD：`PASS` / `PASS-WITH-OPEN-ITEMS` 且 `gate_mode: prd-gate` | 放行，打印 verdict 与置信度 |
| 最新 PRD：`PASS*` 但 `gate_mode: self-reported` 或缺失 | **阻断** |
| 最新 PRD：`FAIL` / `not_reached` / 无 frontmatter | **阻断** |
| `PRD_GATE_GUARD=off` | 放行，静默 |
| `PRD_GATE_GUARD_PRD=<path>` | 改为检查指定文件 |
| `req-dev-lite`、`prd-gate` 两个 skill | 永不阻断（它们本身就是闸门） |

「最新」= `docs/prd/` 下文件名 `YYYY-MM-DD` 前缀最大者，相同则看修改时间。
`*.gate.md`、`*-snapshot.md`、`*.judge-*.json` 不计入。

## 本集成（暂时）不做的事

- **从 ECC 的构建过程采集校准数据。** `prd-gate calib add` 从 auto-dev-lite 的运行日志事件
  （`pytest_failed`、`issue_blocked` 等）推导返工结果。ECC 的 `tdd-workflow` 留下的是另一种痕迹
  （检查点提交 + `.tdd.md` 证据报告）。把 RED/GREEN 证据映射到 calib 事件词表的适配器是下一项；
  在此之前，用 tdd-workflow 构建的运行不能作为校准记录。
- **给 plan 产物把关。** 守卫检查的是 PRD，不是 `*.plan.md`。给 plan 打分是另一套准则，不在此范围。
- **替换 ECC 的 hooks 运行时。** 守卫只是两条普通 hook，不使用也不依赖 ECC 的钩子调度器。

## 为什么不直接贡献进 ECC 主库？

以后可能会，等校准数据够了（≥10 次过闸门的运行）。在那之前集成放在这里，方法可追溯出处，
三个 skill 也能独立安装。ECC 的适配政策（「复制想法，不复制身份」）对一个 harness 来说合理；
对一种方法来说，出处很重要。所以每个 skill 都带 `metadata.origin: prd-grill`，仓库根有 `CITATION.cff`。

— 高山 Sam Gao，2026
