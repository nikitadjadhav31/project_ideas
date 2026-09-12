# AI Usage Disclosure

This project was **human-led and AI-assisted**. I (the author) owned the strategic decisions,
the domain thresholds, and the design judgment; I used AI (Claude) as a tool to draft prose,
write and debug the Python, run the research legwork, and produce the worked examples under my
direction. This document separates the two honestly: what I decided and wrote/tuned myself vs.
what the AI produced for me to review, and what I changed after it did.

Legend: 🧑 = done manually by me · 🤖 = AI-generated · 🧑🔧 = AI-drafted, then manually tuned/corrected by me.

## What I did manually (my decisions and judgment)

- 🧑 **The Skill / Agent / Neither classification for all five functions** (`docs/DECISIONS.md`).
  This is the core of the assignment and the part I would never hand to a tool — deciding that
  #1 is an Agent with a deterministic gate inside it, that #4 splits three ways, and that #5 is
  a Skill not an Agent, is a judgment call I made and then had the AI write up to my reasoning.
- 🧑 **The working definitions the whole task hinges on** — "Skills are libraries, Agents are
  workers, Neither is plumbing," and the specific test I classified on (event-triggered +
  unattended + branching ⇒ Agent). I set these deliberately so the classification would be
  consistent; the AI drafted the surrounding explanation.
- 🧑 **The design principle that the escalation trigger must be deterministic, not the LLM.**
  Insisting that a must-never-miss safety path cannot depend on a probabilistic model — and
  that the model may only ratchet urgency *up*, never down — was my architectural call. The AI
  implemented it.
- 🧑 **The grading rubric weights and the auto-fail gates.** The category weights (Resolution
  35% / Compliance 25% / Communication 25% / Efficiency 10% / Proactivity 5%) and the choice of
  which failures are *auto-fails that zero the whole score* (unverified money claim, missed
  mandatory escalation, harmful/wrong info) are business-judgment decisions about what my
  company actually cares about. I set these; the AI researched comparable industry scorecards
  to sanity-check them and wrote the anchors.
- 🧑 **The churn-risk thresholds in the briefing agent** — e.g. that a ≥40% active-seat drop is
  "critical," that <60% seat utilization is a risk, that a prior downgrade is a leading churn
  signal. These are judgment calls about my customers, not something to outsource; I chose the
  cutoffs and the AI wrote them into `analyze()`.
- 🧑 **The escalation vocabulary** (the outage / security / legal keyword lists in the triage
  gate). Which words and phrases indicate a real emergency depends on knowing my own product
  and customer language, so I curated these lists; the AI wrapped them in the regex machinery.
- 🧑 **The "no numbers in the reply skill" rule.** I decided the policy-safe-reply skill must
  contain zero dollar figures/percentages and instead force a live-doc lookup, because our
  policy doc changes often and baked-in numbers would rot. This drove a full rewrite (see
  corrections below).
- 🧑 **Scope decisions** — what to build vs. deliberately not build (no orchestration, no
  cross-component wiring, no scheduler), per the assignment's no-pipeline instruction. I later
  decided to build the **weekly quality-grading agent** (#4) as well, judging it a single
  self-contained agent (pool in → report out) rather than a pipeline, and the clearest
  demonstration of the Skill-inside-Agent relationship. The pass threshold logic (a reply that
  scrapes 80% but carries a failure tag is *not* a clean pass) was my QA-judgment call.

## What AI generated (under my direction)

- 🤖 **Prose drafting** of `DECISIONS.md`, `README.md`, and the SKILL.md bodies, following my
  decisions and the structure conventions in Anthropic's `skill-creator` skill (frontmatter,
  progressive disclosure, ~90–100-word triggering descriptions).
- 🤖 **Python implementation** of both agents, the connectors, the pluggable reasoner/
  synthesizer pattern, the drop-in `*_claude.py` classes, and all the tests — written to my
  design.
- 🤖 **Mock data** (tickets, billing/usage/tickets fixtures) — representative, not real.
- 🤖 **Worked examples** in each skill's `references/` and the applied eval outputs.

## What was grounded in research (not invented)

I had the AI web-search current sources before writing domain content, so the artifacts reflect
real conventions rather than plausible-sounding guesses. I reviewed these and kept/adjusted:
- **Grading rubric** — weighted-category-plus-auto-fail model and category set corroborated
  against current support-QA scorecard guidance (Kaizo, Zendesk QA, Supportbench, Balto,
  2025–2026). I set the final weights.
- **Bug write-up format** — title = `[area] what breaks (trigger)`, numbered repro from a known
  state, expected vs. actual, environment, severity-vs-priority — from current bug-reporting
  guides (QAWolf, Testomat, BrowserStack, Testsigma).
- **Reply tone guidance** — "voice constant, tone flexes with emotion," the do/don't phrase
  lists, lead-with-empathy — from published support-voice guidance (Mailchimp's public style
  guide as cited, Salesforce, Gorgias, Hiver).

## What I corrected after first generation

These are real fixes I made during the build, not cosmetic:
1. 🧑🔧 **Discarded a weaker first draft of the reply skill** that hardcoded example dollar
   figures, and had it rewritten around my "no numbers; verify against the live doc" rule.
2. 🧑🔧 **Fixed two triage misroutes** I caught by running the agent: a frustrated cancellation
   was landing in Billing on the word "subscription" (added a precedence rule → Account/
   retention); a "wrong totals… every time" ticket defaulted to how_to (broadened the bug
   signals).
3. 🧑🔧 **Required an adversarial test for the safety gate** (`AlwaysHowToReasoner`) that forces
   the reasoner to misclassify every ticket and proves the deterministic gate still catches
   every outage/security/legal case — because the safety argument needed a test, not a claim.
4. 🧑🔧 **Recurring-defect detection** in the briefing agent: the first version only flagged
   recurrence on a repeated keyword; I had it also honor explicit repeat language
   ("again"/"second"/"still"), which is how recurrence actually appears in ticket text.
5. 🧑🔧 **Copy bug** — at 100% seat utilization the brief still said "Paying for unused
   capacity"; made the wording conditional on utilization.
6. 🧑🔧 **Added a money-safety test** asserting the generated brief never emits a
   `$N refund/discount/credit` promise and always defers to policy — the same guardrail as the
   reply skill, applied to agent output.

## Verification performed

- Both agents run end-to-end offline; outputs are in the repo (`triage_output.json`,
  `brief_*.md`).
- All agent tests pass (`test_triage.py`, `test_briefing.py`).
- Skill frontmatter validated (well-formed, in-range descriptions, bodies under the 500-line
  guideline).
- **All three skills functionally evaluated** on fresh, adversarial cases (`skills/_eval/`): a
  refund whose figure can't be verified, an outage buried in a calm message, an angry
  cancellation, a known-issue vs. new bug, an unverified-refund auto-fail, and a
  polite-but-unresolved reply. A programmatic grader (`grade_evals.py`) checks outputs against
  objective assertions: **18/18 auto-checkable assertions pass**, with 9 judgement-only
  assertions left for human review. The grader was itself sanity-checked to confirm it fails a
  deliberately bad output, so the pass rate is real.

## Limitations (honest)

- The mock reasoner/synthesizer are keyword/heuristic stand-ins so the agents run without a
  key. They are explicitly *not* the production judgment layer — that's the `*_claude.py`
  drop-in. The safety gate and risk math are the real deterministic logic and would ship as-is.
- Mock data is representative, not real customer data. The escalation regexes favor recall
  (better a false escalation a human down-triages than a missed one); real deployment should
  tune them against historical tickets.
