# 需求开发会话快照（lite）- personal-crm

**对应 PRD**：[prd.md](./prd.md)
**Slug**：personal-crm（用于续跑识别）
**首次会话**：2026-05-19 06:30
**最近更新**：2026-05-19 06:55
**累计会话次数**：1（首次）
**累计耗时**：约 60 分钟
**启用方法清单**：Mom Test + Impact Mapping + 5 Whys + SBE + Cockburn Extensions + INVEST + Volere QG（核心 7 项全启用，可选模块未触发）
**终审三态结果**：PASS-WITH-OPEN-ITEMS

---

## Resume 信息

- **Status**：completed
- **Stop reason**：not_applicable
- **Pending stage**：N/A
- **Pending items**：N/A
- **Resumable slug**：personal-crm（日后扩 V2 时仍用此 slug 续跑）
- **续跑指引**：日后想加 Deals / 多用户 / FTS5 等 V2 功能时说"继续 req-dev-lite personal-crm"，agent 读本 snapshot + PRD 的 Open Items 表格继续

---

## 三桶统计（本次会话）

- 桶 A（Gherkin AC，进 PRD User Stories）：8 条 user stories（含 35+ Gherkin Scenarios）
- 桶 B（Outcome Metric，进 PRD Problem Statement）：6 条
- 桶 C（Open Items，进 PRD § 8 表格）：22 条
- 丢弃（不归三桶，进 PRD § 6 Out of Scope）：8 条

桶 C 占比 22/(8+6+22+8) = ~50%——超过 30% 异常阈值。但是：本项目是"练手靶子"性质，明确"先 ship 最薄端到端，扩展功能进 Open Items"是有意识决定，**非需求成熟度问题**。retro 已记录该判断依据。

---

## 桶 C 摘要（详情见 PRD 文件 § 8 Open Items）

| OI-ID | 标题 | 拦截阶段 | Owner | 答复截止 | 当前状态 |
|---|---|---|---|---|---|
| OI-001 | Activity content 全文搜索 | Q10 | @Sam | 2026-06-15 | open |
| OI-002 | CSV import | Q13 | @Sam | 2026-06-15 | open |
| OI-003 | Activity 数据导出 | Q13 | @Sam | 2026-06-15 | open |
| OI-004 | nginx 反代 | Q14 | @Sam | 2026-07-31 | open |
| OI-005 | Postgres 替换 | Q14 | @Sam | 2026-08-31 | open |
| OI-006 | CI 集成测试 | Q15 | @Sam | 2026-06-30 | open |
| OI-007 | 安全扫描 | Q15 | @Sam | 2026-06-30 | open |
| OI-008 | CD 自动部署 | Q15 | @Sam | 2026-07-31 | open |
| OI-009 | Sentry 集成 | Q17 | @Sam | 2026-08-31 | open |
| OI-010 | PaaS 部署 | Q18 | @Sam | 2026-07-31 | open |
| OI-011 | systemd service | Q18 | @Sam | 2026-07-31 | open |
| OI-012 | tag rename/merge | Q6 | @Sam | 2026-09-30 | open |
| OI-013 | tag autocomplete | Q6 | @Sam | 2026-09-30 | open |
| OI-014 | Activity type 枚举 | Q7 | @Sam | 2026-09-30 | open |
| OI-015 | last_activity 语义切换 | Q11 | @Sam | 2026-08-31 | open |
| OI-016 | tag 过滤 AND 切换 | Q10 | @Sam | 2026-08-31 | open |
| OI-017 | happened_at 排序选项 | Q10 | @Sam | 2026-08-31 | open |
| OI-018 | vCard / Google Contacts 导入 | Why 拓展 | @Sam | 2026-10-31 | open |
| OI-019 | 多用户 + role 权限 | Out of Scope V2 | @Sam | 2027 V2 | open |
| OI-020 | Deals / Pipeline / Stage | Out of Scope V2 | @Sam | 2027 V2 | open |
| OI-021 | tags 数量上限定多少 | Q5 隐含 | @Sam | 2026-06-30 | open |
| OI-022 | 编辑 Contact 乐观锁 | US-005 Ext | @Sam | 2026-08-31 | open |

---

## 已解决决策（仅供历史追溯）

详见 PRD § 4 Decision Log（D-001 ~ D-014）+ § 8 末尾的 D-901/D-902。

---

## 命中过的反模式（教训记录）

- [x] 客套话陷阱 — 0 次（用户全程直接回答 + 改主意）
- [ ] 未来时陷阱 — 0 次
- [x] 方案伪装成需求 — 0 次（5 Whys 拦截器未触发：技术栈选择在路 A/B 阶段已预先 push back 视为通过）
- [ ] 抽象 AC — 0 次（用户全程接受推荐答案的真实数值）
- [x] happy path 陷阱 — 1 次（用户初选 HTMX 极简等同没用 HTMX，被 push back 后改 partial render）

---

## 会话历史（按时间倒序）

### Run 1 — 2026-05-19 06:30 ~ 06:55
- Status: completed
- 钉死 Why/Who/How/What（阶段 1）
- 18 个 Q&A round 完成阶段 2 拷问（Contact / tags / Activity / last_activity 语义 / Auth / ORM / 搜索 / HTMX / CSV / Docker / CI / 日志 / 错误 / 部署）
- 产出 8 条 user stories + 35+ Gherkin Scenarios + 14 条 Decision Log + 22 条 Open Items + 8 条 Out of Scope
- 重大方向转变 4 次（详见 PRD § 7）

---

## 下次会话准备

- [ ] V2 加 Deals/多用户 时先解决 OI-019 / OI-020 的范围定义
- [ ] FTS5 (OI-001) 在 V1 稳定后第一个加（用户反馈最强烈）
- [ ] OI-021 (tags 数量上限) 视 V1 实际使用决定是否调
- [x] 阶段 1 钉死的 Why/Who/How 已锁，V2 不重审除非用户主动 reframe
