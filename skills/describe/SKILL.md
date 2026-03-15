---
name: describe
description: Generate a precise description of a subject (person, company, experience, idea, place). Use when the user wants to describe something well, write a description for a specific purpose, or capture what makes something distinctive. Triggered by "describe", "write a description of", "how would you describe".
argument-hint: [subject] --purpose [context] --level [0-1] --audience [target] --domain [profile]
allowed-tools: [Read, Grep, Bash]
---

# /describe - precision description generator

you generate descriptions that capture what makes the subject distinctive: what is true of this thing and not true of similar things, at the right level for the reader.

## input

`$ARGUMENTS` contains the subject to describe. parse optional flags:

- `--purpose` (string, optional): what the description is for. this is the most important flag because it determines which dimensions matter.
  - "job application" -> emphasize competence, track record, distinguishing skills
  - "investor pitch" -> emphasize traction, market insight, team capability
  - "personal journal" -> emphasize felt experience, honest self-reflection
  - "introducing to a friend" -> emphasize personality, energy, what they would notice
  - "dating profile" -> emphasize distinctiveness, specificity, what spending time with them is like
  - freeform is allowed

- `--level` (float 0.0-1.0, default 0.6): same precision scale as `/precise`

- `--audience` (string, optional): who will read this description

- `--domain` (string, optional): compatibility shortcut into a domain profile or constraint set. use it to infer terminology expectations, forbidden phrasing, and any precision ceiling that should limit over-specification.

## check for user profile

read `.claude/skills/precise/user-profile.md` if it exists. adapt output style to the user's calibrated preferences.

## process

1. **identify the subject type**: person, company, experience, idea, place, skill, emotion, relationship, other

2. **map salient dimensions** for that subject type:
   - person: behavior patterns, competencies, energy, values, quirks, how they make others feel
   - company: what they actually do, culture, trajectory, market position, distinctive choices
   - experience: sensory details, emotional arc, before and after delta, what you would tell someone who was not there
   - idea: core mechanism, why it is non-obvious, what it predicts, what it replaces, boundary conditions
   - place: atmosphere, what you notice first, what you notice after 10 minutes, who belongs there
   - skill: when to use it, what changes in the output, when not to use it, learning curve shape
   - emotion: physical sensation, trigger pattern, duration, what it makes you want to do, nearest-neighbor emotions it is not

3. **filter by purpose**: given the `--purpose`, rank which dimensions matter most.

4. **context calibration**: before drafting, map the audience and purpose to four dimensions:
   - domain fluency
   - attention budget
   - epistemic stance
   - action orientation

   derive:
   - vocabulary ceiling
   - compression target
   - evidence threshold
   - differentiation pressure

   apply interaction rules:
   - low fluency lowers jargon tolerance even if the topic is technical
   - high epistemic stance increases the evidence burden for claims
   - high action orientation increases the need for clear comparisons and consequences
   - low attention budget favors concise, high-signal distinctions over exhaustive coverage

   if `--domain` is provided, treat it as a domain profile shortcut that can impose required terms, forbidden terms, and precision ceilings.

5. **generate at requested precision level**: apply the same 0.0-1.0 scale from `/precise`. at higher levels, replace every general term with a specific one, but never exceed the calibration targets.

6. **self-check**: for each sentence, ask: "could this sentence describe something else equally well?" if yes, revise. also ask: "is this sentence calibrated for this audience, or merely more detailed?"

## output format

```
## description

[the description itself - polished, precise, in the user's preferred style]

## anatomy

- calibration summary: [audience profile, derived targets, and any domain-profile constraints applied]
- dimensions covered: [list]
- dimensions omitted (and why): [list]
- precision level achieved: [self-assessment]
- distinguishing power: [what makes this description pick out this subject vs similar ones]
```

## hard constraints

- **the self-check is mandatory**. every sentence must pass "could this describe something else?"
- **no resume-speak**. generic praise is the opposite of precise.
- **no flattery unless warranted by evidence**.
- **preserve what the user gives you**. do not replace their specifics with generic filler.
- **flag information gaps**. if you cannot be precise because you lack information, say exactly what you need.
- **the description should teach the reader something**.
- **fit the audience, not an abstract ideal**. precision that exceeds the reader's fluency, patience, or evidence expectations is a calibration failure.
