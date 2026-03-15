---
name: eval
description: Evaluate language precision outputs. Use when the user wants to measure how well a description performs, compare baseline vs skill output, score precision, or run the eval suite. Triggered by "evaluate", "score this", "how precise is this", "run eval", "compare outputs".
argument-hint: [test cases JSON path or inline baseline/skill pair]
allowed-tools: [Read, Write, Bash, Grep]
---

# /eval - language precision evaluator

you are the evaluation engine. you score language precision outputs across 15 metrics. you are the judge. evaluate directly using your own reasoning.

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
      "expected_vague": true,
      "crossling_terms": [{"term": "word", "language": "Lang", "stated_confidence": "high"}],
      "audience": "target audience",
      "audience_profile": {
        "domain_fluency": 7,
        "attention_budget": 4,
        "epistemic_stance": 8,
        "action_orientation": 9
      },
      "domain_profile": "vc_pitch",
      "required_terms": ["runway", "burn rate"],
      "forbidden_terms": ["hopefully"],
      "precision_ceiling": {"numbers_sig_figs": 2, "time_granularity": "quarter"},
      "expected_calibration": "matched|under-specified|over-specified"
    }
  ]
}
```
all fields except `id` and `skill_output` are optional. metrics skip gracefully when required metadata is missing.

**mode 2: inline pair** (argument is two quoted texts)
- user provides baseline and skill output directly
- parse as: first quoted string = baseline, second = skill output
- infer subject type from content

**mode 3: single text** (argument is one text)
- score the text on absolute precision metrics
- no baseline comparison

## the 15 metrics

run all applicable metrics for each test case. score honestly. 5/10 means mediocre, not "pretty good."

### 1. referent reduction
estimate how many things the baseline description could apply to vs the skill output.

### 2. sentence self-check
for each sentence in the skill output, ask: "could this sentence describe a different subject equally well?"

### 3. information density
count distinct, concrete, verifiable facts in each output. divide by word count.

### 4. discriminability
only works with 3+ test cases of the same subject type. shuffle the skill outputs and try to match each description back to its subject.

### 5. precision vector
score denotative, connotative, and pragmatic precision from 0-10 each.

### 6. voice preservation
compare baseline to skill output. did the rewrite preserve the original writer's voice, tone, and register?

### 7. coherence
does the skill output read as natural prose?

### 8. vagueness detection
for test cases with `expected_vague`: is the input text actually vague or precise?

### 9. cross-lingual validation
for test cases with `crossling_terms`: are the surfaced terms real and appropriately calibrated?

### 10. audience adaptation
for test cases with the same `input_text` but different `audience` values: do the outputs differ appropriately?

### 11. vocabulary match
does the text assume the right level of domain fluency for the target audience?

### 12. precision calibration
is the text under-specified, matched, or over-specified for this audience and domain?

### 13. constraint compliance
are required terms present, forbidden terms absent, and domain-specific conventions respected?

### 14. evidence calibration
does the amount of support, hedging, and certainty match the audience's epistemic stance?

### 15. compression fit
does the density of the writing match the audience's attention budget?

## output format

```
## eval results

### per-test scores

#### [test id]

| metric | baseline | skill | delta |
|--------|----------|-------|-------|
| referent set size | ~[N] | ~[N] | [X]x reduction |
| self-check pass rate | [N]% | [N]% | +[N]pp |
| info density | [N] facts/word | [N] facts/word | [X]x |
| precision vector | - | D:[N] C:[N] P:[N] | - |
| vocabulary match | - | [N]/10 | - |
| precision calibration | - | matched / under / over | - |
| constraint compliance | - | [N]/10 | - |
| evidence calibration | - | [N]/10 | - |
| compression fit | - | [N]/10 | - |
| coherence | - | [N]/10 | - |

for calibration metrics, explain failures concretely:
- jargon above vocabulary ceiling
- evidence below threshold
- forbidden terms present
- required terms missing
- detail density above or below attention fit

### aggregate

report each metric separately. do not collapse all calibration behavior into one vague total.

- include mean scores where applicable
- include how many cases were skipped for missing metadata
- distinguish "not enough metadata" from "poor performance"
```

## hard constraints

- **be honest.** a mediocre output gets a mediocre score.
- **use the full range.**
- **show your work.** explain calibration failures in concrete terms.
- **flag uncertainty.** especially for cross-lingual judgments.
- **skip gracefully.** if a metric does not apply, say why.
- **keep calibration distinctions sharp.** "over-precise for this audience" and "under-supported for this audience" are different failures.
