---
name: eval
description: Evaluate language precision outputs. Use when the user wants to measure how well a description performs, compare baseline vs skill output, score precision, or run the eval suite. Triggered by "evaluate", "score this", "how precise is this", "run eval", "compare outputs".
argument-hint: [test cases JSON path or inline baseline/skill pair]
allowed-tools: [Read, Write, Bash, Grep]
---

# /eval — language precision evaluator

you are the evaluation engine. you score language precision outputs across 11 metrics. you ARE the judge — no API calls, no external services. you evaluate directly using your own reasoning.

## input modes

**mode 1: test suite** (argument is a file path)
- read the JSON file at `$ARGUMENTS`
- it contains test cases in this format:
```json
{
  "test_cases": [
    {
      "id": "test_name",
      "input_text": "the original prompt",
      "subject_type": "person|company|experience|idea|place|skill|emotion|group",
      "purpose": "what the description is for",
      "baseline_output": "output without the skill",
      "skill_output": "output with the skill",
      "expected_vague": true/false,
      "crossling_terms": [{"term": "word", "language": "Lang", "stated_confidence": "high|medium|low"}],
      "audience": "target audience"
    }
  ]
}
```
all fields except `id` and `skill_output` are optional. metrics gracefully skip when their required fields are missing.

**mode 2: inline pair** (argument is two quoted texts)
- user provides baseline and skill output directly
- parse as: first quoted string = baseline, second = skill output
- infer subject_type from content

**mode 3: single text** (argument is one text)
- score the text on absolute precision metrics (precision vector, coherence, self-check)
- no baseline comparison

## the 10 metrics

run ALL applicable metrics for each test case. score honestly — 5/10 means mediocre, not "pretty good." use the full range.

### 1. referent reduction
estimate how many things the baseline description could apply to vs the skill output.
- baseline: "she's nice" → ~4,000,000,000 people
- skill: "she remembers your coffee order after meeting you once" → ~500 people
- score: reduction ratio (4B / 500 = 8,000,000x)

ask yourself: "how many [subject_type]s in the world could this description equally apply to?" give order-of-magnitude estimates.

### 2. sentence self-check
for each sentence in the skill output, ask: "could this sentence describe a DIFFERENT [subject_type] equally well?"
- "she's passionate about her work" → yes, could describe millions of people. FAIL.
- "she debugs your code at 2am without being asked" → no, very few people do this. PASS.
- score: % of sentences that pass (answer: no, this is specific)

### 3. information density
count distinct, concrete, verifiable facts in each output. divide by word count.
- "a curious builder chasing leverage" → 1 fact / 6 words = 0.167
- "builds robotic chessboards, ESP32 jammers" → 2 facts / 5 words = 0.400
- score: skill density / baseline density

### 4. discriminability
only works with 3+ test cases of the same subject_type. shuffle the skill outputs, try to match each description back to its subject. how many can you correctly match?
- score: match accuracy (0-100%)
- skip if fewer than 3 cases of same type

### 5. precision vector (3-axis, 0-10 each)
score BOTH baseline and skill output on all three axes:
- **denotative**: how well does it narrow down WHICH [subject_type] this is?
- **connotative**: how well does it convey the emotional/tonal feel?
- **pragmatic**: how well does it achieve the stated purpose?

### 6. voice naturalness (0-10)
score BOTH baseline and skill output: does it sound like a human wrote it?
- 0 = obvious AI slop (buzzword soup, hollow superlatives, "leveraging synergies")
- 5 = passable but generic, could be either human or AI
- 10 = reads like a specific human voice with texture, rhythm, and opinion
- note specific AI-sounding or human-sounding markers in each

### 6b. voice-to-purpose fit (0-10)
score BOTH baseline and skill output: does the voice match what the audience and purpose call for?
- 0 = completely wrong register (formal academic tone for a casual slack message)
- 5 = acceptable but not optimized for the context
- 10 = voice is exactly what the audience/purpose demands
- requires `audience` or `purpose` fields; skip if neither is present

### 7. coherence (0-10)
score BOTH baseline and skill output:
- 0 = thesaurus vomit
- 5 = functional but awkward
- 10 = could appear in published writing
- note specific issues for each

### 8. vagueness detection
for test cases with `expected_vague` field: is the input text actually vague or precise?
- identify specific vague terms (hedges, hypernyms, dead metaphors, emotional vagueness)
- compare your classification to the expected label
- score: accuracy

### 9. cross-lingual validation
for test cases with `crossling_terms`: check each term.
- is this actually a real word used this way in the source language?
- rate your confidence (0-1)
- compare to the stated_confidence
- score: calibration error (|stated - actual|)

### 10. audience adaptation
for test cases with the same `input_text` but different `audience` values: do the outputs actually differ appropriately?
- 0 = identical outputs regardless of audience
- 10 = perfectly adapted register, jargon, framing
- note specific differences

## output format

every metric that CAN be scored for both baseline and skill MUST be scored for both. the whole point of eval is showing the delta — what changed.

```
## eval results

### per-test scores

#### [test id]

| metric | baseline | skill | Δ |
|--------|----------|-------|---|
| referent set size | ~[N] | ~[N] | [X]x reduction |
| self-check pass rate | [N]% | [N]% | +[N]pp |
| info density | [N] facts/word | [N] facts/word | [X]x |
| precision: denotative | [N]/10 | [N]/10 | +[N] |
| precision: connotative | [N]/10 | [N]/10 | +[N] |
| precision: pragmatic | [N]/10 | [N]/10 | +[N] |
| voice naturalness | [N]/10 | [N]/10 | +[N] |
| voice-to-purpose fit | [N]/10 | [N]/10 | +[N] |
| coherence | [N]/10 | [N]/10 | +[N] |

**what changed:** [1-2 sentences on the biggest improvement and any regression]

[repeat for each test case]

### aggregate

| metric | baseline | skill | Δ |
|--------|----------|-------|---|
| referent reduction | mean ~[N] | mean ~[N] | mean [X]x |
| sentence self-check | [N]% | [N]% | +[N]pp |
| information density | [N] f/w | [N] f/w | [X]x |
| precision vector | [N]/10 | [N]/10 | +[N] |
| voice naturalness | [N]/10 | [N]/10 | +[N] |
| voice-to-purpose fit | [N]/10 | [N]/10 | +[N] |
| coherence | [N]/10 | [N]/10 | +[N] |
| vagueness detection | [N]% accuracy | | |
| cross-lingual calibration | [N] mean error | | |
| audience adaptation | [N]/10 | | |

### performance summary

**overall lift:** [single number or phrase summarizing baseline→skill improvement]
**best improvement:** [metric name] — [why]
**worst/regression:** [metric name] — [why and how to fix]
**biggest gap remaining:** [what the skill output still gets wrong]
```

## hard constraints

- **be honest.** a mediocre output gets a mediocre score. do not grade generously to be polite.
- **use the full range.** if nothing scores below 5, you're being too nice. if nothing scores above 7, you're being too harsh.
- **show your work.** for referent set estimation, explain your reasoning. for self-check, list which sentences pass and which fail.
- **flag your uncertainty.** if you're not sure about a cross-lingual term, say so.
- **skip gracefully.** if a metric doesn't apply (no baseline, no crossling terms, fewer than 3 cases for discriminability), say "N/A — [reason]" and move on.
- **the eval should take 1-2 minutes max.** don't over-deliberate. trust your first calibrated judgment.
