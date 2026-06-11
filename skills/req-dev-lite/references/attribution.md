# Sources & Safety Review

req-dev-lite **ships no executable code from any external source** — it cites the
*concepts, question shapes, and templates* below. Each entry lists: source, what was
borrowed, what was modified, and the safety-review conclusion.

Last reviewed: **2026-06-10** (all external sources re-verified on the web).
Chinese version: [attribution.zh.md](attribution.zh.md).

---

## Sources

### 1. Rob Fitzpatrick — *The Mom Test* (book, 2013)

- **Borrowed**: the three rules (their life / past behavior / listen more), the banned-question list, the mandatory question shapes.
- **Used in**: `SKILL.md` stage 2; `question-bank.md` §1–2.
- **Modified**: re-expressed and extended (e.g., the "why is this still unfixed" cost-quantification questions); no original passages reproduced.
- **Review**: ☑ methodology concepts, not copyrightable expression; no source text copied.

### 2. Gojko Adzic — *Impact Mapping* (2012) & *Specification by Example* (2011)

- **Borrowed**: the four-level Why/Who/How/What map; the SBE thesis ("if you can't write a concrete failing example, the requirement isn't mature"); Gherkin Given-When-Then.
- **Used in**: `SKILL.md` stages 1 & 4; `methods.md` §2 & §4; `templates/user-story*.md`.
- **Modified**: Impact Mapping turned into a stepwise conversational protocol; examples ours.
- **Review**: ☑ Gherkin syntax is an open standard (Cucumber, MIT); ☑ concepts only.

### 3. Toyota Production System / Sakichi Toyoda — 5 Whys

- **Borrowed**: the five-layer why chain.
- **Used in**: `SKILL.md` stage 2.5; `question-bank.md` §4.
- **Modified**: combined with O'Hara 2025's LLM-interrogation / deterministic-verification split; landing point fixed to the Ulwick outcome shape; Minoura's critique of 5 Whys included rather than ignored.
- **Review**: ☑ public-domain methodology.

### 4. Alistair Cockburn — Use Case Extensions (*Writing Effective Use Cases*, 2000)

- **Borrowed**: main flow + per-step failure/branch enumeration.
- **Used in**: `SKILL.md` stage 4.5; `methods.md` §5; `question-bank.md` §5.
- **Modified**: added modern failure modes (concurrency, partial success, user cancel).
- **Review**: ☑ methodology, no code, no reproduced text.

### 5. Suzanne & James Robertson — Volere Requirements Specification Template

- **Borrowed**: the Quality Gateway mechanism only (4 testpoints: testable / traceable / solution-free / no weasel words) — not the full ~30-section template.
- **Used in**: `SKILL.md` stage 5; `quality-gateway.md`; executed mechanically by `prd-gate`.
- **Copyright acknowledgment (as required by volere.org)**: concepts referenced from the
  Volere Requirements Specification Template, copyright © 1995–2019 the Atlantic
  Systems Guild Limited. The template itself may not be sold or used for commercial
  gain without the Guild's written permission; **this repository reproduces no part of
  the template text** — it implements the Quality Gateway *idea* in original wording, with attribution.
- **Review (re-verified 2026-06-10 against volere.org terms)**: ☑ compliant — concept use + attribution, no template distribution.

### 6. Bill Wake — INVEST (article, 2003, xp123.com)

- **Borrowed**: the six-letter story checklist.
- **Used in**: `SKILL.md` stage 4; `templates/user-story*.md`.
- **Review**: ☑ public methodology concept.

### 7. Tony Ulwick — Outcome-Driven Innovation outcome syntax

- **Borrowed**: the "minimize / maximize [verb][object][constraint]" sentence shape.
- **Used in**: `SKILL.md` stage 2.5; `methods.md` §9.
- **Review**: ☑ sentence shape as public method; Strategyn's proprietary research process not used.

### 8. carollrollroll/prd-skill (GitHub)

- **URL**: https://github.com/carollrollroll/prd-skill — **License: MIT** (verified 2026-06-10).
- **Borrowed**: the seven review label names — [Contradiction] [Gap] [Fallacy] [Redundancy] [Dangling] [Overreach] [Unowned].
- **Modified**: label names kept; all judgment criteria, examples, and fix procedures rewritten from scratch (`quality-gateway.md` §7).
- **Review**: ☑ MIT; ☑ no code or prompt text copied; label-name borrowing with attribution.

### 9. wiveu/prd-skill-agent (GitHub)

- **URL**: https://github.com/wiveu/prd-skill-agent — **License: MIT** (verified 2026-06-10).
- **Borrowed**: the design philosophy "a good PRD is not a wish list — it's a decision log."
- **Review**: ☑ MIT; ☑ philosophy only; no question bank or SKILL text copied.

### 10. Christopher Aaron O'Hara — *Agentic Architecture Mediation for LLM Assistants:
Preventing Solution-Jumping with Requirements Elicitation* (TechRxiv **preprint**, Dec 2025)

- **Source**: TechRxiv, DOI 10.36227/techrxiv.176583345.56962463 (dataset on IEEE DataPort).
  *Correction 2026-06-10: previously mislabeled "IEEE Software 2025"; it is a preprint —
  treat its conclusions as not yet journal-peer-reviewed.*
- **Borrowed**: the division of labor "LLM runs the interrogation; verification is
  deterministic" and the multi-agent 5 Whys interceptor against solution-jumping.
- **Evidence strength**: the paper **reports** 100% detection of solution mismatches
  across six industry anti-patterns (~$0.01/session) — small-sample supporting
  evidence, not proof.
- **Used in**: design rationale for `SKILL.md` stage 2.5; `methods.md` §3; `question-bank.md` §4.

---

## Standards alignment (why we call these "recognized practice")

The Quality Gateway dimensions align with the individual-requirement quality
characteristics described in **ISO/IEC/IEEE 29148** (requirements engineering):
verifiability (Q1), traceability (Q2), unambiguity (Q4); our Q3 ("solution-free")
mirrors what the standard calls implementation freedom. The 7 labels address
set-level characteristics: consistency ([Contradiction]/[Redundancy]) and
completeness ([Gap]/[Dangling]). Gherkin/SBE and INVEST are de-facto agile standards.
None of this is exotic — the contribution here is *mechanical enforcement at an agent
handoff*, not new theory.

*Reference note*: the standard is cited nominatively; **no text, definitions, tables,
or clause content from ISO/IEC/IEEE 29148 is reproduced** in this repository, and no
conformance or certification claim is made or implied.

## Safety review summary

| Check | Status |
|---|---|
| No external URLs embedded in skill files (other than this attribution file) | ☑ |
| No executable code from external sources | ☑ |
| No instructions that load remote content | ☑ |
| No git submodule / clone references to other repos | ☑ |
| No PII / commercially sensitive data | ☑ |
| No API keys / secrets | ☑ |
| All sources attributed; licenses verified 2026-06-10 (MIT × 2 repos; Volere terms; grill-with-docs MIT vendored in `third_party/`) | ☑ |

If any cited repository's license changes (e.g., to GPL/AGPL), re-review the corresponding entry.
