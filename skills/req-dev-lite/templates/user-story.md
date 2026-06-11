# User Story Template

Use this for every story. The comments explain why each section exists — keep them
until the team is fluent. Chinese version: [user-story.zh.md](user-story.zh.md).

```markdown
## US-NNN: [short title]

<!-- Title: verb–object, what the user can do. e.g. "View accumulated redeemable points" -->

### Story
As a <specific role>,
I want <action + object>,
so that <observable value>.

<!-- Role must be a job title, not "user".
     Value must be observable, not "convenient" or "better".
     ✓ As a first-time account opener aged 18–25, I want to see exactly which
       verification step failed, so that I can fix it without redoing the whole flow.
     ✗ As a user, I want easier operations, so that the experience is better.
-->

### Traceability
- Upstream Why: [stage-1 business goal id / OKR-XX-X]
- Upstream Who: [stage-1 role]
- Upstream How: [behavior change: X → Y]

<!-- Can't fill this in → the story is [Overreach] or the trace is broken. Back to stage 1. -->

### INVEST (30-second screen)
- [ ] Independent — deliverable without other undelivered stories
- [ ] Negotiable — details still discussable, not a frozen spec
- [ ] Valuable — visible value to the traced Who
- [ ] Estimable — engineering can size it
- [ ] Small — fits one sprint
- [ ] Testable — verifiable completion criteria

### Acceptance criteria (Gherkin — ≥1 example, MUST contain real values)

```gherkin
Scenario: [noun-phrase scenario name]
  Given [initial state, down to field values]
    And [other preconditions]
  When [user action, down to click/input/call]
  Then [observable result, down to displayed text / data change / status code]
    And [other observable results]
```

<!-- Real values are mandatory.
     ✓ Given balance ¥100.00 When withdrawing ¥150.00 Then show "Insufficient balance, withdrawable ¥100"
     ✗ Given insufficient balance When withdrawing Then show an error
-->

### Unhappy paths (Cockburn Extensions)

Main flow steps:
1. [step]
2. [step]
...

Extensions:
- 1a. [step 1 fails/times out/cancelled] → [specific behavior]
- 1b. [other branch] → [specific behavior]
- 2a. [step 2 fails] → [specific behavior]
...

<!-- One missing branch = [Gap]. Back to stage 2. -->

### Volere QG self-check
- [ ] Testable — QA can write tests from this directly
- [ ] Traceable — upstream Why/Who filled in
- [ ] Solution-free — no Redis/React/specific tech
- [ ] No weasel words — no user-friendly / fast / 友好 / 高性能 etc.

### Bucket assignment
- [ ] Bucket A: this story has Gherkin AC with real values
- [ ] Bucket B: linked outcome metric (in the PRD body)
- [ ] Bucket C: depends on an open item (link it)

<!-- Fits no bucket → it does not enter the PRD. -->
```
