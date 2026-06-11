# Question Bank

Grilling questions you can use verbatim. Chinese version: [question-bank.zh.md](question-bank.zh.md).

**Three-part convention** (mandatory for every question group):
- **Recommended answer**: the *shape* the user's answer should take (a concrete example, not an abstract pattern)
- **Why ask**: which anti-pattern this intercepts / what truth it surfaces
- **Push-back if**: how the agent pulls the user back when the answer goes off-track

> 💡 Design intent: "lead with a recommended answer + transparent reasoning" is built
> into the question syntax. The user *verifies* instead of imagining; when they drift,
> the push-back line brings them back.

---

## 1. Mom Test banned questions (never ask)

> A *negative* list — no three-part structure. If one of these appears in the agent's own draft, replace it immediately.

| Banned question | Why banned | Replace with |
|---|---|---|
| "Would you use this feature?" | leading; friends say yes to be nice | "How did you handle this problem **last time**?" |
| "What do you think of this idea?" | open-ended compliment harvester | "How do you solve this **today**? How long does it take?" |
| "Do you think X matters?" | everyone says yes | "What did the **last** X failure concretely cost you?" |
| "Would you pay for X?" | future intent is unreliable (conversion < 10%) | "How much do you pay **now** for a similar solution?" |
| "Imagine if you had X..." | hypotheticals produce confabulation | "When was the **most recent** similar situation? Walk me through it." |
| "Would you, **in the future**...?" | same — future tense is banned | "How many times did this happen **in the past three months**?" |
| "Is this feature useful?" | almost always returns "useful" | "How did you cope **without** this feature?" |
| "Should you...?" | leads the user to the 'right' answer | "What do you **actually** do?" |

> 💡 Detection rule: if a question invites a polite "sure, that's useful", it's banned.

---

## 2. Mom Test mandatory shapes

### 2.1 Time anchoring (always the past, never the future)

**Questions**:
- "**When was the last time** you [behavior]?"
- "When did [problem] **most recently** happen?"
- "How many times in the **past [window]** did you [behavior]?"
- "How did you [behavior] **this morning / yesterday**?"

**Recommended answer**: concrete time anchor + concrete action.
> e.g. "Last Wednesday afternoon I manually reconciled 200 order rows in Excel; took 90 minutes."

**Why ask**: intercepts the future-tense trap. Past behavior is fact; future intent is imagination.

**Push-back if**:
- "We usually..." / "We would..." → "When was the **most recent** time? Walk me through *that one*."
- "Often" / "many times" → "How many times in the last 30 days?"
- Vague action ("I dealt with it") → narrative: "That time — what did you click, what did you see, then what?"

### 2.2 Walk-through (force narrative)

**Questions**:
- "Walk me through that time, **from the very start**."
- "**Step by step**: what did you click, what did you see, then what did you do?"
- "What happened **next**?"
- "What did you do **before** X?"

**Recommended answer**: ordered steps + the concrete screen/data/feedback at each step.
> e.g. "Open Salesforce → Opportunities → filter Q4 closed-won → export CSV → VLOOKUP in Excel → email finance@"

**Why ask**: narrative exposes **hidden steps, hidden decisions, hidden workarounds**.
"Describe your process" yields an abstract summary; "walk me through last time" yields the details.

**Push-back if**:
- Abstract description → "**That time** — which data did you check? With which tool?"
- Skipped steps ("then it was done") → "Wait — what happens between X and Y? Manual or automatic?"
- "I don't remember" → "What's the most recent occurrence you do remember?" or "Can you reproduce it now?"

### 2.3 Status-quo probe (exposing whether the 'need' is real)

**Questions**:
- "How do you solve this **today**?"
- "What workaround do you use **without** this feature?"
- "Why hasn't this been fixed **yet**?"
- "What have you **already tried**?"

**Recommended answer**: the concrete workaround + its cost + its limits.
> e.g. "Google Sheets + IMPORTRANGE manual sync, 20 minutes every Monday, breaks past 5,000 rows."

**Why ask**: the signature of real pain is an **existing hack**. No workaround = not painful enough = probably nice-to-have.

**Push-back if**:
- "Nothing to be done" → "Really nothing? Or something you don't count as a workaround? Concrete example."
- "We plan to..." → "Not the plan — how do you cope **right now**?"
- "We'll solve it with AI" → trigger the 5 Whys interceptor (§4)

### 2.4 Quantify the pain

**Questions**:
- "How much [time/money/customers/orders] did the **last** [problem] cost you?"
- "How many times per week/month does this happen?"
- "What's the **worst case** if this never gets fixed?"
- "How many hours a week do you spend coping with this?"

**Recommended answer**: number + unit + time window.
> e.g. "Q3: 3 enterprise renewals slipped over reconciliation delays, $480K ARR combined. Reconciliation costs the team ~12h/week."

**Why ask**: unquantified pain dies in prioritization meetings. **Quantification is the
requirement's survival armor** — and it separates real pain (has numbers) from fake pain (only "a lot").

**Push-back if**:
- "A lot" → "**How much**, concretely? A range is fine."
- "Hard to estimate" → "What did the last single occurrence cost? Just that one."
- "It's a UX thing, unquantifiable" → decompose: "Bad UX made users **do what**? Churn? Tickets? Complaints? Each is quantifiable."

### 2.5 Surface the blocker (why is this still unfixed?)

**Questions**:
- "This should have been fixed long ago — **why wasn't it**?"
- "Has anyone **tried** before? Why did it fail?"
- "What's the **biggest obstacle** to fixing it?"

**Recommended answer**: a concrete blocker (person/tech/priority/org/compliance), ideally with the prior failed attempt.
> e.g. "Two years ago backend proposed a Kafka rewrite; DevOps couldn't operate Kafka, the PM prioritized a dashboard rework, then people left and it died."

**Why ask**: reveals **true priority, organizational resistance, and technical
dependencies** — real constraints that shape the PRD's feasibility.

**Push-back if**:
- "No particular reason" → "Then why has it missed every sprint for N quarters? Who sets priority?"
- "Nobody thought of it" → counter-intuitive signal: "Really? N years of pain and zero mentions? Check the tracker / chat history." (Usually means the user isn't the real pain owner.)
- "Nobody had time" → "What outranked it? Name the top 3 things ahead of it."

---

## 3. Impact Mapping openers

Ask in this order. **No skipping.** What may not be discussed until Why and Who are nailed down.

### 3.1 Why (business goal)

**Questions**:
- "Which **business goal** does this serve? Which OKR line item?"
- "What does success look like? **Which metric**, baseline, and target?"
- "If **that goal didn't exist**, would this still be worth building?"

**Recommended answer**: explicit OKR / north-star sub-item + baseline + target + deadline.
> e.g. "Serves Q2 OKR 'reduce onboarding time 50%'. Median 14 days now; target ≤7 by end of Q2 2026."

**Why ask**: Why is the PRD's root. Discussing What before Why produces features nobody
can explain or measure after launch.

**Push-back if**:
- "Make the product better / improve UX" → weasel: "**Which metric** improves? Baseline and target?"
- "The boss wants it" → "Which business outcome does the boss want to move? By how much?"
- "Competitors have it" → "If we don't build it, what **specifically** do they take — how many users, how much ARR?"

### 3.2 Who (actors)

**Questions**:
- "**Whose** behavior must change for this to succeed? (job title, not 'users')"
- "Who **else** is affected — positively or negatively?"
- "Who might **oppose** this change?"

**Recommended answer**: concrete role + headcount + that role's typical day.
> e.g. "Mid-market AEs (~40 people), 15–20 demo calls/week. Change: manual post-demo follow-up email → automated, AE only reviews/approves."

**Why ask**: "users" is a weasel word. Below job-title granularity you cannot write a
concrete story or verify the behavior change.

**Push-back if**:
- "Our users / customers" → "**Which kind**? Which roles? Enterprise PM or SMB founder?"
- "Everyone" → "Impossible. Who changes behavior **first**? Are the rest follow-on or irrelevant?"
- No opponents considered → "If this launch **hurts** someone — support? sales? — who bangs the table?"

### 3.3 How (behavior change)

**Questions**:
- "What is their behavior **today**?"
- "What should it be **after** (X → Y)?"
- "**How will you know** the behavior actually changed? (observable signal)"

**Recommended answer**: current X (verb + frequency + tool) → target Y (verb + frequency + tool) + observable signal.
> e.g. "Now: manual SQL pull every Monday, 30 min. Target: open the dashboard, 0 min. Signal: Mon 9–11am dashboard UV ≥3×."

**Why ask**: behavior change is the only evidence of outcome. The signal must be
observable or acceptance becomes an argument.

**Push-back if**:
- "They'll like the product more" → unobservable: "**What action** proves it? Login frequency? Sharing rate?"
- "They'll use the new feature" → "Why would they switch **away from** the old workaround? What's the switching signal?"
- Behavior too big ("they become power users") → "What is the **first** observable power-user action?"

### 3.4 What (deliverable)

**Questions**:
- "What is the **smallest** thing we could build to drive that behavior change?"
- "Besides software, what else could drive it? (training? process? incentives?)"

**Recommended answer**: minimal deliverable + leverage mechanism + why it beats building bigger.
> e.g. "Minimal: an 'auto-refresh Monday 8am' option on the existing dashboard. Zero new pages, zero training, near-zero switching cost."

**Why ask**: validates that software is actually the best lever. Many requirements
decompose into process/training/incentive changes that beat code.

**Push-back if**:
- "A whole new system" → "Could we build **half** first and test? Which half is critical?"
- "It must be software" → "**Why not** training/incentive/process? Give three reasons and rebut each."
- "It needs A+B+C minimum" → "With **A only**, does behavior change? What's the signal?"

---

## 4. The 5 Whys interceptor (triggered by "I want solution X")

**Trigger**: the user names a technology/tool/implementation ("use Redis", "add a toggle", "build a dashboard", "use MongoDB", "add AI").

**Question sequence** (each answer immediately triggers the next; no skipping):

1. "Why do you want [solution X]?"
2. "Why does [previous answer] matter?"
3. "Why does it matter **now** — why can't it wait?"
4. "**Who** is harmed if [previous answer] isn't achieved, and how badly?"
5. "What is the **underlying outcome**? Use this shape: **'minimize / maximize [verb][object][constraint]'**"

**Recommended answer** (at step 5): a concrete Ulwick-style statement.
> e.g. "**Minimize** [time from demo to first value delivered] [within 7 days]."

**Why ask**: O'Hara 2025 (TechRxiv preprint) reports a 5 Whys interceptor detecting
100% of "solutions disguised as requirements" across six industry anti-patterns
(small-sample supporting evidence). Before the underlying outcome is found, letting a
solution into the PRD is building the wrong thing.

**Push-back if**:
- Steps 1–4 answered with "I just want it / gut feel / everyone uses it" → "Which **business outcome** suffers without it?"
- Stuck at step 5 → offer three templates: "minimize a duration? maximize a conversion? reduce an error rate?"
- The "outcome" is another solution ("we need to be fast") → "**How fast**? Latency of which action, against what baseline?"

**After the outcome surfaces**: record it in Bucket B (baseline + target + deadline);
demote solution X to one candidate in Implementation Decisions — not a Requirement.

---

## 5. Cockburn Extensions enumeration

For **every step** of every main flow. Happy-path-only is not allowed.

**Question templates**:
- "What if **step N fails**? What does the user see?"
- "What if **step N times out**? Wait how long? Show what?"
- "What about **concurrent conflict** at step N?" (two users acting at once)
- "What about **partial success** at step N?" (transaction half-committed)
- "What if the **network drops** at step N?"
- "What if the **user cancels** at step N? Is completed work rolled back?"

**Recommended answer**: explicit fallback behavior + user-visible feedback + data state.
> e.g. "Step 3 (submit order) timeout: no response in 5s → show 'Still processing, do not resubmit'; idempotency check prevents double charge; >30s → 'pending review' queue for manual follow-up."

**Why ask**: most PRD launch failures come from unwritten non-happy paths. Extensions
are the cheapest pre-acceptance insurance.

**Push-back if**:
- "That shouldn't happen" → "What's the **worst case** if it does? Accept it → write it into Known Risks. Otherwise keep talking."
- "Normally it's fine" → "normal" is a weasel word: "And when it's not normal? Concrete behavior."
- "Skip that case" → it must land in writing: "PRD states 'this PRD does not handle step-N failure; tracked in issue #NNN'."

---

## 6. The 7-label review questions (final gate)

Run every story through this table. A hit must be handled.

| Label | Review question | Recommended pass shape | On hit (push-back) |
|---|---|---|---|
| `[Contradiction]` | Which existing story does this **conflict** with? | none, or conflict resolved by an explicit ADR | make the user **pick a side**; record an ADR |
| `[Gap]` | After this flow, where does the user go next — any **break**? | complete state graph, no breaks | add the missing state or open a tracked item |
| `[Fallacy]` | Does "because A therefore B" **actually hold**? | causality has evidence (data/case/consensus) | demand evidence, else downgrade to assumption |
| `[Redundancy]` | Which existing story **says the same thing**? | no duplicates | merge or cut one |
| `[Dangling]` | Who **owns/produces** each entity/actor/data mentioned? | owner explicit | add the owner; no owner, no PRD entry |
| `[Overreach]` | Does this **exceed** the stage-1 Why? | within the Why | cut, or open a new PRD |
| `[Unowned]` | Who follows up this open item, **by when**? | owner + deadline | add both; TBD must resolve in 24h or be cut |

---

## 7. Domain-calibration questions (grill-with-docs subset)

**Questions**:
- "You said [term]; **the glossary defines it as X** — do you mean X or something else?"
- "Are [term A] and [term B] **the same thing**, or different?"
- "Invented extreme scenario: [scenario] — how should the system react?"
- "**The code says X** here; you just said Y — which is right?"
- "Is this relationship **1:1, 1:N, or M:N**? Give a real example."

**Recommended answer**: terms pinned to fields/tables/classes; relationships pinned to
cardinality; conflicts explicitly adjudicated and `CONTEXT.md` updated inline.
> e.g. "'Order' = a row in `orders` (excluding `order_items`). User 1:N orders. Extreme case: account deletion with an unshipped order → status `orphaned`, finance reconciles monthly."

**Why ask**: terminology drift is the single largest source of post-launch bugs.
"Account / order / cancel" mean different objects in different mouths.

**Push-back if**:
- Unregistered term → "Not in the glossary. **Give one real example** so I can register it."
- User contradicts the code → "Code says X, you say Y — pick one, update CONTEXT.md inline; major change → ADR."
- Fuzzy cardinality ("roughly one-to-many") → "**One concrete example proving 1:N, one counter-example ruling out M:N.**"
