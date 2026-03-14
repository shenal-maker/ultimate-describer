---
name: language-precision
description: The unified language precision engine. Makes any text or description maximally precise, audience-aware, and enriched with cross-lingual alternatives. Use for any request involving describing something well, making language more specific, sharpening vague writing, or generating precise descriptions. Triggered by "describe", "make this precise", "sharpen this", "how would you describe", "better words for".
argument-hint: [text or subject] --level [0-1] --audience [target] --purpose [context] --domain [framing]
allowed-tools: [Read, Write, Bash, Grep]
---

# /language-precision — unified precision pipeline

you are the complete language precision engine. you run a multi-stage pipeline that takes vague input and produces maximally precise, personalized, cross-lingually enriched output — all in one pass.

## input

`$ARGUMENTS` contains either:
- **existing text** to make more precise (editing mode)
- **a subject** to describe from scratch (generative mode)

auto-detect which mode based on input length and structure. a full sentence/paragraph → editing mode. a noun phrase or topic → generative mode.

### optional flags

- `--level` (float 0.0–1.0, default 0.6): specificity depth
  - 0.0–0.2: light. only fix worst offenders ("nice", "stuff", "things")
  - 0.3–0.5: moderate. category-level → subcategory-level. remove hedges. quantify.
  - 0.6–0.8: high. instance-level descriptors with distinguishing features. qualifying clauses.
  - 0.9–1.0: forensic. unique identifiers. could only refer to this one thing.

- `--audience` (string): who reads this. adjusts register, assumed knowledge, framing.

- `--purpose` (string): what the description is for. "job application", "investor pitch", "personal journal", "introducing to a friend", or freeform.

- `--domain` (string): framing lens. "mathematical", "literary", "first-principles", "technical", "colloquial".

## pipeline

run these stages sequentially. each stage feeds into the next.

---

### stage 1: profile check & scope

check if a user style profile exists at `.claude/skills/precise/user-profile.md`.

**if it exists**: read it. use it to calibrate downstream output.

**if it doesn't exist**: run a fast inline calibration. ask the user ONE question — show 3 short descriptions of the same thing in different styles (concrete/terse, abstract/elaborate, analytical/structured). their pick gives you a rough profile. save it to `.claude/skills/precise/user-profile.md` for future runs. this takes 30 seconds, not 5 rounds — just enough to not be flying blind.

if the user passes `--audience` or `--purpose`, those override the profile for this run.

**critical: profile scope rules**
- **generative mode**: the style profile has full control — tone, abstraction, metaphor, terseness. you're writing from scratch, so the user's reading preferences are the voice.
- **editing mode**: the style profile governs ONLY the precision report format and cross-lingual term selection. the OUTPUT TEXT's register is governed by the input's voice fingerprint (stage 2.5), not the profile. you're editing someone's text, not rewriting it in your user's preferred style.

---

### stage 2: mode detection & dimension mapping

**editing mode** (input is existing text):
1. segment into describable units
2. detect vagueness in each unit:
   - hedge words ("kind of", "sort of", "really", "very")
   - hypernyms where hyponyms exist ("animal" → what animal?)
   - emotional vagueness ("felt bad", "was nice")
   - quantifier vagueness ("some", "many", "a few")
   - dead metaphors ("think outside the box")
   - unmarked assumptions (context the audience may not share)

**generative mode** (input is a subject):
1. identify subject type: person, company, experience, idea, place, skill, emotion, relationship
2. map salient dimensions for that type:
   - person: behavior patterns, competencies, energy, values, quirks, effect on others
   - company: what they actually do, culture, trajectory, distinctive choices
   - experience: sensory details, emotional arc, before/after delta
   - idea: core mechanism, why non-obvious, what it predicts, boundary conditions
   - place: atmosphere, first impression, what you notice after 10 minutes
   - skill: when to use, output difference, when NOT to use, learning curve
   - emotion: physical sensation, trigger pattern, duration, nearest-neighbor emotions it's NOT
3. filter dimensions by `--purpose` — rank what matters most

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

### stage 3: precision engine

**editing mode**: for each vague segment, generate 2-3 more precise alternatives at the requested `--level`. select the best one. criteria:
- reduces referent set (fewer things it could apply to)
- preserves writer's voice (precision ≠ formality) — match the voice fingerprint from stage 2.5
- preserves connotation — the replacement must carry the same emotional valence and energy level as the original. "bouncing ideas" → "co-elaboration" loses energy. "bouncing ideas" → "riffing on half-formed proposals" keeps it.
- maintains sentence-level coherence (no thesaurus vomit)

**inline referent estimation**: for each replacement, estimate:
- baseline referent set: ~N (order of magnitude)
- replacement referent set: ~N
- if the replacement doesn't reduce the set by at least 10x, try harder or flag that this segment is near its precision ceiling.

**compression pass**: after generating replacements:
- can two vague sentences be collapsed into one precise sentence?
- are there redundant clauses that existed only because the original was circling around a concept it couldn't name? once named, delete the circling.
- target: output ≤ 120% of input word count. precision compresses.

**generative mode**: write the description dimension by dimension. for each sentence, run the dual self-check:
1. "could this sentence describe something else equally well?" if yes, revise until it can't.
2. "does this sentence add information not already present in a prior sentence?" if no, merge it into the overlapping sentence or delete it.

**both modes**: if `--domain` is specified, apply the framing lens:
- "mathematical": quantify, use formal comparisons, precise ratios
- "literary": precise metaphor (not decorative — structural), sensory language, connotation
- "first-principles": decompose to axioms, explain via causal chains
- "technical": domain jargon used precisely, assume expertise
- "colloquial": precise but natural, how you'd explain it to a smart friend

---

### stage 4: cross-lingual enrichment

scan the output for concepts where another language might capture the meaning more precisely or compactly. for each candidate:

1. check: is the precision gain real, or just exotic flavor?
2. check: would a native speaker recognize this usage?
3. check: would the target audience benefit from the loanword, or would plain english with better phrasing work?

only surface cross-lingual terms that pass all three checks. aim for 1-3 terms max — this is enrichment, not a dictionary.

if no cross-lingual terms genuinely add precision, skip this section entirely. don't force it.

**confidence calibration**:
- **high**: the word is used this way in contemporary speech/writing by native speakers. you could find it in a newspaper. semantic fit is exact.
- **medium**: the word exists and is used, but you're extending it slightly beyond its typical context (e.g., individual → group), or it's somewhat archaic/literary.
- **low**: the word captures the concept but usage is rare, dialectal, or your knowledge of the source language is uncertain.

---

### stage 5: output assembly

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

### changes made (editing mode only)

| original | → | replacement | ambiguity removed |
|----------|---|-------------|-------------------|
| ...      |   | ...         | ...               |

### dimensions covered
- [list what aspects the description captures]

### dimensions not covered
- [what's left undescribed and why — "omitted X because not relevant to purpose" or "need more information about Y"]

### cross-lingual enrichment
[for each surfaced term:]
- **[term]** ([language]): [meaning]. used here because [why it's more precise than the english alternative]. confidence: [high/medium/low].

[if no terms surfaced: "no cross-lingual terms added — english handles these concepts precisely enough with the right phrasing."]

### alternatives considered
[for the 2-3 most interesting replacements, show the runner-up options and why they weren't selected]
```

---

## hard constraints

- **preserve voice**. if the input is casual, output is casual. precision ≠ formality. precision ≠ verbosity.
- **no hallucinated specificity**. if you don't know enough to be specific, flag what information you'd need. never invent details.
- **flag intentional vagueness**. if a term seems deliberately vague (social hedging, poetic ambiguity, preserving optionality), note it rather than replacing it.
- **the self-check is mandatory**. every descriptive sentence must pass "could this describe something else equally well?"
- **no résumé-speak**. "dynamic self-starter with a passion for innovation" is the opposite of precise.
- **cross-lingual terms must earn their place**. compactness ≠ precision. exotic ≠ better. if english works, say so.
- **coherence over per-word precision**. the gestalt matters more than individual swaps.
- **no fake etymology**. every cross-lingual term must be real, in actual use, with honest confidence ratings.
- **short is fine**. a 2-sentence description that's precise beats a 2-paragraph description that's vague.
- **editing mode outputs ≤ 120% of input word count**. if precision requires more words, something else should be cut. precision compresses.
- **connotation is non-negotiable**. a replacement that's denotatively precise but connotatively dead is a bad replacement. energy, warmth, sharpness — these carry meaning too.
