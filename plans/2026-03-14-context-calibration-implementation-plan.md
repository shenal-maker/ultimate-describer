# Context Calibration Layer Implementation Plan

## Overview

Replace the current flat `--domain` framing concept with a first-class context calibration layer inside the unified `describe-well` skill. The new layer will model audience and domain context through four explicit dimensions, apply deterministic calibration rules before the precision rewrite/generation stage, and extend the test and eval stack so calibration quality is measurable rather than implied.

## Current State Analysis

The unified skill currently exposes `--domain` as a simple framing lens in [skills/describe-well/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/describe-well/SKILL.md#L18), with examples like `mathematical`, `literary`, and `technical`. That lens is only applied inside the precision engine stage in [skills/describe-well/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/describe-well/SKILL.md#L85), so the current system has no explicit mechanism for deciding when text is over-specified or under-specified for a given audience.

The same flat model appears in the standalone rewrite skill at [skills/precise/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/precise/SKILL.md#L13), and the public repo summary in [skills/README.md](/Users/hq/github_projects/ultimate-describer/skills/README.md#L12) still describes the system as a 5-stage pipeline without a separate context-calibration layer.

The eval system measures output quality after the fact but does not score audience calibration directly. The prompt-side evaluator defines 10 metrics in [skills/eval/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/eval/SKILL.md#L32), and the scripted evaluator implements them in [eval.py](/Users/hq/github_projects/ultimate-describer/eval.py#L80). The test corpus in [tests.json](/Users/hq/github_projects/ultimate-describer/tests.json#L1) contains `purpose` and occasional `audience`, but no structured audience profile, no domain constraint sets, and no precision ceiling metadata.

## Desired End State

`describe-well` should contain an explicit Layer 2 context-calibration section between mode detection and precision generation. That layer should:

- model audience context with four dimensions:
  - domain fluency
  - attention budget
  - epistemic stance
  - action orientation
- derive concrete calibration targets from those dimensions:
  - vocabulary ceiling
  - compression target
  - evidence threshold
  - differentiation pressure
- define domain-specific constraint sets:
  - required terms
  - forbidden terms
  - precision ceilings
- explain how interaction rules override naive per-axis recommendations
- expose enough structure that evals can score whether a rewrite is appropriately calibrated, not just generally precise

Verification of the desired end state means:

- the prompt architecture in `describe-well` explicitly names the context-calibration layer and its decision rules
- reusable calibration references exist on disk and are linked from the skill
- the test corpus contains context metadata needed to evaluate calibration
- the eval prompt and script can score vocabulary match, calibration fit, and constraint compliance

### Key Discoveries

- The unified skill already has a stage-based orchestrator structure that can absorb a new Layer 2 without changing the repo’s overall architecture: [skills/describe-well/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/describe-well/SKILL.md#L36).
- The current `--domain` flag is too weakly specified to support deterministic calibration, because it only provides stylistic framing and not audience-fit logic: [skills/describe-well/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/describe-well/SKILL.md#L32).
- The evaluator is already organized as one function per metric with a shared aggregation layer, so adding calibration metrics fits the existing pattern cleanly: [eval.py](/Users/hq/github_projects/ultimate-describer/eval.py#L80), [eval.py](/Users/hq/github_projects/ultimate-describer/eval.py#L444), [eval.py](/Users/hq/github_projects/ultimate-describer/eval.py#L498).

## What We're NOT Doing

- Building a separate `context-calibration` skill as the primary implementation vehicle
- Replacing the current skill system with a code-driven runtime
- Solving automatic inference of all audience dimensions from arbitrary external context
- Building a production-grade NLP classifier for jargon or precision ceilings in the first pass
- Refactoring unrelated skills like `crossling` or `precise-calibrate` beyond what is required for consistency

## Implementation Approach

Treat context calibration as an explicit intermediate layer in the prompt architecture, then externalize detailed domain knowledge into references so `SKILL.md` stays procedural. After the prompt structure is upgraded, expand the test schema and eval stack to make the layer observable. This sequence keeps the conceptual model coherent while avoiding the trap of introducing theory that the repo cannot validate.

## Phase 1: Refactor The Unified Prompt Architecture

### Overview

Upgrade `describe-well` from a 5-stage prompt pipeline with a flat `--domain` flag into a 6-stage pipeline with a first-class context-calibration layer.

### Changes Required:

#### 1. Unified Skill Prompt
**File**: `skills/describe-well/SKILL.md`
**Changes**:
- Replace the current `--domain` flag description with a broader context model section
- Add an explicit Layer 2 or `context calibration` section after mode detection
- Define the four dimensions and derived calibration targets
- Add interaction rules showing how combinations of dimensions change rewrite behavior
- Move old framing examples into either preset profiles or calibration behaviors
- Update the output format so the precision report includes a short calibration summary

```md
### stage 3: context calibration

map the request to a calibration profile across four dimensions:
- domain fluency (0-10)
- attention budget (0-10 or low/medium/high mapped to anchors)
- epistemic stance (0-10)
- action orientation (0-10)

derive:
- vocabulary ceiling
- compression target
- evidence threshold
- differentiation pressure

scan for calibration mismatches:
- jargon above fluency ceiling
- wording below fluency floor
- claims below evidence threshold
- details above precision ceiling
- missing required terms
- forbidden terms present
```

#### 2. Standalone Rewrite Skill Alignment
**File**: `skills/precise/SKILL.md`
**Changes**:
- Replace the flat `--domain` framing-lens description with lighter-weight context calibration wording
- Clarify that `precise` uses the same calibration principles as `describe-well`, but only in rewrite mode

#### 3. Standalone Generative Skill Alignment
**File**: `skills/describe/SKILL.md`
**Changes**:
- Add the same audience-calibration concepts so generated descriptions and unified descriptions do not diverge conceptually
- Clarify how purpose and audience interact with the new calibration targets

### Success Criteria:

#### Automated Verification:
- [x] `rg -n "context calibration|domain fluency|attention budget|epistemic stance|action orientation" skills` returns matches in the intended skill files
- [x] `rg -n "framing lens" skills/describe-well/SKILL.md skills/precise/SKILL.md skills/describe/SKILL.md` returns no stale phrasing where the new model should replace it

#### Manual Verification:
- [ ] Reading `describe-well` top to bottom shows a clear stage order with context calibration preceding precision generation
- [ ] The four dimensions are defined precisely enough that two engineers would likely produce similar rewrites for the same profile
- [ ] The output report clearly communicates not just what changed, but why it was calibrated that way

**Implementation Note**: After completing this phase and verification, pause for manual review of the prompt architecture before touching test or eval code.

---

## Phase 2: Add Reusable Context References

### Overview

Move the detailed audience and domain model into reference files so the skill can stay concise while still exposing a rigorous calibration system.

### Changes Required:

#### 1. Audience Axes Reference
**File**: `skills/describe-well/references/context-axes.md`
**Changes**:
- Define the four dimensions with scoring anchors from 0-10
- Describe what each dimension controls in output behavior
- Document the derived calibration targets
- Include a compact interaction table for common pairings

```md
## domain fluency
- 0-1: child / uninformed general reader
- 2-3: journalist / broad educated audience
- 4-6: practitioner
- 7-8: specialized professional
- 9-10: expert evaluator

## derived targets
- vocabulary ceiling
- definition burden
- acceptable jargon density
```

#### 2. Domain Profile Reference
**File**: `skills/describe-well/references/domain-profiles.md`
**Changes**:
- Add starter profiles for:
  - `vc_pitch`
  - `technical_docs`
  - `blog_post`
- For each profile, document:
  - default four-axis tuple
  - required terms
  - forbidden terms
  - precision ceiling rules
  - “never do this” guidance

#### 3. Example Calibration Reference
**File**: `skills/describe-well/references/examples.md`
**Changes**:
- Add before/after examples for the same input rewritten for different profiles
- Include at least one over-precision correction and one under-precision correction

### Success Criteria:

#### Automated Verification:
- [x] `find skills/describe-well/references -type f` shows all planned reference files
- [x] `rg -n "vc_pitch|technical_docs|blog_post" skills/describe-well/references/domain-profiles.md` confirms the starter profiles exist

#### Manual Verification:
- [ ] `skills/describe-well/SKILL.md` explicitly points to each new reference file
- [ ] The reference docs are specific enough to guide implementation without duplicating the full prompt
- [ ] The examples show noticeable behavioral differences across audience/context combinations

**Implementation Note**: After completing this phase, pause for human review of the profile definitions before encoding them into tests and evals.

---

## Phase 3: Expand The Test Schema For Calibration

### Overview

Add the structured metadata needed to evaluate context calibration instead of relying on loosely implied `audience` and `purpose` fields.

### Changes Required:

#### 1. Test Corpus Schema Upgrade
**File**: `tests.json`
**Changes**:
- Add optional structured fields for calibration-aware cases:
  - `audience_profile`
  - `domain_profile`
  - `required_terms`
  - `forbidden_terms`
  - `precision_ceiling`
  - `expected_calibration`
- Preserve compatibility with current cases while adding new calibration-focused cases

```json
{
  "audience_profile": {
    "domain_fluency": 7,
    "attention_budget": 4,
    "epistemic_stance": 8,
    "action_orientation": 9
  },
  "domain_profile": "vc_pitch",
  "required_terms": ["runway", "burn rate"],
  "forbidden_terms": ["hopefully", "maybe"],
  "precision_ceiling": {
    "numbers_sig_figs": 2,
    "time_granularity": "quarter"
  },
  "expected_calibration": "matched"
}
```

#### 2. Calibration Test Coverage
**File**: `tests.json`
**Changes**:
- Add new cases covering:
  - same input, multiple audience profiles
  - over-precise text for low-attention contexts
  - under-precise text for skeptical decision-makers
  - forbidden-term detection in a VC-style pitch
  - jargon mismatch against low domain fluency

### Success Criteria:

#### Automated Verification:
- [x] `python -m json.tool tests.json >/dev/null` succeeds
- [x] Existing eval workflows still parse `tests.json` without schema errors

#### Manual Verification:
- [ ] Each new test case makes the expected calibration target obvious from the metadata
- [ ] The new cases cover both under-specification and over-specification, not just one direction

**Implementation Note**: After this phase, pause to review the test matrix before writing new eval metrics against it.

---

## Phase 4: Extend The Eval Prompt Contract

### Overview

Teach the interactive `/eval` skill how to judge context calibration directly, not just generic precision.

### Changes Required:

#### 1. Eval Skill Prompt Update
**File**: `skills/eval/SKILL.md`
**Changes**:
- Extend the accepted test-case schema description with calibration fields
- Add new metrics:
  - vocabulary match
  - precision calibration
  - constraint compliance
  - evidence calibration
  - compression fit
- Update output format to report calibration-specific results and aggregate scores

```md
### 11. vocabulary match
does the text assume the right level of domain fluency for the target audience?

### 12. precision calibration
is the text under-specified, matched, or over-specified for this audience and domain?

### 13. constraint compliance
are required terms present, forbidden terms absent, and domain-specific conventions respected?
```

### Success Criteria:

#### Automated Verification:
- [x] `rg -n "vocabulary match|precision calibration|constraint compliance|evidence calibration|compression fit" skills/eval/SKILL.md` returns the new metric definitions

#### Manual Verification:
- [ ] The eval prompt can explain why a text is over-precise for one audience and under-precise for another
- [ ] The output format stays readable and does not collapse calibration into a single vague score

**Implementation Note**: Review the prompt wording before implementing the scripted metrics so the Python runner and prompt-side eval stay aligned.

---

## Phase 5: Extend The Scripted Evaluator

### Overview

Add calibration-aware metrics to the batch evaluator in `eval.py` and preserve the current metric-per-function structure.

### Changes Required:

#### 1. Metric Registration
**File**: `eval.py`
**Changes**:
- Extend `ALL_METRICS` and `METRIC_FUNCS`
- Add aggregation logic for the new metrics

#### 2. New Metric Functions
**File**: `eval.py`
**Changes**:
- Add functions following the current pattern:
  - `eval_vocabulary_match`
  - `eval_precision_calibration`
  - `eval_constraint_compliance`
  - `eval_evidence_calibration`
  - `eval_compression_fit`
- Each function should:
  - skip gracefully if required metadata is missing
  - use the shared `judge()` helper
  - return per-case structured scores compatible with `aggregate()`

```py
def eval_precision_calibration(cases, repeats=1):
    scored_cases = [tc for tc in cases if tc.get("audience_profile") and tc.get("expected_calibration")]
    ...
    return scores
```

#### 3. Summary Logic
**File**: `eval.py`
**Changes**:
- Ensure the summary extraction logic includes the new metrics
- Preserve current output compatibility for existing runs

### Success Criteria:

#### Automated Verification:
- [ ] `python eval.py --test-cases tests.json --metrics precision_calibration --output /tmp/context-calibration-results.json` runs successfully when `ANTHROPIC_API_KEY` is set
- [ ] `python eval.py --test-cases tests.json --metrics vocabulary_match,constraint_compliance --output /tmp/context-calibration-results.json` runs successfully when `ANTHROPIC_API_KEY` is set
- [x] Existing metrics like `precision_vector` and `coherence` still run unchanged

#### Manual Verification:
- [ ] Per-case eval output explains calibration failures in concrete terms, not just numeric scores
- [ ] Aggregate output distinguishes between missing metadata and genuine low performance

**Implementation Note**: Do not remove the current metrics. Calibration metrics should extend the evaluator, not replace the baseline precision metrics.

---

## Phase 6: Align Repo Documentation

### Overview

Update the human-facing docs so the repo description matches the new architecture and examples.

### Changes Required:

#### 1. Skills Index
**File**: `skills/README.md`
**Changes**:
- Replace references to a generic `domain` lens with context calibration language
- Update the pipeline summary from 5 stages to 6 stages
- Add a concise explanation of the four dimensions and precision ceilings
- Update examples if needed to demonstrate audience-specific rewrites

#### 2. Top-Level Repo Note
**File**: `README.md`
**Changes**:
- Expand the current one-line note if needed so it reflects the repo’s context-calibration purpose rather than only “describe things well”

### Success Criteria:

#### Automated Verification:
- [x] `rg -n "framing lens|5-stage pipeline" README.md skills/README.md` shows no stale language if those concepts were replaced
- [x] `rg -n "context calibration|precision ceiling|domain fluency" skills/README.md README.md` returns updated documentation matches

#### Manual Verification:
- [ ] A new reader can understand the difference between raw precision and context-calibrated precision from the docs alone
- [ ] The examples in the docs visibly differ by audience/domain rather than just by wording style

**Implementation Note**: This phase should be last so docs describe the final behavior, not an intermediate state.

---

## Testing Strategy

### Unit Tests:

- Validate `tests.json` schema consistency by parsing it after each change
- Exercise each new eval metric in isolation with a minimal metric list
- Confirm `aggregate()` handles empty calibration subsets without crashing

### Integration Tests:

- Run `eval.py` on the full test corpus with the new calibration metrics enabled
- Run mixed metric suites combining old and new metrics to ensure summary generation still works
- Verify prompt-side `/eval` instructions and scripted `eval.py` remain semantically aligned

### Manual Testing Steps:

1. Read `skills/describe-well/SKILL.md` and confirm the pipeline now explicitly includes context calibration before precision generation.
2. Compare the same sample input against at least two preset profiles in `references/examples.md` and verify the output changes in vocabulary, evidence level, and density.
3. Run the calibration-aware eval metrics and inspect whether failures are explained as over-precision, under-precision, or constraint violations.
4. Confirm the standalone `precise` and `describe` skills still read coherently and do not contradict the unified skill’s model.

## Performance Considerations

The main cost increase is evaluator token usage. Adding calibration metrics to `eval.py` will increase the number of Anthropic judge calls per test run. Mitigate this by:

- keeping each new metric narrowly scoped
- skipping cases without required metadata
- preserving the existing `--metrics` flag so partial runs remain cheap
- using `--repeats` selectively rather than by default

Prompt-size growth is the second cost. Keep `SKILL.md` procedural and move detailed domain/profile content into `references/` to avoid unnecessary context bloat.

## Migration Notes

- Maintain backward compatibility for existing test cases that only include `purpose` and `audience`
- Treat the new calibration metadata as optional at first so the old eval suite continues to run
- Keep the old conceptual behavior of “make language more precise” while adding the new concept of “fit the right level of precision to the audience”
- If `--domain` remains user-facing for compatibility, reinterpret it as a shortcut into domain profiles rather than a free-floating stylistic lens

## References

- Original concept discussion: current chat context
- Unified skill: [skills/describe-well/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/describe-well/SKILL.md)
- Rewrite skill: [skills/precise/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/precise/SKILL.md)
- Generative skill: [skills/describe/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/describe/SKILL.md)
- Eval skill: [skills/eval/SKILL.md](/Users/hq/github_projects/ultimate-describer/skills/eval/SKILL.md)
- Scripted evaluator: [eval.py](/Users/hq/github_projects/ultimate-describer/eval.py)
- Current test corpus: [tests.json](/Users/hq/github_projects/ultimate-describer/tests.json)
