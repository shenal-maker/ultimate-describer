---
name: precise-calibrate
description: Calibrate your language precision preferences. Use when the user wants to set up their style profile, take the precision quiz, or configure how /precise adapts to them. Triggered by "calibrate", "set up my profile", "learn my style".
argument-hint: [optional: path to writing sample]
allowed-tools: [Read, Write, Bash]
---

# /precise-calibrate — style profile builder

you run an adaptive quiz to learn how the user likes things described. the output is a style profile saved to `.claude/skills/precise/user-profile.md` that `/precise` reads on every invocation.

## mode 1: quiz (default, no arguments)

run exactly 5 rounds. each round:

1. present a **scenario** (describing a person, a company, an experience, an idea, or a place)
2. show **3 descriptions** of the same thing, each in a distinctly different style:
   - one abstract/conceptual
   - one concrete/sensory/specific
   - one structured/analytical
   vary the exact styles across rounds — don't repeat the same three archetypes.
3. ask: "which one do you like best? (1/2/3)"
4. use the answer to update your model of the user's preferences

### what you're inferring (axes)

- **abstract ↔ concrete**: do they prefer "a liminal space" or "the hallway between the kitchen and the back door where nobody ever turns the light on"?
- **emotional ↔ analytical**: "it felt like the air had been punched out of the room" vs "morale dropped 40% in Q3 based on pulse survey data"
- **terse ↔ elaborate**: "sharp. relentless. right." vs a full paragraph
- **formal ↔ colloquial**: "the organization demonstrated resilience" vs "they just refused to die"
- **metaphorical ↔ literal**: "a cathedral of code" vs "a well-structured 50k-line codebase with clear module boundaries"

### adaptive selection

each question should maximize information gain. if the first two answers both lean concrete, don't ask another concrete-vs-abstract question — probe a different axis (terse vs elaborate, metaphorical vs literal).

after round 5, present the inferred profile to the user for confirmation.

## mode 2: writing sample (argument provided)

if the user provides a path to a writing sample via `$ARGUMENTS`:

1. read the file
2. analyze: sentence length distribution, adjective density, abstraction level, metaphor frequency, formality markers, terse-vs-elaborate ratio
3. infer the same 5-axis profile
4. present to user for confirmation/adjustment

## output: user profile

after confirmation, write the profile to `.claude/skills/precise/user-profile.md`:

```markdown
---
name: user-precision-profile
description: style preferences for /precise output calibration
type: user
---

## precision style profile

- abstract ↔ concrete: [score 0-1, where 0 = fully abstract, 1 = fully concrete]
- emotional ↔ analytical: [score 0-1]
- terse ↔ elaborate: [score 0-1]
- formal ↔ colloquial: [score 0-1]
- metaphorical ↔ literal: [score 0-1]

## interpretation

[2-3 sentences describing what this profile means in plain language. e.g., "you prefer descriptions that are concrete and terse — you'd rather hear one precise detail than three abstract adjectives. you're comfortable with metaphor when it earns its keep but don't want ornamental flourish."]

## calibration data

[list the quiz answers or writing sample analysis that produced this profile]
```

## hard constraints

- **5 questions max in quiz mode**. respect the user's time. if you can infer with high confidence in 3, stop early.
- **no psychoanalysis**. you're inferring description preferences, not personality. keep it about language.
- **the profile is a starting point**. tell the user they can re-run `/precise-calibrate` anytime or manually edit the profile file.
- **make the quiz interesting**. the descriptions should be genuinely well-written and distinct. the user should enjoy the process, not endure it.
