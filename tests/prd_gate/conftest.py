import sys
from pathlib import Path as _P

# Acceptance tests import sibling fixtures as top-level modules
sys.path.insert(0, str(_P(__file__).parent))

import textwrap

import pytest

GOOD_PRD = textwrap.dedent("""\
    ---
    title: CSM Onboarding Dashboard
    slug: csm-dashboard
    created: 2026-06-10
    status: complete
    final_gate_verdict: not_reached
    ---

    # CSM Onboarding Dashboard

    ## 1. Problem Statement

    - **Why**：2026 Q2 OKR「onboarding 中位时长减半」
      - 基线：14 天（2026 Q1 末测）
      - 目标：≤7 天
      - 截止：2026-06-30
    - **Who**：Customer Success Manager（12 人）
    - **How**：每周手动查 Notion → 每早 9am 看 dashboard

    ## 3. User Stories（桶 A）

    ### US-001：查看 owned 客户阶段总览

    **作为** CSM，**我希望** 打开主页看到 owned 客户列表，**以便** 不开会就发现卡死客户。

    **追溯**：Why=OKR-Q2-1, Who=CSM, How=周会同步 → 每早自查

    **Gherkin AC**：
    ```gherkin
    Scenario: 总览加载
      Given CSM Lily 登录，owned 12 个 active 客户
      When 她打开主页
      Then 显示 12 行，每行含客户名、阶段、卡死天数
    ```

    **Extensions（不开心路径）**：
    - 1a. 加载超时 3 秒 → 显示「点击重试」
    - 2a. owned 客户为 0 → 显示空态文案「暂无客户」

    ### US-002：卡死 3 天自动通知

    **作为** CSM，**我希望** 客户卡死 ≥3 天时收到通知，**以便** 在客户 escalate 前介入。

    **追溯**：Why=OKR-Q2-1, Who=CSM, How=被动等 escalation → 3 天内主动介入

    **Gherkin AC**：
    ```gherkin
    Scenario: 卡死告警
      Given Acme Corp 卡在 SSO 配置 3 天 0 小时
      When 每日 9:00am job 运行
      Then 主 CSM 收到消息「Acme Corp 卡在 SSO 配置 3 天」
    ```

    **Extensions（不开心路径）**：
    - 1a. 同客户同阶段已告警过 → 不重复发

    ## 8. Open Items（桶 C）

    | ID | 标题 | Owner | 答复截止 | 状态 |
    |---|---|---|---|---|
    | OI-001 | 阶段定义需 VP 确认 | @lina | 2026-06-15 | open |
    """)

BAD_PRD = textwrap.dedent("""\
    ---
    title: Some Feature
    ---

    # Some Feature

    ## 1. Problem Statement

    - **Why**：<阶段 1 钉死的业务目标>
    - **Who**：用户

    ## 3. User Stories

    ### US-001：快速友好的查询

    **作为** 用户，**我希望** 系统快速响应并给出友好提示，**以便** 体验更好。
    用 Redis 缓存结果保证高性能。

    ### US-002：合理处理错误

    **作为** 用户，**我希望** 系统合理处理错误。

    **追溯**：Why=[业务目标], Who=<角色>

    ```gherkin
    Scenario: 错误处理
      Given 出现错误
      When 用户操作
      Then 系统正确处理
    ```

    ## 8. Open Items（桶 C）

    | ID | 标题 | Owner | 答复截止 | 状态 |
    |---|---|---|---|---|
    | OI-001 | 待定问题 | TBD | TBD | open |
    """)


@pytest.fixture
def good_prd_file(tmp_path):
    p = tmp_path / "2026-06-10-good.md"
    p.write_text(GOOD_PRD, encoding="utf-8")
    return p


@pytest.fixture
def bad_prd_file(tmp_path):
    p = tmp_path / "2026-06-10-bad.md"
    p.write_text(BAD_PRD, encoding="utf-8")
    return p
