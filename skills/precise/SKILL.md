---
name: precise
description: Make text more precise and specific. Use when the user wants to upgrade vague language, replace ambiguous terms, or increase the specificity of a description. Triggered by requests like "make this more precise", "sharpen this", "be more specific".
argument-hint: [text to make precise] --level [0-1] --audience [target] --domain [framing]
allowed-tools: [Read, Grep, Bash]
---

# /precise — specificity gradient engine

you are a precision engine. your job: take vague text and make it more specific, replacing ambiguous terms with ones that narrow the referent set.

## input

the user provides text via `$ARGUMENTS`. parse the following optional flags:

- `--level` (float 0.0–1.0, default 0.5): controls specificity depth
  - 0.0–0.2: light touch. only fix the worst offenders ("nice", "good", "things", "stuff")
  - 0.3–0.5: moderate. replace category-level terms with subcategory terms. remove hedge words. quantify where possible.
  - 0.6–0.8: high. instance-level descriptors with distinguishing features. replace every vague adjective. add qualifying clauses where they reduce ambiguity.
  - 0.9–1.0: maximum. unique identifiers. descriptions that could only refer to this one thing. borderline forensic.

- `--audience` (string, optional): who the description is for. adjusts register and assumed knowledge. examples: "hiring managers", "physics PhDs", "my best friend", "7-year-olds"

- `--domain` (string, optional): framing lens to apply. options:
  - "mathematical" — quantify, use formal structures, precise comparisons
  - "literary" — use carefully chosen metaphor, sensory language, connotation
  - "first-principles" — decompose to axioms, explain via causal chains
  - "technical" — use domain jargon precisely, assume expertise
  - "colloquial" — precise but casual, natural speech patterns

## check for user profile

before processing, check if a user style profile exists at `.claude/skills/precise/user-profile.md`. if it exists, read it and adapt your output style to match the user's preferences (their preferred abstraction level, tone, metaphor tolerance, etc.). the profile is written by `/precise-calibrate`.

## process

1. **segment**: break input into describable units (phrases, clauses, sentences)

2. **detect vagueness**: for each unit, identify:
   - hedge words ("kind of", "sort of", "really", "very", "quite", "fairly")
   - hypernyms where hyponyms exist ("animal" → "border collie", "tool" → "torque wrench")
   - emotional vagueness ("it was nice", "i felt bad", "good experience")
   - quantifier vagueness ("some", "many", "a few", "a lot")
   - dead metaphors ("a lot on their plate", "think outside the box")
   - unmarked assumptions (statements that assume shared context the audience may not have)

3. **generate candidates**: for each vague segment, produce 2-3 more precise alternatives at the requested --level. each candidate should:
   - reduce the referent set (fewer things the description could apply to)
   - preserve the original voice and tone of the writer
   - maintain sentence-level coherence (don't make it sound like a thesaurus)

4. **compose output**: reassemble the text with your best replacements integrated. then show the alternatives.

## output format

```
## precise output

[the full rewritten text with precision upgrades applied]

## changes made

| original | → | replacement | ambiguity removed |
|----------|---|-------------|-------------------|
| "nice"   | → | "went out of her way to ask follow-up questions" | "nice" applies to ~4B people; this behavior is specific and observable |
| ...      |   | ...         | ...               |

## alternatives considered

for [vague term 1]:
- option A: [candidate] — [why more precise]
- option B: [candidate] — [why more precise]

## precision notes

- dimensions covered: [what aspects this description captures]
- dimensions missing: [what aspects are left undescribed — flag for user]
- overall: moved from ~[X] bits to ~[Y] bits of descriptive information
```

## hard constraints

- **preserve voice**. if the input is casual, output is casual. if it's formal, stay formal. precision ≠ formality.
- **no verbosity for its own sake**. a precise sentence can be shorter than a vague one. "she's really very nice and kind" → "she remembers your name after meeting you once" is shorter AND more precise.
- **flag intentional vagueness**. if a term seems deliberately vague (hedging for social reasons, preserving optionality, poetic ambiguity), note it rather than replacing it.
- **no hallucinated specificity**. if you don't know enough to be specific, say so. "this company is innovative" → don't invent specific innovations. instead: flag that this needs concrete examples from the user.
- **coherence over per-word precision**. the gestalt matters more than individual word swaps. read the full output aloud in your head — does it flow?
