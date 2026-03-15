# language precision skills

## `/describe-well` - the unified skill

one command that runs the full pipeline. it auto-detects whether you're editing existing text or describing something new, checks your style profile, calibrates the output to audience and domain context, upgrades precision, and adds cross-lingual terms only when they genuinely help.

```
/describe-well "she's a really nice person who does interesting work" --level 0.8
/describe-well "my cofounder" --purpose "investor pitch" --audience "YC partners" --domain vc_pitch
/describe-well "the feeling when a great idea surfaces mid-conversation and immediately evaporates"
```

### flags

- `--level` (0-1, default 0.6): specificity depth. 0.2 = light touch. 0.8 = instance-level. 1.0 = forensic.
- `--audience`: who is reading. helps infer domain fluency, attention budget, epistemic stance, and action orientation.
- `--purpose`: what the description is for. changes which dimensions matter and how much evidence or compression is needed.
- `--domain`: compatibility shortcut into a domain profile such as `vc_pitch`, `technical_docs`, or `blog_post`.

### what it does (6-stage pipeline)

1. **profile check** - reads your style preferences or runs a fast 1-question calibration on first use
2. **mode detection** - auto-detects editing vs generative mode and maps salient subject dimensions
3. **context calibration** - sets domain fluency, attention budget, epistemic stance, and action orientation, then derives a vocabulary ceiling, compression target, evidence threshold, and differentiation pressure
4. **precision engine** - replaces vague terms and generates sharper descriptions inside the calibration envelope
5. **cross-lingual enrichment** - surfaces terms from other languages only when they genuinely add precision
6. **output assembly** - returns the result with a calibration summary, change table, dimension coverage, and alternatives considered

### why calibration matters

raw precision asks: "can this sentence be made narrower?"

context-calibrated precision asks: "what is the narrowest useful sentence for this audience, purpose, and domain?"

that distinction prevents two common failures:
- over-precision: technically sharp language that exceeds the reader's fluency or patience
- under-precision: vague language that fails a skeptical or decision-oriented reader

### reference files

- `skills/describe-well/references/context-axes.md`
- `skills/describe-well/references/domain-profiles.md`
- `skills/describe-well/references/examples.md`

---

## individual skills

the pipeline stages are also available as standalone skills for when you want just one piece.

### `/precise` - rewrite mode only

takes existing text and upgrades vague terms using the same calibration model as `/describe-well`.

```
/precise "the company has a great culture" --level 0.7 --audience "job candidates"
```

### `/precise-calibrate` - full style calibration

5-round adaptive quiz or writing sample analysis. builds a detailed profile across 5 stylistic axes: abstract<->concrete, emotional<->analytical, terse<->elaborate, formal<->colloquial, metaphorical<->literal.

use this when you want a thorough style calibration instead of the 1-question fast version built into `/describe-well`.

```
/precise-calibrate
/precise-calibrate path/to/my-writing-sample.md
```

### `/describe` - generative descriptions only

generates descriptions from scratch for a subject while using the same audience-calibration model as the unified skill.

```
/describe "the mass resignation at Twitter post-acquisition" --purpose "case study" --audience "operators" --domain blog_post
```

### `/crossling` - cross-lingual search only

finds terms from other languages that capture a concept more precisely than english. includes confidence ratings and flags when english already works fine.

```
/crossling "the satisfaction of watching someone get what they deserve"
```

## evaluation

### `/eval` - precision evaluator

scores outputs across 15 metrics. the original metrics still measure precision quality directly, and the new calibration metrics measure whether the precision is audience-fit.

```
/eval tests.json
/eval "she's nice" "she remembers your coffee order"
/eval "she remembers your coffee order after meeting you once"
```

measures:
- referent reduction
- sentence self-check
- information density
- discriminability
- precision vector
- voice preservation
- coherence
- vagueness detection
- cross-lingual validation
- audience adaptation
- vocabulary match
- precision calibration
- constraint compliance
- evidence calibration
- compression fit

there is also an `eval.py` script in the repo root for automated batch runs via the API. it still supports the old metrics and now adds calibration-aware metrics when metadata is present.

## personalization

`/precise-calibrate` or the first run of `/describe-well` writes a style profile to `.claude/skills/precise/user-profile.md`. all skills read it automatically.
