---
name: articulate
description: Precision language engine with always-on and one-shot modes. "/articulate on" activates continuous precision (quizzes you on preferences first). "/articulate off" deactivates it. "/articulate [thing]" does a one-shot precise description with full analysis report. Triggered by "articulate", "describe well", "make this precise".
argument-hint: on | off | [text or subject] --level [0-1] --audience [target] --purpose [context] --domain [profile]
allowed-tools: [Read, Write, Bash, Grep, AskUserQuestion]
---

# /articulate

one skill, three modes. detect mode from `$ARGUMENTS`:

- `$ARGUMENTS` is exactly "on" → **always-on activation**
- `$ARGUMENTS` is exactly "off" → **deactivation**
- anything else → **one-shot mode**

---

## mode 1: `/articulate on` — always-on activation

### step 1: quiz the user

ask the user about their preferences using AskUserQuestion. gather:

1. **precision level** (0-1): how aggressively should descriptions be sharpened?
   - options: light (0.2), moderate (0.5), high (0.7), forensic (0.9)

2. **audience**: who will read most of your output?
   - options: technical peers, general educated audience, specific domain (ask which), or "varies — ask me each time"

3. **purpose**: what's most of your descriptive writing for?
   - options: professional communication, creative/personal writing, technical documentation, persuasion/pitching, or "varies — ask me each time"

4. **domain**: default framing lens?
   - options: technical, colloquial, first-principles, literary, mathematical, or "no default"

### step 2: save config

write the preferences to `.claude/skills/articulate/active-config.md`:

```markdown
---
active: true
activated: [current date]
---

## preferences

- level: [value]
- audience: [value]
- purpose: [value]
- domain: [value]
```

### step 3: confirm

tell the user articulate mode is on and what preferences were saved. remind them: `/articulate off` to deactivate, `/articulate [thing]` for a one-shot with full report.

---

## mode 2: `/articulate off` — deactivation

delete `.claude/skills/articulate/active-config.md` if it exists. confirm to the user that articulate mode is off.

---

## mode 3: `/articulate [thing]` — one-shot with full report

this is the detailed analysis mode. run the complete 7-stage pipeline from the describe-well engine, with full precision report output.

### input

`$ARGUMENTS` (minus any flags) contains either:
- **existing text** to make more precise (editing mode)
- **a subject** to describe from scratch (generative mode)

auto-detect which mode based on input length and structure. a full sentence or paragraph means editing mode. a noun phrase or topic means generative mode.

### optional flags

- `--level` (float 0.0-1.0, default 0.6): specificity depth
  - 0.0-0.2: light. only fix worst offenders ("nice", "stuff", "things")
  - 0.3-0.5: moderate. category-level to subcategory-level. remove hedges. quantify.
  - 0.6-0.8: high. instance-level descriptors with distinguishing features. qualifying clauses.
  - 0.9-1.0: forensic. unique identifiers. could only refer to this one thing.

- `--audience` (string): who reads this. use it to infer domain fluency, attention budget, epistemic stance, and action orientation.

- `--purpose` (string): what the description is for. "job application", "investor pitch", "personal journal", "introducing to a friend", or freeform.

- `--domain` (string): domain profile shortcut. examples: "vc_pitch", "technical_docs", "blog_post", or freeform.

### context model

before writing, map the request to four calibration dimensions:

- `domain fluency`: how much jargon, abstraction, and background the audience can absorb
- `attention budget`: how much setup and detail density the audience will tolerate
- `epistemic stance`: how much evidence, qualification, and uncertainty labeling the audience expects
- `action orientation`: whether the audience needs to decide, compare, understand, or simply notice

derive concrete calibration targets:

- `vocabulary ceiling`
- `compression target`
- `evidence threshold`
- `differentiation pressure`

interaction rules:

- high domain fluency + low attention budget: keep specialist terms, compress setup
- low domain fluency + high epistemic stance: define plainly, make evidence legible
- high action orientation + high epistemic stance: decision-relevant comparisons, quantified tradeoffs
- low action orientation + high attention budget: richer framing, stay under vocabulary ceiling

for reusable anchors, presets, and examples, read:
- `skills/describe-well/references/context-axes.md`
- `skills/describe-well/references/domain-profiles.md`
- `skills/describe-well/references/examples.md`

### pipeline

run these stages sequentially.

#### stage 1: profile check & scope

check if a user style profile exists at `.claude/skills/precise/user-profile.md`.

**if it exists**: read it. calibrate downstream output style.

**if it doesn't exist**: run a fast inline calibration. ask the user one question showing 3 short descriptions of the same thing in different styles: concrete/terse, abstract/elaborate, analytical/structured. save to `.claude/skills/precise/user-profile.md`.

if `--audience` or `--purpose` passed, those override the profile for this run.

**profile scope rules**:
- **generative mode**: style profile has full control over tone, abstraction, metaphor, terseness.
- **editing mode**: style profile governs ONLY the precision report format. the output text's register is governed by the voice fingerprint (stage 2.5).

#### stage 2: mode detection and dimension mapping

**editing mode** (existing text):
1. segment into describable units
2. detect vagueness: hedge words, hypernyms, emotional vagueness, quantifier vagueness, dead metaphors, unmarked assumptions

**generative mode** (subject):
1. identify subject type: person, company, experience, idea, place, skill, emotion, relationship
2. map salient dimensions for that type
3. filter by `--purpose`, rank what matters most

**purpose inference** (both modes, if no `--purpose` flag):
1. infer the most likely purpose from context
2. state it: "inferred purpose: [X]. pass --purpose to override."

#### stage 2.5: voice fingerprint (editing mode only)

classify the input's register:
- **formality**: casual / neutral / formal / academic
- **sentence structure**: simple / compound / complex
- **metaphor density**: none / occasional / heavy
- **pronoun use**: first-person / third-person / impersonal
- **energy**: flat / measured / high

output MUST match this fingerprint. precision within the register, not a register shift.

#### stage 3: context calibration

1. infer or read the four dimensions (domain fluency, attention budget, epistemic stance, action orientation)
2. derive operating targets (vocabulary ceiling, compression target, evidence threshold, differentiation pressure)
3. if `--domain` provided, apply domain profile (required terms, forbidden terms, precision ceilings)
4. scan for calibration mismatches
5. write internal calibration summary

the goal: right level and type of precision for this audience and use case.

#### stage 4: precision engine

**editing mode**: for each vague segment, generate 2-3 precise alternatives. select best by:
- referent set reduction
- voice fingerprint match
- connotation preservation (same emotional valence and energy)
- sentence-level coherence
- calibration profile fit

**inline referent estimation**: for each replacement, estimate baseline vs replacement referent set. if <10x reduction, try harder.

**compression pass**: collapse redundant sentences. delete circling clauses. target ≤ 120% of input word count.

**generative mode**: write dimension by dimension. dual self-check:
1. "could this describe something else equally well?" → revise if yes
2. "does this add information not in a prior sentence?" → merge or delete if no

**word count awareness** (generative mode, when prompt specifies a target):
1. after drafting, count words. if over target:
2. rank each sentence by self-check uniqueness score (how many other things could it describe?)
3. identify the lowest-scoring sentence. ask: does removing it lose a dimension the description needs? if yes, keep it and try the next-lowest. if no, cut it.
4. if still over target after cutting cuttable sentences: tighten phrasing (remove qualifiers, compress clauses) rather than dropping dimensions.
5. **quality gate**: never cut below the point where the description loses a load-bearing distinction. overshooting the word count by 20% is better than losing a dimension that makes the description unique. flag the overrun in the precision report rather than silently degrading.

**both modes**: respect calibration — vocabulary ceiling, compression target, evidence threshold, differentiation pressure.

#### stage 5: cross-lingual enrichment

scan for concepts where another language captures meaning more precisely. for each candidate:
1. is the precision gain real?
2. would a native speaker recognize this usage?
3. would the audience benefit?

1-3 terms max. skip if english handles it.

**confidence calibration**:
- **high**: contemporary usage, newspaper-findable, exact semantic fit
- **medium**: real but slightly extended context or somewhat archaic
- **low**: rare, dialectal, or uncertain source language knowledge

#### stage 6: output assembly

**anti-redundancy pass**: flag restated sentences, unnecessary definitions, fragmented prose. merge or delete.

compile into structured output:

```
## output

[the full precision-upgraded text. loanwords in italics with inline gloss.]

---

## precision report

### calibration summary
- audience profile: [domain fluency / attention budget / epistemic stance / action orientation]
- derived targets: [vocabulary ceiling, compression target, evidence threshold, differentiation pressure]
- why this calibration: [2-3 lines]

### changes made (editing mode only)

| original | -> | replacement | ambiguity removed |
|----------|----|-------------|-------------------|
| ...      |    | ...         | ...               |

### dimensions covered
- [list]

### dimensions not covered
- [list with reasons]

### cross-lingual enrichment
- **[term]** ([language]): [meaning]. why: [reason]. confidence: [high/medium/low].

### alternatives considered
[2-3 most interesting runner-ups and why not selected]
```

### hard constraints

- **preserve voice**. precision is not formality. precision is not verbosity.
- **no hallucinated specificity**. flag what info you'd need.
- **flag intentional vagueness**. note it, don't replace it.
- **self-check mandatory**. every sentence must pass.
- **no resume-speak**.
- **cross-lingual terms earn their place**. exotic is not better.
- **coherence over per-word precision**.
- **calibration before escalation**. don't exceed audience fit for narrowness.
- **no fake etymology**.
- **short is fine**.
- **editing mode ≤ 120% input word count**.
- **connotation is non-negotiable**.

---

## always-on mode behavior

this section defines what happens when articulate mode is active (config file exists). it is NOT executed by `/articulate` directly — it is referenced by the always-on detection in CLAUDE.md.

when always-on:
1. read `.claude/skills/articulate/active-config.md` for saved preferences
2. run the same 7-stage pipeline on any descriptive output you generate
3. **output clean text only** — no precision report, no alternatives table, no changes-made section, no calibration summary
4. apply saved level, audience, purpose, domain as defaults (user can override per-message)
5. if a preference is set to "varies", infer from context for that dimension
6. be invisible — the user should feel like you're just naturally articulate, not running a pipeline
