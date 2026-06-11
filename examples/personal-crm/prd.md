---
title: Personal CRM (Auto-Dev Pipeline 训练靶子)
slug: personal-crm
created: 2026-05-19
author: Sam
status: complete
final_gate_verdict: PASS-WITH-OPEN-ITEMS
methods: [Mom Test, Impact Mapping, 5 Whys, SBE, Cockburn, INVEST, Volere QG]
session_id: 2026-05-19-0651-personal-crm
snapshot: docs/prd/personal-crm-snapshot.md
---

# Personal CRM (Auto-Dev Pipeline 训练靶子)

> 一句话摘要：用一个"个人 CRM 单用户应用"作为靶子，练手 Auto-Dev pipeline 的 PRD-driven 工程纪律级交付能力。CRM 本身不是产品。

## 1. Problem Statement

### 业务目标（来自 Impact Mapping）

- **Why**：为日后真跑 Auto-Dev pipeline 准备一份合规的 PRD。这份 PRD 是练手项目的 source of truth，未来手动同步到 GitHub repo 后驱动 pipeline AFK 实现。CRM 是 pipeline 的训练靶子，不是要 ship 的产品。
  - 基线：当前 operator 用散装 prompt 喂 Claude 写代码，无 PRD、无 issue tracking、无系统化拆分
  - 目标：本 PRD 通过 Volere 终审 PASS / PASS-WITH-OPEN-ITEMS，含 ≥8 条 user stories（INVEST + Gherkin AC 含真实数值）、≥3 条 outcome metric、≥10 条 Open Items（owner+deadline 齐全）
  - 截止：2026-05-19（即本会话结束时）

- **Who**：你（Sam）作为 Auto-Dev pipeline operator。不是 CRM 终端用户——这一点会话期间被明确 push back 并修正过一次（Q2 阶段）。

- **How**：operator 的需求开发动作链从「描述功能列表 → 喂给 Claude」**变为**「Impact Mapping 钉 Why/Who → 写 user stories with INVEST + Gherkin → 未决项进 Open Items 含 owner+deadline → PRD 同步 GitHub issue → AFK pipeline 消费」。

### Outcome Metrics（桶 B）

| Metric | 当前 | 目标 | 测量方法 |
|---|---|---|---|
| PRD Volere 终审三态 | not_reached | PASS-WITH-OPEN-ITEMS（允许 ≤20% AC fail） | 阶段 5 自检通过 |
| 三桶覆盖完整性 | not_reached | A:≥8 stories / B:≥3 metrics / C:≥10 items / 弃:≥5 | 本文件章节计数 |
| user stories INVEST 过审 | not_reached | 8/8 pass | 每条 story 内 INVEST checklist 勾选 |
| Gherkin AC 含真实数值率 | not_reached | 100%（每条 story ≥1 Gherkin 例子） | 文本审查无 weasel word |
| Open Items 元数据完整率 | not_reached | 100%（owner + deadline 齐全，无双 TBD） | § 8 表格审查 |
| pipeline-actionable 切片度 | not_reached | 每条 US 可独立映射到 1-2 个 ready-for-agent issue | to-issues skill 后回填 |

### 现状与痛点

> **特殊说明**：本 PRD 的 Who 是 pipeline operator，不是 CRM 终端用户。**没有真实的 CRM-side 用户痛点 anecdote 可挖**——会话期间 Q2 阶段已尝试 Mom Test 拷问"上次因没有 CRM 吃亏什么时候"，用户诚实回答"没真吃过亏，就是想做做看"，因此 Who 改为 operator。

operator-side 现状（即真实痛点）：

- **2026-05-03 以来跑过两个 demo**（scientific calculator #58、todo demo 8 tickets），均为单语言单层无持久化，pipeline 在"工程纪律 + 跨层"维度没真压测过
- **soft-escalate 从未真实有机触发**——todo demo 那次是 `--simulate-soft-escalate` 强制注入的；operator 不知道真实场景下 soft-escalate 该长什么样
- **operator 当前的需求描述方式不严格**——会出现 weasel word（"系统应正确处理"）、跳过 INVEST 检查、Open Items 无 owner / deadline；这次正好用 CRM 当靶子练规范

---

## 2. Solution（候选方案，非锁定）

> 5 Whys 拦截器：本 PRD 中 Object-What 的所有技术选型（FastAPI、HTMX、SQLAlchemy、SQLite、Docker、structlog、cookie session）在会话早期"路 A vs 路 B"决策中已通过一轮 push-back（接受"工程纪律级压测 + 跨层协同"两个目标的约束），视为已过 5 Whys。未在拷问阶段再次拦截。

- **方案 A（锁定）**：Python 全栈 server-rendered + HTMX 局部增强。FastAPI 路由层 + Jinja2 模板 + HTMX partial render + SQLAlchemy 2.0 + alembic + SQLite 文件 + 手搓 cookie session auth + structlog JSON 日志 + ruff/mypy/pytest CI + Docker 单 service。  
  *Fit*：单语言 pipeline 风险低；跨层但不跨语言；可在 1-2 周吃完；工程纪律可真压测。
- **暂不考虑**：
  - 真跨语言全栈（FastAPI + React/Vue）— Q4 阶段被 push back 拍掉，理由：pipeline 没跑过 Node/TS，AFK 失败率高
  - HTMX 极简只 form POST — Q12 阶段被 push back 拍掉，理由：等同没用 HTMX，违反"跨层协同"Why
  - 多用户 role-based 权限 — 档次选择 Q（早期）被拍掉，理由：1-2 周 + AFK 装不下
  - PaaS 自动部署 — Q18 拍掉，理由：账号 setup 不在 pipeline 能力内

---

## 3. User Stories（桶 A）

### US-001：单 admin 登录 / 登出

**作为** pipeline operator（CRM 唯一管理员），  
**我希望** 用配置好的 admin 凭据登录 CRM 系统并能登出，  
**以便** 保护 CRM 数据不被未授权访问，且 session 状态可被 pipeline 测试覆盖。

**追溯**：Why=OM-1（Volere PASS），Who=pipeline operator（兼 admin 用户），How=auth 由散装 prompt 变为带测试覆盖的 production pattern

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**（必须含真实数值）：

```gherkin
Scenario: 正确凭据登录成功
  Given DB 的 user 表含 1 条记录, username="admin", password_hash=bcrypt("test123", rounds=12)
    And 用户访问 GET /login（未登录状态）
    And SECRET_KEY 环境变量已配置为长度 ≥32 的随机字符串
  When 用户提交表单 POST /login, body="username=admin&password=test123"
  Then HTTP 状态 302
    And response header Location="/contacts"
    And response Set-Cookie 含 session 字段, max-age=2592000 (30 天), HttpOnly, SameSite=Lax

Scenario: 错误密码登录失败（无 session 泄露）
  Given DB 的 user 表含 1 条 admin 记录
  When 用户提交 POST /login, body="username=admin&password=wrong"
  Then HTTP 状态 200
    And response body 含字符串 "用户名或密码错误"
    And response 不含 Set-Cookie 设置 session 字段
    And bcrypt verify 耗时（无论成功失败）≥80ms（防 timing attack）

Scenario: 登出清除 cookie
  Given 用户已登录，浏览器持有有效 session cookie
  When 用户提交 POST /logout
  Then HTTP 状态 302, Location="/login"
    And response Set-Cookie 含 session 字段, max-age=0
```

**主流程步骤**：
1. operator 访问 /login
2. 提交 username + password
3. 服务端 bcrypt verify
4. session cookie 签发
5. redirect /contacts

**Extensions（不开心路径）**：
- 1a. 未登录访问 /contacts → 302 redirect /login，Location 含 `?next=/contacts` 参数
- 2a. username 不存在 → 仍走完 bcrypt（dummy hash）保 timing constant，回错误提示
- 3a. password_hash 字段为空（DB 损坏）→ 500 error page + structlog ERROR 日志（含 request_id）
- 4a. SECRET_KEY 未配置 → 应用启动时 fail-fast，不允许跑（uvicorn 进程退出码 ≠ 0）
- 5a. session cookie 被篡改 → itsdangerous 验签失败 → 当作未登录处理，redirect /login

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言（bcrypt/itsdangerous 是 Object-What 已锁约束，不是方案语言） [x] 无 weasel word

**三桶归属**：桶 A（Gherkin 含真实数值：30 天 cookie, 32 字符 SECRET_KEY, 80ms bcrypt）

---

### US-002：创建 Contact

**作为** pipeline operator（CRM admin），  
**我希望** 通过表单创建一条 Contact 记录（含 name 必填、email/phone/company/tags 可选），  
**以便** 后续 user stories 有数据基础，且 pipeline 能验证 form validation + DB write 全链路。

**追溯**：Why=OM-1, Who=admin, How=naked CRUD → form validation + audit timestamp 完整

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**：

```gherkin
Scenario: 创建 Contact 含所有字段
  Given 用户已登录
    And DB contact 表为空
  When 用户提交 POST /contacts, body=
    """
    name=张三&email=zhang@example.com&phone=13800138000&company=Acme&tags=客户&tags=VIP
    """
  Then HTTP 状态 302, Location 匹配正则 "^/contacts/[0-9a-f-]{36}$"
    And DB contact 表新增 1 行, 字段值:
      | name       | 张三                  |
      | email      | zhang@example.com     |
      | phone      | 13800138000           |
      | company    | Acme                  |
      | tags       | ["客户","VIP"]        |
      | last_activity_at | NULL            |
    And created_at, updated_at 字段非 NULL 且差值 < 1 秒

Scenario: 仅 name 必填，其余 optional
  Given 用户已登录
  When 用户提交 POST /contacts, body="name=李四"
  Then HTTP 302, 新增 Contact 行, name="李四", 其他可选字段为 NULL / 空数组

Scenario: name 缺失返回 422 + inline error
  Given 用户已登录
  When 用户提交 POST /contacts, body="email=foo@bar.com" (name 缺失)
  Then HTTP 422
    And response body 含字符串 "name 不能为空"
    And response 是 partial template（含 HX-Request 时仅 form 片段, 不含 layout）
    And DB contact 表行数不变

Scenario: tags 字段重复值去重
  Given 用户已登录
  When 用户提交 POST /contacts, body="name=王五&tags=VIP&tags=VIP&tags=客户"
  Then DB 新增 Contact 行, tags JSON=["VIP","客户"]（去重，保持出现顺序）
```

**主流程步骤**：
1. operator GET /contacts/new 看到 form
2. 填字段，提交 POST /contacts
3. 服务端 Pydantic 校验
4. SQLAlchemy session.add + commit
5. 302 redirect 到 /contacts/{id}

**Extensions**：
- 2a. name 字段空白（含纯空格）→ 视为缺失 → 422 inline error
- 2b. email 字段格式不符（无 @）→ 422 inline "email 格式错误"，**不强制 email 格式校验** if 用户未填
- 2c. tags 字段含 > 20 项 → 422 "tags 数量上限 20"（防恶意输入；进 Open Items 决定是否调）
- 4a. DB write 失败（如磁盘满、SQLite 锁）→ 500 error page + structlog ERROR + transaction rollback
- 5a. 创建后并发请求 → SQLAlchemy session 隔离，无脏写

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A（Gherkin 含字段值与状态码）。依赖 OI-021（tags 上限到底定多少）。

---

### US-003：Contact 列表（含搜索、过滤、排序、HTMX partial render）

**作为** pipeline operator（CRM admin），  
**我希望** 在 /contacts 列表页看到所有 Contact 按"最近联系"排序，并能按 name/email/company 文本搜索 + 按 tag 多选 OR 过滤，搜索和过滤变化时只刷新列表区域（不全页刷新），  
**以便** 验证 pipeline 能处理"一个 endpoint 同时支持 full-page render 和 partial render"的双模式响应。

**追溯**：Why=OM-1, Who=admin, How=multi-feature endpoint 必须用 HX-Request header 区分双模式

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T（合并 search/filter/sort 是因为 HTMX partial render 让它们共享同一 list endpoint，拆开会让 issue 互相阻塞）

**Gherkin AC**：

```gherkin
Scenario: 列出所有 Contact，按 last_activity_at DESC NULLS LAST
  Given 用户已登录
    And DB contact 表含 3 条:
      | name | last_activity_at      |
      | 张三 | 2026-05-15T10:00:00Z  |
      | 李四 | NULL                  |
      | 王五 | 2026-05-19T08:00:00Z  |
  When 用户 GET /contacts (不带 HX-Request header)
  Then HTTP 200, content-type "text/html"
    And response body 含完整 HTML layout (含 <html>, <head>)
    And 列表区域 #contact-list 内顺序为: 王五, 张三, 李四
    And 李四 行的 last_activity_at 单元格显示 "—"（NULL 占位符）

Scenario: 搜索 name 字段（case-insensitive LIKE）
  Given 用户已登录
    And DB contact 表含: "Zhang San", "李四", "WangWu"
  When 用户 GET /contacts?q=zhang (不带 HX-Request)
  Then HTTP 200, 列表只含 "Zhang San"（case-insensitive 命中）
    And 不含 "李四"（无 zhang 子串）
    And 不含 "WangWu"

Scenario: 按 tag 过滤多选 OR 关系
  Given 用户已登录
    And DB contact 表含:
      | name | tags          |
      | 张三 | ["VIP"]       |
      | 李四 | ["客户"]      |
      | 王五 | ["VIP","客户"]|
      | 赵六 | []            |
  When 用户 GET /contacts?tag=VIP&tag=客户
  Then HTTP 200, 列表含 3 行: 张三, 李四, 王五
    And 不含 赵六

Scenario: 搜索 + 过滤 AND 组合
  Given 与上一场景相同 schema
  When 用户 GET /contacts?q=张&tag=VIP
  Then HTTP 200, 列表只含 张三（name 命中 AND tag 命中）

Scenario: HTMX partial render
  Given 用户已登录, 浏览器已渲染 /contacts 完整页面
  When 浏览器发起 GET /contacts?q=zhang, header HX-Request=true
  Then HTTP 200, content-type "text/html"
    And response body 不含 <html> 或 <head> 标签
    And response body 是 #contact-list 内部片段（仅 <tr> 行或 partial table fragment）
    And response header HX-Push-Url="/contacts?q=zhang"

Scenario: 空结果
  Given 用户已登录, DB contact 表为空
  When 用户 GET /contacts
  Then HTTP 200, 列表区域显示 "暂无 Contact，点 [新建] 创建第一条"
    And [新建] 是链接到 /contacts/new
```

**主流程步骤**：
1. operator GET /contacts
2. 服务端读 query params (q, tag[])
3. SQL build: name LIKE %q% OR email LIKE %q% OR company LIKE %q% (q 非空时) AND tag IN [...]（tags 命中任一时）
4. ORDER BY last_activity_at DESC NULLS LAST
5. 根据 HX-Request header 渲染 full-page 或 partial

**Extensions**：
- 2a. q 含 SQL 特殊字符（`%`, `_`）→ SQLAlchemy 参数化绑定自动 escape，无 SQL injection
- 2b. q 含 HTML 标签 → Jinja2 默认 autoescape，无 XSS
- 3a. tag 参数含不存在的 tag → 命中 0 行（不报错）
- 4a. last_activity_at 排序遇 NULL → NULLS LAST 显式约定
- 5a. partial render 时若 layout 模板被引用 → 立刻 fail-fast 拒收（pipeline 测试要发现）

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A（Gherkin 完整 + 真实数据）。依赖 OI-001（FTS5）、OI-016（tag AND 切换）、OI-017（happened_at 排序）。

---

### US-004：Contact 详情 + Activity 时间线

**作为** pipeline operator（CRM admin），  
**我希望** 点击列表中的 Contact 行进入详情页，看到该 Contact 所有字段 + 关联 Activity 按 created_at DESC 排序的时间线，  
**以便** 在不切页的情况下回顾历史。

**追溯**：Why=OM-1, Who=admin, How=join query 完整覆盖

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**：

```gherkin
Scenario: Contact 详情显示完整字段
  Given 用户已登录
    And DB 含 Contact id="abc-123-...", name="张三", email="zhang@example.com", company="Acme", tags=["VIP"], last_activity_at="2026-05-19T08:00:00Z"
    And DB 含 2 条 Activity 关联 contact_id="abc-123-...":
      | content      | happened_at | created_at            |
      | 见面聊项目   | 2026-05-19  | 2026-05-19T08:00:00Z  |
      | 电话沟通     | 2026-05-10  | 2026-05-10T14:30:00Z  |
  When 用户 GET /contacts/abc-123-...
  Then HTTP 200, response body 含字符串: "张三", "zhang@example.com", "Acme", "VIP"
    And response body 含两条 Activity，顺序: "见面聊项目"在前, "电话沟通"在后（created_at DESC）

Scenario: Contact 不存在 → 404
  Given 用户已登录
  When 用户 GET /contacts/00000000-0000-0000-0000-000000000000
  Then HTTP 404, response 是 error/404.html 全页模板
    And response body 含 "Contact 不存在" 和返回首页链接

Scenario: id 非 UUID 格式 → 404（不是 422）
  Given 用户已登录
  When 用户 GET /contacts/not-a-uuid
  Then HTTP 404
    And 不暴露 SQL 错误 stack trace
```

**主流程步骤**：
1. operator GET /contacts/{id}
2. SQL SELECT contact + JOIN activity ORDER BY a.created_at DESC
3. 渲染详情模板含 activities 列表

**Extensions**：
- 1a. 未登录 → 302 /login
- 2a. UUID 格式错 → FastAPI path validator → 404（统一不暴露内部错）
- 2b. UUID 合法但 DB 无此 contact → 404
- 3a. Contact 无任何 Activity → 时间线区域显示 "暂无活动，点 [新增] 添加"

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A。

---

### US-005：编辑 Contact（HTMX inline 或独立页）

**作为** pipeline operator（CRM admin），  
**我希望** 编辑 Contact 的所有字段（name/email/phone/company/tags），保存后 updated_at 自动刷新且回到详情页，  
**以便** 验证 PATCH 语义 + HTMX form swap。

**追溯**：Why=OM-1, Who=admin, How=PATCH 不是 PUT, partial update 语义清晰

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**：

```gherkin
Scenario: 编辑 name 字段
  Given 用户已登录
    And DB 含 Contact id="abc", name="张三", updated_at="2026-05-19T08:00:00Z"
  When 用户提交 POST /contacts/abc/edit, body="name=张三丰&email=&phone=&company=&tags="
  Then HTTP 302, Location="/contacts/abc"
    And DB Contact name 更新为 "张三丰"
    And DB Contact email 字段为 NULL（用户明确清空）
    And updated_at 字段 > "2026-05-19T08:00:00Z"

Scenario: 编辑后 last_activity_at 不被改动
  Given Contact last_activity_at="2026-05-15T10:00:00Z"
  When 用户编辑 name 字段
  Then DB Contact last_activity_at 仍为 "2026-05-15T10:00:00Z"（编辑 Contact 不触发 last_activity_at 更新，**只有写 Activity 才触发**）

Scenario: 编辑表单 422 失败（name 改空）
  Given Contact name="张三"
  When 用户提交 POST /contacts/abc/edit, body="name="
  Then HTTP 422, partial template 含 "name 不能为空"
    And DB Contact 字段不变（无部分写入）
```

**主流程步骤**：
1. GET /contacts/{id}/edit → form pre-fill
2. POST /contacts/{id}/edit
3. validation
4. DB update
5. redirect 详情页

**Extensions**：
- 2a. 用户清空 optional 字段（如 email）→ DB 写 NULL（不视为"未修改"）
- 4a. 并发编辑（两 tab）→ 后写覆盖（无乐观锁；Open Items 加锁选项）
- 5a. updated_at 是 SQLAlchemy onupdate trigger，不依赖应用代码显式赋值

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A。依赖 OI-022（乐观锁）。

---

### US-006：删除 Contact（级联删除 Activity）

**作为** pipeline operator（CRM admin），  
**我希望** 删除一个 Contact 时，其所有关联 Activity 一并删除（含 confirmation 防止误删），  
**以便** 数据完整性约束（无孤儿 Activity）成立，且 pipeline 处理 cascade delete 真实场景。

**追溯**：Why=OM-1, Who=admin, How=referential integrity 必须真做

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**：

```gherkin
Scenario: 删除 Contact 级联删除 Activity
  Given 用户已登录
    And DB 含 Contact id="abc", 关联 Activity 共 3 条
    And DB 含其他 Contact id="def", 关联 Activity 共 1 条
  When 用户 POST /contacts/abc/delete (confirmation 已通过)
  Then HTTP 302, Location="/contacts"
    And DB contact 表无 id="abc" 行
    And DB activity 表无 contact_id="abc" 行
    And DB Contact id="def" 及其 1 条 Activity 仍存在（隔离）

Scenario: 删除前确认对话框
  Given 用户已登录, GET /contacts/abc 详情页
  When 用户点击 [删除] 按钮
  Then 显示 HTMX 触发的 confirm 对话框, 文字 "确认删除 Contact 张三（含 3 条关联 Activity）？此操作不可撤销"
    And [取消] 关闭对话框, [确认] 提交 POST /contacts/abc/delete

Scenario: 删除不存在的 Contact → 404
  Given 用户已登录
  When 用户 POST /contacts/nonexistent/delete
  Then HTTP 404
    And DB 无变化
```

**主流程步骤**：
1. GET /contacts/{id} 看到 [删除]
2. 点击触发 HTMX hx-confirm 或 modal
3. 确认后 POST /contacts/{id}/delete
4. DB delete cascade
5. redirect /contacts

**Extensions**：
- 3a. cascade delete 失败（约束违反、外键损坏）→ 500 error + transaction rollback + structlog ERROR
- 4a. 用户撤销 → 无 API call（前端 cancel）
- 5a. 已删除的 Contact 详情页 → 点击删除得 404（race condition 隔离）

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A。

---

### US-007：Activity CRUD（含 last_activity_at 自动维护）

**作为** pipeline operator（CRM admin），  
**我希望** 在 Contact 详情页能添加/编辑/删除 Activity（content + 可选 happened_at），且 Contact.last_activity_at 在写 Activity 时自动同步为最新 created_at，  
**以便** 验证派生字段的 invariant 在所有写场景下被正确维护——这是 pipeline 最容易踩坑的点。

**追溯**：Why=OM-1（pipeline 必须处理派生字段一致性）, Who=admin, How=invariant maintenance 真做

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**：

```gherkin
Scenario: 添加 Activity 触发 last_activity_at 更新
  Given 用户已登录
    And DB Contact id="abc", last_activity_at=NULL
  When 用户 POST /contacts/abc/activities, body="content=见面聊项目"
  Then HTTP 302, Location="/contacts/abc"
    And DB activity 表新增 1 行, contact_id="abc", content="见面聊项目"
    And 该 Activity 的 happened_at = created_at（用户未填则默认）
    And DB Contact id="abc" 的 last_activity_at = 该 Activity 的 created_at（不是 happened_at）

Scenario: 补录历史 Activity 不让 last_activity_at 倒退
  Given DB Contact id="abc", last_activity_at="2026-05-19T08:00:00Z"
  When 用户 POST /contacts/abc/activities, body="content=补录2022年的事&happened_at=2022-03-15"
  Then 新 Activity 行 happened_at="2022-03-15", created_at=now（设为 "2026-05-19T10:00:00Z"）
    And DB Contact last_activity_at 更新为 "2026-05-19T10:00:00Z"（用户今天记录这件事，算"最近接触"）

Scenario: 删除 Activity 后 last_activity_at 重算
  Given DB Contact id="abc", 关联 Activity 3 条, created_at 分别为:
    | 2026-05-19T10:00:00Z |
    | 2026-05-15T08:00:00Z |
    | 2026-05-10T14:30:00Z |
    And Contact last_activity_at = "2026-05-19T10:00:00Z"（最新 created_at）
  When 用户删除最新的 Activity (created_at="2026-05-19T10:00:00Z")
  Then DB activity 表剩 2 条
    And DB Contact last_activity_at 重算为 "2026-05-15T08:00:00Z"（剩余最新）

Scenario: 删除最后一条 Activity 后 last_activity_at 回到 NULL
  Given Contact 仅有 1 条 Activity, last_activity_at = 该 Activity 的 created_at
  When 用户删除该 Activity
  Then Contact last_activity_at = NULL

Scenario: 编辑 Activity 的 content 不影响 last_activity_at
  Given Contact id="abc", last_activity_at="2026-05-19T10:00:00Z"
  When 用户 POST /activities/{id}/edit, body="content=改正错别字"
  Then Activity content 更新
    And last_activity_at 不变（created_at 不变，只 content 变了）

Scenario: 编辑 Activity 的 happened_at 不影响 last_activity_at
  Given Contact last_activity_at="2026-05-19T10:00:00Z"（绑定 Activity created_at）
  When 用户改 Activity happened_at 从 "2026-05-19" 到 "2022-03-15"
  Then last_activity_at 不变（语义 = MAX(created_at)，与 happened_at 无关）
```

**主流程步骤**：
1. 在 /contacts/{id} 详情页点击 [新增 Activity]
2. POST /contacts/{id}/activities
3. DB activity.insert + DB contact.update last_activity_at（同 transaction）
4. redirect 详情页

**Extensions**：
- 2a. content 为空 → 422 inline error
- 2b. happened_at 格式不合法（如 "2026-13-45"）→ 422 "日期格式错误"
- 2c. happened_at 早于 1900 或晚于 2100 → 422（防恶意 / 误输）
- 3a. activity insert 成功但 contact update 失败 → transaction rollback, 整体失败 → 500
- 4a. 用户在两个 tab 同时加 Activity → 第二个的 last_activity_at 是后写的胜（无 race condition）
- 5a. 编辑 / 删除时 Activity 不存在 → 404

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A（含大量真实数值的 invariant 测试）。这条 story 是 pipeline 最易踩坑点，多 Gherkin scenario 是有意的。

---

### US-008：CSV 导出（遵守当前筛选）

**作为** pipeline operator（CRM admin），  
**我希望** 在 Contact 列表页点击 [Export CSV] 下载当前筛选结果（不是全表），CSV 含所有 Contact 字段（tags 用 `;` 分隔），  
**以便** 数据可被外部工具（Excel/jq）读取，且 pipeline 验证 streaming 响应。

**追溯**：Why=OM-1, Who=admin, How=stream response 不是 buffer-all

**INVEST**：[x] I [x] N [x] V [x] E [x] S [x] T

**Gherkin AC**：

```gherkin
Scenario: 导出全表 CSV
  Given 用户已登录
    And DB contact 表含 2 条:
      | name | email             | tags         | last_activity_at |
      | 张三 | zhang@example.com | ["VIP","客户"] | 2026-05-19T10:00 |
      | 李四 | NULL              | []           | NULL             |
  When 用户 GET /contacts/export.csv (不带筛选参数)
  Then HTTP 200
    And response header Content-Type="text/csv; charset=utf-8"
    And response header Content-Disposition='attachment; filename="contacts-2026-05-19.csv"'
    And response body 第 1 行 = "id,name,email,phone,company,tags,last_activity_at,created_at,updated_at"
    And response body 第 2 行匹配 'abc-...,张三,zhang@example.com,,,"VIP;客户",2026-05-19T10:00:00Z,...'
    And response body 第 3 行匹配 'def-...,李四,,,,"",,...'（NULL email → 空字段；NULL last_activity_at → 空字段）

Scenario: 导出遵守当前筛选
  Given DB contact 表含 100 条
    And 用户应用过滤 ?tag=VIP&q=zhang 命中 5 条
  When 用户点击 [Export CSV]（GET /contacts/export.csv?tag=VIP&q=zhang）
  Then response 仅含 5 条记录 + 1 行 header

Scenario: tags 字段 ;分隔且 含 ; 字符的 tag 被双引号包裹
  Given Contact tags=["重要;紧急", "VIP"]（含分号的 tag）
  When 导出 CSV
  Then 该字段值为 `"重要;紧急;VIP"`（整字段被双引号包裹，原 ; 不转义；这是 CSV RFC 4180 行为）
```

**主流程步骤**：
1. GET /contacts/export.csv?<filters>
2. 服务端 query 同 /contacts 列表，但流式返回 CSV
3. 浏览器下载

**Extensions**：
- 2a. 0 条结果 → CSV 仍返回 header 行 + 0 数据行（不报错）
- 2b. 用户取消下载 → 服务端 stream 中断，无副作用
- 3a. 大数据集（> 10k 行）→ stream chunked，不全内存 buffer（pipeline 测试关注）

**Volere QG**：[x] 可测试 [x] 可追溯 [x] 无方案语言 [x] 无 weasel word

**三桶归属**：桶 A。依赖 OI-002 (CSV import)、OI-003 (Activity 导出)。

---

## 4. Implementation Decisions

### 决策记录（Decision Log）

| ID | 决策 | 备选方案 | 选定理由 | 关联 ADR |
|---|---|---|---|---|
| D-001 | 演示档次 = 个人 CRM 单用户 Contact 为中心 | 销售 CRM (Deals) / 团队 CRM (多用户) | 1-2 周 AFK 预算下唯一可行档；后已改 lite 但范围保留 | N/A |
| D-002 | Stack = FastAPI + HTMX + Jinja2 + SQLAlchemy 2.0 + alembic + SQLite + Docker 单 service | 真跨语言 (FastAPI + React) / 极简 (无 HTMX) | 单语言降 pipeline 风险；HTMX 让"跨层"压测成立 | N/A |
| D-003 | Auth = 手搓 cookie session + bcrypt + DB user 表 + env var seed admin | fastapi-users 库 / HTTP Basic / 无 auth | production pattern；不过度；pipeline 易处理；保留多用户扩展 | N/A |
| D-004 | tags 实现 = JSON 数组字段（不是 M:N 独立表） | M:N 三表 / CSV 字符串 | 单用户 < 100 tag 量级；SQLite JSON1 足以；A→B 迁移机械 | N/A |
| D-005 | Activity 模型 = 单一 Note + happened_at optional（无 type enum） | type-tagged 多态 / 多表 | 用户原话"一句话 + 日期"即此模型；type 在单用户场景无价值 | N/A |
| D-006 | last_activity_at 语义 = MAX(Activity.created_at) | MAX(happened_at) / MAX 取大 | 操作视角直觉（"我最近想起谁"）；补录场景不让派生字段错乱 | N/A |
| D-007 | 搜索范围 = name+email+company LIKE，不跨 Activity content | + FTS5 / 仅 name | 主用例覆盖；FTS5 进 Open Items | N/A |
| D-008 | 过滤 = tag 多选 OR | AND / 单选 | 直觉默认；AND 进 Open Items | N/A |
| D-009 | CSV = Contact only + 遵守 filter + tags `;` 分隔 | + import / + Activity 导出 / 全表 | backup 主用例覆盖；import/Activity 进 Open Items | N/A |
| D-010 | CI = ruff lint/format + mypy --strict + pytest + cov ≥80% + docker build smoke | + 集成测试 / + 安全扫描 / + CD | Python 项目 production 事实标准 6 项；其他进 Open Items | N/A |
| D-011 | 日志 = structlog + JSON to stdout + request_id middleware | stdlib logging / loguru | 结构化为 production 必须；pipeline 熟 | N/A |
| D-012 | 错误处理 = 表单 inline / 404 全页 / 500 全页+req_id / HTMX 失败 toast | Sentry 集成 / 极简全页 | HTMX-aware UX 一致；Sentry 进 Open Items | N/A |
| D-013 | 部署目标 = `docker compose up` 本地 only | + PaaS / + systemd / 无 Docker | 1-2 周不够上云；本地部署够练手 | N/A |
| D-014 | 新 bounded context = `crm_demo/`，待 CONTEXT-MAP.md 加行 | 不创建独立 context（共用 root） | 与 todo_demo / weather_demo 一致模式；术语隔离 | 见 Verification |

> 何时开 ADR：本会话 14 个决策均无"难逆 + 没上下文困惑 + 真实权衡"三条全中——大多数是 trade-off 不到要严格记录的强度。**保留为 Decision Log 即可，不开 ADR**。这是有意识的决定（避免 ADR 污染）。

---

## 5. Testing Decisions

### 不开心路径覆盖率

每条 user story 的 Extensions 至少一条对应测试：

| Story | 主流程测试 | Extensions 测试 | 覆盖率 |
|---|---|---|---|
| US-001 | T-001-login-success | T-001a-wrong-pw, T-001b-no-secret-key-fail-fast, T-001c-timing-constant | 4/5 |
| US-002 | T-002-create-full | T-002a-missing-name-422, T-002b-tags-dedup, T-002c-rollback-on-write-fail | 4/5 |
| US-003 | T-003-list-sort | T-003a-search-cs, T-003b-filter-tag-or, T-003c-htmx-partial, T-003d-empty | 5/5 |
| US-004 | T-004-detail | T-004a-404-uuid-invalid, T-004b-no-activity-empty-state | 3/3 |
| US-005 | T-005-edit-name | T-005a-clear-optional-field, T-005b-last_activity_not_changed | 3/3 |
| US-006 | T-006-delete-cascade | T-006a-isolation-other-contact, T-006b-confirm-required, T-006c-404 | 4/4 |
| US-007 | T-007-add-bump-last-activity | T-007a-backfill-no-regress, T-007b-delete-recompute, T-007c-edit-content-no-change, T-007d-edit-happened_at-no-change | 5/5 |
| US-008 | T-008-export-with-filter | T-008a-rfc4180-quote, T-008b-zero-rows, T-008c-stream-no-buffer | 4/4 |

### Specification by Example 一致性

QA 测试用例与 Gherkin AC 逐字符对齐——实现选项：

- **(b) 手工把 Gherkin 翻译成 pytest 测试代码**（推荐）
  - 单用户 / 8 个 US 量级，behave 框架的引入收益不抵成本
  - pytest fixture 模拟 user 登录 / db seed
  - 每个 Gherkin Scenario → 一个 pytest 函数，函数名匹配 Scenario 名

不选 (a) Cucumber/Behave 自动跑 Gherkin——pipeline 训练材料 pytest 多于 behave，且 Gherkin 翻译手工成本可控。

不选 (c) Gherkin 仅作 spec——失去"AC 即测试"价值，违反工程纪律 Why。

---

## 6. Out of Scope

### 明确丢弃的需求（不归三桶之一）

会话期间提出但被丢弃的，附理由：

- **多用户 + role-based 权限**：丢弃理由 [Overreach]——1-2 周 + AFK 预算装不下，进 Open Items O-019 等 V2
- **Deal / Pipeline / Stage / Won-Lost 状态机**：丢弃 [Overreach]——档次二/三的范围，进 Open Items O-020
- **真实 OAuth (Google / GitHub login)**：丢弃 [Overreach]——单用户场景过度，env var seed 已足
- **集成邮件（IMAP/Gmail API）/ 日历（Google Calendar）**：丢弃 [Overreach]——超出"个人 CRM 单用户"的范围
- **移动端 native app**：丢弃 [Overreach]——Web responsive 即可
- **数据加密（at rest）**：丢弃 [Fallacy]——本地 SQLite，OS 级文件权限足；at rest 加密需 KMS 等基础设施，远超练手范围
- **i18n / 多语言**：丢弃 [Overreach]——单用户用户语言固定，UI 字符串硬编码中文（必要时改）
- **WebSocket 实时推送**：丢弃 [Fallacy]——单用户场景无并发刷新需求

> 让未来读者知道"我们考虑过但没做"，避免下个 sprint 又有人提同样的事。

---

## 7. Further Notes

### 会话元数据

- 拷问会话日期：2026-05-19
- 启用方法：Mom Test + Impact Mapping + 5 Whys + SBE + Cockburn Extensions + INVEST + Volere QG（核心 7 项全启用）
- 可选模块：未启用 Event Storming / JTBD / KAOS / OST / Critical Decision Method——理由：单用户练手项目，复杂方法不触发
- 会话耗时：约 60 分钟（从"我想做一个 CRM"到 PRD 落地）
- 终审通过轮次：1/3
- 关联 snapshot：[personal-crm-snapshot.md](./personal-crm-snapshot.md)
- 关联 retro：[../../skills/req-dev-lite/sessions/2026-05-19-0651-personal-crm.md](../../skills/req-dev-lite/sessions/2026-05-19-0651-personal-crm.md)

### 重大方向转变记录

会话期间用户的两次重大方向转变（PRD 读者必读）：

1. **驱动从"做产品" → "练 pipeline"**（Q1 阶段）：原句"我想做一个 CRM"被 push back 为 solution-first 提问，最终用户明确选"练手 Auto-Dev pipeline"。
2. **从"AFK 跑 pipeline" → "只要 PRD"**（Q4 阶段 repo 归属选择）：用户选"本地 repo + req-dev-lite"，与"AFK 练 pipeline"目标冲突，被 push back 后明确改为"只要一份 PRD"。
3. **Who 从"CRM 使用者" → "pipeline operator"**（Q2 阶段）：Mom Test 拷问揭示用户无真实 CRM-side 痛点 anecdote，诚实选 "pipeline operator"，CRM 降格为"练手靶子"。
4. **HTMX 用法从"极简 form POST" → "partial render"**（Q12 阶段）：用户初选极简后被 push back（与"跨层协同"目标冲突），改回 partial render。

---

## 8. Open Items（桶 C — 未决事项，本地版替代 issue tracker）

每条**必须**有 owner + deadline + 触发上下文 + 目前最佳假设。无 owner 或无 deadline 的条目 **24h 内补全否则砍**。

| ID | 标题 | 拦截阶段 | 类型 | Owner | 答复截止 | 目前最佳假设 | 影响范围 | 状态 |
|---|---|---|---|---|---|---|---|---|
| OI-001 | Activity content 全文搜索 | Q10 搜索范围 | 技术验证 | @Sam | 2026-06-15 | SQLite FTS5 虚拟表 + trigger 同步 content 列 | US-003 | open |
| OI-002 | CSV import | Q13 CSV 范围 | 决策待定 | @Sam | 2026-06-15 | 单独 endpoint /contacts/import，pandas 或 csv stdlib + per-row validation | US-008 后续 | open |
| OI-003 | Activity 数据导出 | Q13 CSV 范围 | 决策待定 | @Sam | 2026-06-15 | 单独 endpoint /activities/export.csv | US-008 后续 | open |
| OI-004 | nginx 反代 | Q14 Docker | 技术验证 | @Sam | 2026-07-31 | docker-compose 加 nginx service + upstream FastAPI | 部署 | open |
| OI-005 | Postgres 替换 SQLite | Q14 Docker | 决策待定 | @Sam | 2026-08-31 | 当 contact 量 > 10k 或多用户时考虑；用 SQLAlchemy 同代码切换 | 数据层 | open |
| OI-006 | CI 集成测试（docker up + curl） | Q15 CI | 技术验证 | @Sam | 2026-06-30 | GitHub Actions job 启 service + 跑 smoke endpoint | CI | open |
| OI-007 | 安全扫描（bandit / safety） | Q15 CI | 决策待定 | @Sam | 2026-06-30 | 加 CI job，初期允许 warn-only，false positive 阈值后定 | CI | open |
| OI-008 | CD 自动部署 | Q15 CI | 决策待定 | @Sam | 2026-07-31 | 视 PaaS 决策定，merge to main 推 staging | 部署 | open |
| OI-009 | Sentry / Glitchtip 集成 | Q17 错误处理 | 决策待定 | @Sam | 2026-08-31 | sentry-sdk + structlog 集成 + DSN 走 env var | 错误监控 | open |
| OI-010 | PaaS 部署（Fly.io / Railway） | Q18 部署 | 决策待定 | @Sam | 2026-07-31 | 决定一个 PaaS 后写 deploy script | 部署 | open |
| OI-011 | systemd service 文件 | Q18 部署 | 技术验证 | @Sam | 2026-07-31 | 简单 .service 文件 + README VPS 部分 | 部署 | open |
| OI-012 | tag rename / merge UI | Q6 tags | 决策待定 | @Sam | 2026-09-30 | 当 tag 数 > 30 时需要；JSON 数组改全表 update 实现 | US-003 | open |
| OI-013 | tag autocomplete（server-side） | Q6 tags | 技术验证 | @Sam | 2026-09-30 | datalist + endpoint /tags?prefix= | US-002 / US-005 | open |
| OI-014 | Activity type 枚举（call/email/meeting/note） | Q7 activity | 决策待定 | @Sam | 2026-09-30 | enum 字段 + UI icon/颜色区分 | US-007 | open |
| OI-015 | last_activity_at 语义切换到 happened_at | Q11 语义 | 决策待定 | @Sam | 2026-08-31 | 当用户反馈"补录场景反直觉"时切换；改 SQL + 重算所有 contact | US-007 | open |
| OI-016 | tag 过滤 AND 关系切换 | Q10 filter | 决策待定 | @Sam | 2026-08-31 | 加 ?mode=and 参数，SQL JSON1 contains | US-003 | open |
| OI-017 | 按 happened_at 排序选项 | Q10 排序 | 决策待定 | @Sam | 2026-08-31 | 单独 sort 选项 ?sort=happened_at | US-003 | open |
| OI-018 | 数据导入 vCard / Google Contacts | Why 拓展 | 干系人对齐 | @Sam | 2026-10-31 | 从手机通讯录 vCard 或 Google Contacts API | 后续 sprint | open |
| OI-019 | 多用户 + role 权限模型 | Out of Scope V2 | 决策待定 | @Sam | 2027 V2 | RLS 或 application-level 检查；user 表已预留扩展 | 后续 major | open |
| OI-020 | Deals / Pipeline / Stage（销售 CRM 功能） | Out of Scope V2 | 决策待定 | @Sam | 2027 V2 | 档次二/三的内容 | 后续 major | open |
| OI-021 | tags 数量上限到底定多少（US-002 引用 20） | Q5 tags 隐含 | 决策待定 | @Sam | 2026-06-30 | 暂用 20；视实际使用调，若 < 5 命中则降至 10 | US-002 AC 真实数值 | open |
| OI-022 | 编辑 Contact 乐观锁（两 tab 并发） | US-005 Extensions | 决策待定 | @Sam | 2026-08-31 | 加 version 字段 + If-Match header；现暂"后写胜" | US-005 | open |

### 已解决决策（仅供历史追溯）

会话期间达成共识但未触发新 ADR 的决策（已在 § 4 Decision Log）：

- **D-901**：CRM 不创建独立 GitHub repo（最终走 lite 本地）—— 依据：阶段 Q4 用户改主意
- **D-902**：retrospective 写到 skills/req-dev-lite/sessions/（lite skill 路径，不交叉污染 full 版） —— 依据：skill 阶段 8 硬约束
