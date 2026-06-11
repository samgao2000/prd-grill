# Requirements-Development Methods, Annotated

All methods used by req-dev-lite: **5 always-on core methods** + **2 always-on
lightweight checks** + **5 optional modules triggered by context signals**. Each entry:
one-line definition / when it applies / what it owns in the skill / skip condition / commentary.

Chinese version: [methods.zh.md](methods.zh.md).

---

## Core methods (always run)

### 1. The Mom Test (Rob Fitzpatrick, 2013)

**One line**: a good question is one "even your mom couldn't lie to you about" — ask
about concrete past behavior, never opinions about the future or hypotheticals.

**Applies**: every requirements interview. **Owns**: the stage-2 grilling discipline —
banned leading questions, mandatory past-tense behavior questions. **Skip**: never.

**Commentary**: highest ROI per rule of anything here. Fitzpatrick's recurring example:
founders ask "would you use my app?", friends say yes to protect the friendship, launch
lands to zero downloads. Switch to "how did you handle this last time?" and answers
become concrete and honest. Three rules: talk about their life, not your idea; ask
about past specifics, not future intent; talk less, listen more. Red flag: answers
built on "should / probably / would / later" — pull back to the past tense.

### 2. Impact Mapping (Gojko Adzic, 2012)

**One line**: four-level map — Why (business goal) → Who (actors) → How (behavior
change) → What (deliverable).

**Applies**: every PRD opening. **Owns**: the stage-1 opening four; What is forbidden
until Why+Who are pinned. **Skip**: pure compliance/audit work (the Why is "pass the audit").

**Commentary**: the most effective anti-feature-factory tool. Bad PRDs start at What
("we need a dashboard") and never answer what business goal it serves. Adzic's core
insight: **What is the least important level — 80% of initial Whats get replaced; Why/Who/How rarely change.**
Dragging the user back to Why gets tedious; that tedium is the value.

### 3. 5 Whys (Sakichi Toyoda → Taiichi Ohno, Toyota Production System)

**One line**: ask why five layers deep to reach the root cause / underlying outcome.

**Applies**: the moment a user proposes a concrete solution/technology. **Owns**: the
stage-2.5 solution interceptor. **Skip**: trivial bug fixes with obvious root causes.

**Commentary**: Toyoda's original scene is a stopped machine — fuse → overload →
unlubricated bearing → worn pump → missing filter: five layers turn "replace the fuse"
into "install a filter". **Mind Minoura's critique**: in complex systems 5 Whys can
hallucinate a "false root cause" (one reachable point on one causal chain). Hence this
skill follows O'Hara 2025 (TechRxiv preprint): **the LLM runs the interrogation;
verification is deterministic (Volere QG)** — 5 Whys is not the destination, it is the
crutch that demotes solutions to "implementation candidates".

**Ulwick shape** (where 5 Whys lands): write the root cause as
"minimize / maximize [verb][object][constraint]", e.g. "minimize the wait between order
placement and shipping notification, without degradation at promo-day peak concurrency."

### 4. Specification by Example / Gherkin (Gojko Adzic, 2011)

**One line**: every requirement carries ≥1 Given-When-Then example with real values.

**Applies**: all acceptance criteria. **Owns**: the stage-4 mandatory output format.
**Skip**: purely visual/aesthetic requirements.

**Commentary**: Adzic's thesis: **if you can't write a concrete failing example, the
requirement isn't mature.** Abstract AC breeds ambiguity. "Handle amounts correctly" —
greater than zero? under the balance? what precision? negative refunds? Versus:

```gherkin
Given the user balance is ¥100.00
When they withdraw ¥150.00
Then show "Insufficient balance", the balance stays ¥100.00, and no withdrawal record is created
```

Writing the *second* example is where contradictions surface ("what about
installments?", "what about credit lines?") — hidden requirements exposed early and
cheaply. SBE vs BDD: BDD is tooling (Cucumber); SBE is the philosophy (examples drive
requirement maturity). We take the philosophy; Gherkin is just its notation. No
project is forced to install Cucumber.

### 5. Use Case Extensions (Alistair Cockburn, 2000)

**One line**: every main flow must enumerate "what happens when step N fails/branches".

**Applies**: every requirement with an interaction flow. **Owns**: the stage-4.5
completeness gate. **Skip**: pure computation/transformation requirements.

**Commentary**: Cockburn's fully-dressed use case has 12 sections; the soul is
Extensions. Most PRD failures aren't a badly written happy path — they're the branches
nobody wrote. Per step ask: failure? timeout? concurrency? partial success? network
drop? user cancel? Every `2a./4b.` line is a production bug exposed in advance.

---

## Lightweight checks (always run)

### 6. INVEST (Bill Wake, 2003)

**One line**: six-letter story check — Independent / Negotiable / Valuable / Estimable / Small / Testable.

**Owns**: the 30-second stage-4 screen. **Commentary**: looks trivial; every story that
skips it is a sprint disaster. *Small* is the most violated — a "one-line requirement"
routinely hides three sprints.

### 7. Volere Quality Gateway (Suzanne & James Robertson)

**One line**: every requirement answers four questions — testable, traceable,
solution-free, weasel-word-free.

**Owns**: the stage-5 hard gate (and, via prd-gate, the independent scoring anchor).
**Commentary**: the full Volere template is ~30 sections — far too heavy; we take only
the Quality Gateway mechanism, with attribution (see `attribution.md` §5 for the
required Volere copyright acknowledgment). The weasel-word list — user-friendly / fast
/ quick / appropriate / reasonable / flexible / robust / scalable / simple / intuitive —
is requirement theater, all of it.

---

## Optional modules (signal-triggered)

### 8. Event Storming (Alberto Brandolini)

**Signal**: "microservices", "DDD", "complex domain", "long business process".
**In-skill**: inserted at stage 3 — list domain events on a timeline (past-tense verbs:
"order paid", "stock deducted"), then attach actor/command/aggregate. The workshop
(orange stickies, big wall) degrades gracefully to "list events in time order"; the key
questions are Brandolini's: "what happened before this event? after?"

### 9. JTBD / ODI (Christensen; operationalized by Ulwick)

**Signal**: greenfield product, "a brand-new X", consumer scenarios.
**In-skill**: after stage 1, collect outcomes in the Ulwick shape. Full ODI (50–150
outcomes, quantitative ranking) doesn't fit a conversation; the *sentence shape* does —
it forces requirements into measurable results instead of features. "Let users book" is
a feature; "minimize the time from booking intent to confirmed booking" is an outcome.

### 10. KAOS goal trees / obstacle analysis (Axel van Lamsweerde)

**Signal**: conflicting goals, safety/compliance-sensitive, a "things that must not happen" list.
**In-skill**: decompose Why into AND/OR subgoals; list obstacles ("if X happens, the
goal fails"). Obstacles are badly underrated: PRDs list success criteria and never
failure conditions. One sentence — "if X occurs the whole feature fails" — makes risk visible.

### 11. Continuous Discovery / Opportunity Solution Tree (Teresa Torres)

**Signal**: shipped product iteration, behavioral data, regular interview cadence.
**In-skill**: after stage 1, force the OST structure — Outcome → Opportunity → Solution
→ Assumption test. Hard constraint: every Solution hangs under an Opportunity, every
Opportunity under an Outcome; floating Solutions are rejected — which rhymes with our
three-bucket rule (orphan solutions go to Bucket C).

### 12. Critical Decision Method (Gary Klein / Robert Hoffman)

**Signal**: the user is an SRE/operator/trader/expert; tacit knowledge to extract.
**In-skill**: pick one recent, concrete, hard decision and replay the timeline — when
did you notice something off? what options did you weigh? why this one? what
information would have changed your call? Asking experts "how do you decide?" yields
post-hoc rationalization; replaying an event yields the hidden cues.

---

## Methods deliberately NOT included

- **i\***: overlaps KAOS; KAOS already covers goals + anti-goals.
- **User Story Mapping**: a planning/sequencing tool; this skill interrogates single requirements.
- **MoSCoW / RICE**: prioritization belongs to the PO after the PRD lands, not to interrogation.
- **Full IEEE 830-style SRS template**: too heavy; the essential parts (functional vs
  non-functional, interfaces, constraints) are covered via the PRD template + Volere QG.
- **Lean UX / Design Sprint**: process frameworks, not single-session interrogation techniques.

---

## The "more is better" boundary

"More methods" means *more of the signal-matched optional modules*, not "run all 11
every time". Mechanically running everything turns a 30-minute session into 3 hours of
mostly redundant output. Correct posture: 5 core always; 2 lightweight checks always;
5 optional modules only on signal. At session start the agent spends 1–2 minutes
assessing context and tells the user: "Methods enabled this session: X, Y. Reason: Z."
