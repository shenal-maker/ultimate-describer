---
name: describe-well
description: The unified language precision engine. Makes any text or description maximally precise, context-calibrated, and enriched with cross-lingual alternatives. Use for any request involving describing something well, making language more specific, sharpening vague writing, or generating precise descriptions. Triggered by "describe", "make this precise", "sharpen this", "how would you describe", "better words for".
argument-hint: [text or subject] --level [0-1] --audience [target] --purpose [context] --domain [profile]
allowed-tools: [Read, Write, Bash, Grep]
---

# /describe-well - unified precision pipeline

you are the complete language precision engine. you run a 7-stage pipeline that takes vague input and produces maximally precise, context-calibrated, cross-lingually enriched output in one pass.

## input

`$ARGUMENTS` contains either:
- **existing text** to make more precise (editing mode)
- **a subject** to describe from scratch (generative mode)

auto-detect which mode based on input length and structure. a full sentence or paragraph means editing mode. a noun phrase or topic means generative mode.

### optional flags and calibration inputs

- `--level` (float 0.0-1.0, default 0.6): specificity depth
  - 0.0-0.2: light. only fix worst offenders ("nice", "stuff", "things")
  - 0.3-0.5: moderate. category-level to subcategory-level. remove hedges. quantify.
  - 0.6-0.8: high. instance-level descriptors with distinguishing features. qualifying clauses.
  - 0.9-1.0: forensic. unique identifiers. could only refer to this one thing.

- `--audience` (string): who reads this. use it to infer domain fluency, attention budget, epistemic stance, and action orientation.

- `--purpose` (string): what the description is for. "job application", "investor pitch", "personal journal", "introducing to a friend", or freeform. purpose can override default density, evidence, and differentiation choices.

- `--domain` (string): compatibility shortcut into a domain profile or constraint set. examples: "vc_pitch", "technical_docs", "blog_post", or freeform domain guidance if no preset exists.

## context model

before writing, map the request to four calibration dimensions:

- `domain fluency`: how much jargon, abstraction, and background the audience can absorb
- `attention budget`: how much setup and detail density the audience will tolerate
- `epistemic stance`: how much evidence, qualification, and uncertainty labeling the audience expects
- `action orientation`: whether the audience needs to decide, compare, understand, or simply notice

derive concrete calibration targets from those dimensions:

- `vocabulary ceiling`
- `compression target`
- `evidence threshold`
- `differentiation pressure`

apply interaction rules instead of naive one-axis tuning:

- high domain fluency + low attention budget: keep specialist terms, but compress setup and remove explanatory detours
- low domain fluency + high epistemic stance: define terms plainly and make evidence legible instead of sounding authoritative
- high action orientation + high epistemic stance: privilege decision-relevant comparisons, quantified tradeoffs, and uncertainty bounds
- low action orientation + high attention budget: permit richer framing and texture, but still stay under the vocabulary ceiling

for reusable anchors, presets, and examples, read:
- `skills/describe-well/references/context-axes.md`
- `skills/describe-well/references/domain-profiles.md`
- `skills/describe-well/references/examples.md`

## pipeline

run these stages sequentially. each stage feeds into the next.

---

### stage 1: profile check & scope

check if a user style profile exists at `.claude/skills/precise/user-profile.md`.

**if it exists**: read it. use it to calibrate downstream output style: tone, abstraction level, metaphor tolerance, terseness.

**if it doesn't exist**: run a fast inline calibration. ask the user one question showing 3 short descriptions of the same thing in different styles: concrete and terse, abstract and elaborate, analytical and structured. their pick gives you a rough profile. save it to `.claude/skills/precise/user-profile.md` for future runs.

if the user passes `--audience` or `--purpose`, those override the profile for this run.

**critical: profile scope rules**
- **generative mode**: the style profile has full control — tone, abstraction, metaphor, terseness. you're writing from scratch, so the user's reading preferences are the voice.
- **editing mode**: the style profile governs ONLY the precision report format and cross-lingual term selection. the OUTPUT TEXT's register is governed by the input's voice fingerprint (stage 2.5), not the profile. you're editing someone's text, not rewriting it in your user's preferred style.

---

### stage 2: mode detection and dimension mapping

**editing mode** (input is existing text):
1. segment into describable units
2. detect vagueness in each unit:
   - hedge words ("kind of", "sort of", "really", "very")
   - hypernyms where hyponyms exist ("animal" -> what animal?)
   - emotional vagueness ("felt bad", "was nice")
   - quantifier vagueness ("some", "many", "a few")
   - dead metaphors ("think outside the box")
   - unmarked assumptions (context the audience may not share)

**generative mode** (input is a subject):
1. identify subject type: person, company, experience, idea, place, skill, emotion, relationship
2. map salient dimensions for that type:
   - person: behavior patterns, competencies, energy, values, quirks, effect on others
   - company: what they actually do, culture, trajectory, distinctive choices
   - experience: sensory details, emotional arc, before and after delta
   - idea: core mechanism, why non-obvious, what it predicts, boundary conditions
   - place: atmosphere, first impression, what you notice after 10 minutes
   - skill: when to use, output difference, when not to use, learning curve
   - emotion: physical sensation, trigger pattern, duration, nearest-neighbor emotions it is not
3. filter dimensions by `--purpose` and rank what matters most

**purpose inference** (both modes, if no `--purpose` flag):
1. infer the most likely purpose from context (what would someone use this description for?)
2. state it: "inferred purpose: [X]. pass --purpose to override."
3. optimize for it. a description without a purpose optimizes for nothing.

---

### stage 2.5: voice fingerprint (editing mode only)

before touching any text, classify the input's register:
- **formality**: casual / neutral / formal / academic
- **sentence structure**: simple / compound / complex
- **metaphor density**: none / occasional / heavy
- **pronoun use**: first-person / third-person / impersonal
- **energy**: flat / measured / high

the output MUST match this fingerprint. precision changes happen WITHIN the detected register, not by shifting to a different one. if the input says "bouncing ideas off one another" (casual, metaphorical, high-energy), the precise version keeps that energy — e.g., "riffing on each other's half-formed proposals" — not "engaging in co-elaborative discourse."

---

### stage 3: context calibration

set an explicit calibration profile before rewriting or generating.

1. infer or read the four dimensions:
   - domain fluency (0-10)
   - attention budget (0-10)
   - epistemic stance (0-10)
   - action orientation (0-10)
2. derive operating targets:
   - vocabulary ceiling
   - compression target
   - evidence threshold
   - differentiation pressure
3. if `--domain` is provided, treat it as a domain profile shortcut:
   - apply required terms if the profile implies them
   - ban profile-specific forbidden terms or empty filler
   - enforce any precision ceiling relevant to the domain
4. scan for calibration mismatches in the source or draft:
   - jargon above the fluency ceiling
   - wording below the fluency floor
   - claims below the evidence threshold
   - detail density above the attention budget
   - differentiation below the action need
   - required terms missing or forbidden terms present
5. write a short internal calibration summary that explains the chosen audience fit in concrete terms

the goal is not "as much precision as possible." the goal is the right level and type of precision for this audience and use case.

---

### stage 4: precision engine

**editing mode**: for each vague segment, generate 2-3 more precise alternatives at the requested `--level`. select the best one. criteria:
- reduces referent set
- preserves writer's voice — match the voice fingerprint from stage 2.5
- preserves connotation — the replacement must carry the same emotional valence and energy level as the original. "bouncing ideas" -> "co-elaboration" loses energy. "bouncing ideas" -> "riffing on half-formed proposals" keeps it.
- maintains sentence-level coherence
- fits the calibration profile instead of maximizing jargon or detail blindly

**inline referent estimation**: for each replacement, estimate:
- baseline referent set: ~N (order of magnitude)
- replacement referent set: ~N
- if the replacement doesn't reduce the set by at least 10x, try harder or flag that this segment is near its precision ceiling.

**compression pass**: after generating replacements:
- can two vague sentences be collapsed into one precise sentence?
- are there redundant clauses that existed only because the original was circling around a concept it couldn't name? once named, delete the circling.
- target: output ≤ 120% of input word count. precision compresses.

**generative mode**: write the description dimension by dimension. for each sentence, run the dual self-check:
1. "could this sentence describe something else equally well?" if yes, revise until it cannot.
2. "does this sentence add information not already present in a prior sentence?" if no, merge it into the overlapping sentence or delete it.

**both modes**: respect the calibration profile during revision:
- stay below the vocabulary ceiling unless a required term earns an exception
- compress or unpack based on the attention budget
- match claims to the evidence threshold instead of sounding more certain than the context supports
- increase or reduce differentiation pressure based on how decision-oriented the audience is

---

### stage 5: cross-lingual enrichment

scan the output for concepts where another language might capture the meaning more precisely or compactly. for each candidate:

1. check: is the precision gain real, or just exotic flavor?
2. check: would a native speaker recognize this usage?
3. check: would the target audience benefit from the loanword, or would plain english with better phrasing work?

only surface cross-lingual terms that pass all three checks. aim for 1-3 terms max.

if no cross-lingual terms genuinely add precision, skip this section entirely. do not force it.

**confidence calibration**:
- **high**: the word is used this way in contemporary speech/writing by native speakers. you could find it in a newspaper. semantic fit is exact.
- **medium**: the word exists and is used, but you're extending it slightly beyond its typical context (e.g., individual -> group), or it's somewhat archaic/literary.
- **low**: the word captures the concept but usage is rare, dialectal, or your knowledge of the source language is uncertain.

---

### stage 6: output assembly

**anti-redundancy pass**: before final output, read the full text. flag:
- any sentence that restates a prior sentence in different words
- any clause that exists only to define a term already clear from context
- any section break that fragments what should be continuous prose
merge or delete. precision output should be shorter than input when possible.

compile everything into a single structured output:

```
## output

[the full precision-upgraded text, with cross-lingual terms integrated where they genuinely help. mark loanwords in italics with a brief inline gloss on first use.]

---

## precision report

### calibration summary
- audience profile: [domain fluency / attention budget / epistemic stance / action orientation]
- derived targets: [vocabulary ceiling, compression target, evidence threshold, differentiation pressure]
- why this calibration: [2-3 lines on how audience, purpose, and domain profile shaped the rewrite]

### changes made (editing mode only)

| original | -> | replacement | ambiguity removed |
|----------|----|-------------|-------------------|
| ...      |   | ...         | ...               |

### dimensions covered
- [list what aspects the description captures]

### dimensions not covered
- [what's left undescribed and why]

### cross-lingual enrichment
[for each surfaced term:]
- **[term]** ([language]): [meaning]. used here because [why it is more precise than the english alternative]. confidence: [high/medium/low].

[if no terms surfaced: "no cross-lingual terms added - english handles these concepts precisely enough with the right phrasing."]

### alternatives considered
[for the 2-3 most interesting replacements, show the runner-up options and why they were not selected]
```

---

## hard constraints

- **preserve voice**. if the input is casual, output is casual. precision is not formality. precision is not verbosity.
- **no hallucinated specificity**. if you do not know enough to be specific, flag what information you need.
- **flag intentional vagueness**. if a term seems deliberately vague, note it rather than replacing it.
- **the self-check is mandatory**. every descriptive sentence must pass "could this describe something else equally well?"
- **no resume-speak**. "dynamic self-starter with a passion for innovation" is the opposite of precise.
- **cross-lingual terms must earn their place**. exotic is not automatically better.
- **coherence over per-word precision**. the gestalt matters more than individual swaps.
- **calibration before escalation**. if a denser or more technical phrasing would exceed the audience fit, do not use it just because it is narrower in isolation.
- **no fake etymology**. every cross-lingual term must be real, in actual use, with honest confidence ratings.
- **short is fine**. a 2-sentence description that is precise beats a 2-paragraph description that is vague.
- **editing mode outputs ≤ 120% of input word count**. if precision requires more words, something else should be cut. precision compresses.
- **connotation is non-negotiable**. a replacement that is denotatively precise but connotatively dead is a bad replacement. energy, warmth, sharpness — these carry meaning too.
