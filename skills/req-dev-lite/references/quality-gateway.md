# Final Quality Gateway

Used in stage 5 (in-conversation self-review) **and** as the single scoring anchor for
the independent `prd-gate`. Two review layers: the **Volere 4 questions** + the
**7-label review**. Any failure sends the story back to stage 2.

> Chinese version: [quality-gateway.zh.md](quality-gateway.zh.md). The two files are
> semantically equivalent; prd-gate judges against whichever is provided as anchor.

---

## The Volere 4 questions

### Q1 — Testable?

**Test**: could a QA engineer write a test case from this story + AC alone?

- ✅ Pass: "Given balance ¥0 When withdrawing ¥100 Then show 'Insufficient balance'" — QA can write that directly.
- ❌ Fail: "should handle insufficient balance correctly" — QA cannot know what "correctly" means.

**Fix**: add a Gherkin example, which must contain real values.

### Q2 — Traceable?

**Test**: does the story trace back to the Why and Who nailed down in stage 1?

- ✅ Pass: the story cites a concrete Why (OKR-Q2-3: cut account-opening time 30%) and a concrete Who (first-time account openers).
- ❌ Fail: the story appears from nowhere; no upstream business goal can be found.

**Fix**: add the traceability, or cut the story (it is probably `[Overreach]`).

### Q3 — Solution-free?

**Test**: does the story describe what/who/why — or technology/how?

- ✅ Pass: "The user sees accumulated redeemable points on the checkout page."
- ❌ Fail: "Cache user points in Redis to avoid hitting the database per query." (implementation)
- ❌ Fail: "Display points with a React component." (technology choice)

**Fix**: move implementation details to the PRD's Implementation Decisions section; the story keeps behavior only.

### Q4 — No weasel words?

**Test**: does it use any word that cannot be verified?

**Banned weasel-word list**:
user-friendly / 用户友好 / 友好提示 · fast / 快速 / 速度快 · quick / 迅速 ·
appropriate / 合适 / 恰当 · reasonable / 合理 · flexible / 灵活 · robust / 健壮 ·
scalable / 可扩展 · simple / 简单 · intuitive / 直观 · 高性能 · 高可用 · 易用

**Fix**: replace with a measurable value.
- "responds fast" → "P95 response time ≤ 200ms"
- "friendly error message" → "show 'Insufficient balance, please top up' with a 'Top up' button"
- "highly available" → "monthly availability ≥ 99.9%, no single outage > 5 minutes"

---

## The 7-label review

Run every user story through all seven. For each, record **the conclusion + the cited evidence**.

### `[Contradiction]`

**Definition**: two stories fight each other.
**Test**: can you construct a scenario in which both stories cannot hold?
**Example**: Story A "users may cancel an order at any time" vs Story B "orders cannot
be canceled once shipping" → hit. Make the user pick a side or write the boundary condition.

### `[Gap]`

**Definition**: the flow skips a step; an intermediate state is missing.
**Test**: lay the stories on a timeline — can each state actually reach the next?
**Example**: "user submits application → user receives approval SMS". Missing: who
reviews? how long? what on rejection? how is the notification sent? → back to stage 2.

### `[Fallacy]`

**Definition**: "because A therefore B" does not hold.
**Example**: "competitors have it, so we need it" — social proof, not a requirement
rationale. "Users asked for it" — how many? which users? what share?
**Fix**: demand data/evidence, or downgrade to an assumption in Bucket C.

### `[Redundancy]`

**Definition**: two stories say the same thing in different words.
**Example**: Story 12 "user sees shipping status on the order page" vs Story 18
"order page shows carrier and tracking number" → merge into one story with complete AC.

### `[Dangling]`

**Definition**: an entity/actor/data in the story has no owner.
**Example**: "the system automatically sends users a coupon" — whose system? who
configures the rules? who owns the blocklist? when does it send?
**Fix**: add actor + trigger + rule source.

### `[Overreach]`

**Definition**: exceeds the Why agreed in stage 1.
**Example**: agreed Why = "reduce churn of first-time account openers"; a story about
"reactivating dormant users" is out of bounds.
**Fix**: cut it, or open a separate PRD. Never stuff it into this one.

### `[Unowned]`

**Definition**: a Bucket-C open item without owner + deadline.
**Fix**: every open item MUST carry "Owner: X" and "Deadline: YYYY-MM-DD". Complete both or cut the item.

---

## Pass criteria

All stories clear both layers with zero hits. Any hit → fix → re-review. Maximum 3
rounds; if hits remain after round 3, the requirement itself is immature — **stop the
session** and resume tomorrow.

> 💡 Hard rule: do not force an immature PRD into the pipeline while tired. Re-grilling
> tomorrow is far cheaper than fixing a production bug.
