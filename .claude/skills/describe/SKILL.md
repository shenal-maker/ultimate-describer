---
name: describe
description: Generate a precise description of a subject (person, company, experience, idea, place). Use when the user wants to describe something well, write a description for a specific purpose, or capture what makes something distinctive. Triggered by "describe", "write a description of", "how would you describe".
argument-hint: [subject] --purpose [context] --level [0-1] --audience [target]
allowed-tools: [Read, Grep, Bash]
---

# /describe — precision description generator

you generate descriptions that capture what makes the subject *distinctive* — what's true of this thing and not true of similar things.

## input

`$ARGUMENTS` contains the subject to describe. parse optional flags:

- `--purpose` (string, optional): what the description is for. this is the most important flag — it determines which dimensions matter.
  - "job application" → emphasize competence, track record, distinguishing skills
  - "investor pitch" → emphasize traction, market insight, team capability
  - "personal journal" → emphasize felt experience, honest self-reflection
  - "introducing to a friend" → emphasize personality, energy, what they'd notice
  - "dating profile" → emphasize distinctiveness, specificity, what spending time with them is like
  - freeform: user can write anything

- `--level` (float 0.0–1.0, default 0.6): same precision scale as /precise

- `--audience` (string, optional): who will read this description

## check for user profile

read `.claude/skills/precise/user-profile.md` if it exists. adapt output style to the user's calibrated preferences.

## process

1. **identify the subject type**: person, company, experience, idea, place, skill, emotion, relationship, other

2. **map salient dimensions** for that subject type:
   - person: behavior patterns, competencies, energy, values, quirks, how they make others feel
   - company: what they actually do (not what they say they do), culture, trajectory, market position, distinctive choices
   - experience: sensory details, emotional arc, before/after delta, what you'd tell someone who wasn't there
   - idea: core mechanism, why it's non-obvious, what it predicts, what it replaces, boundary conditions
   - place: atmosphere, what you notice first, what you notice after 10 minutes, who belongs there
   - skill: when to use it, what changes in the output, when NOT to use it, learning curve shape
   - emotion: physical sensation, trigger pattern, duration, what it makes you want to do, nearest-neighbor emotions it's NOT

3. **filter by purpose**: given the --purpose, which dimensions matter most? rank them. a job application doesn't need "quirks" but does need "competencies."

4. **generate at requested precision level**: apply the same 0.0–1.0 scale from /precise. at higher levels, replace every general term with a specific one.

5. **self-check**: for each sentence, ask: "could this sentence describe something else equally well?" if yes, it's not precise enough. revise.

## output format

```
## description

[the description itself — polished, precise, in the user's preferred style]

## anatomy

- dimensions covered: [list]
- dimensions omitted (and why): [list — "omitted X because not relevant to stated purpose"]
- precision level achieved: [self-assessment]
- distinguishing power: [what makes this description pick out THIS subject vs similar ones]
```

## hard constraints

- **the self-check is mandatory**. every sentence must pass "could this describe something else?" if it could, either make it more specific or flag it.
- **no résumé-speak**. "dynamic self-starter with a passion for innovation" is the opposite of precise. it describes everyone and therefore no one.
- **no flattery unless warranted by evidence**. "brilliant" is vague praise. "published three papers that changed how the field thinks about X" is precise praise.
- **preserve what the user gives you**. if they provide details about the subject, USE those details. don't replace their specifics with your generics.
- **flag information gaps**. if you can't be precise because you don't have enough information, say exactly what you'd need to know. "to make this more precise, i'd need to know: [specific questions]"
- **the description should teach the reader something**. after reading it, they should understand the subject better than before — not just have a vague positive/negative impression.
