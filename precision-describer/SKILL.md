---
name: precision-describer
description: Rewrite vague or underspecified text into more precise language. Use when the user wants sharper wording, audience-calibrated descriptions, better term choice, tone calibration, domain-specific phrasing, or side-by-side alternatives ranked from vague to precise. Do not use for factual research, pure grammar correction, or longform copy generation unless improving specificity is the core task.
---

# Precision Describer

## Use this skill when

Use this skill when the user wants to:
- replace vague, overloaded, or ambiguous terms
- adapt wording for a specific audience, culture, or domain
- compare alternative phrasings by precision level
- tune emotional register or stylistic feel without losing meaning
- learn how to describe something better, not only receive a rewrite

Do not use this skill when:
- the task is mainly factual lookup or research
- the task is mainly proofreading or grammar correction
- the user wants broad brainstorming where precision is not the goal
- the user primarily wants image or video generation rather than wording work

## Core workflow

1. identify vague, overloaded, or underspecified terms in the source text
2. infer the precision target:
   - what is being described
   - who the description is for
   - what kind of precision matters most: technical, sensory, emotional, cultural, evaluative, or comparative
3. generate alternatives along a specificity spectrum from broader to narrower
4. rank or label the options by specificity and note the tradeoff briefly
5. choose the narrowest useful output mode for the request

## Specificity axis

When ranking options, prefer this order:
1. less ambiguous
2. more concrete
3. more audience-appropriate
4. more domain-accurate
5. more emotionally calibrated
6. more stylistically aligned with the user's stated or inferred preferences

Do not assume the most technical phrasing is always best. Precision is contextual.

## Context calibration

Check these dimensions when they matter:
- audience: expert, peer, recruiter, student, customer, fan community
- domain: literary, mathematical, technical, colloquial, artistic, commercial
- cultural context: idiom, community norms, connotation
- emotional register: neutral, warm, intense, restrained, playful, formal

Read the relevant references only when needed:
- `references/context-calibration.md`
- `references/domain-vocab.md`
- `references/cross-language.md`

## Personalization

If the user has clear preferences, prioritize them over generic elegance.

Personalization signals can come from:
- explicit user instructions
- examples of the user's writing
- comparative selections such as "which do you like better?"
- requested words, phrases, or stylistic constraints

If personalization is important, read:
- `references/personalization.md`

## Output modes

Choose the narrowest useful output mode:
- `inline`: direct term swaps inside the source
- `spectrum`: options ordered from vague to precise
- `calibrated rewrite`: rewrite for a stated audience or domain
- `comparison`: 2-5 variants with tradeoffs
- `teaching`: explain why one description is stronger
- `teaching-annotations`: return machine-readable span annotations for an external renderer or inline teaching UI

Use `teaching-annotations` when:
- the user wants inline critique instead of a rewritten paragraph
- another tool needs exact spans in the source text
- the instructive moment should be rendered in a UI rather than explained only in prose

For `teaching-annotations`, return JSON with this shape:

```json
{
  "text": "original source text",
  "annotations": [
    {
      "start": 0,
      "end": 7,
      "label": "phrase being flagged",
      "why": "why this weakens precision",
      "try": "what kind of wording would be stronger"
    }
  ]
}
```

Rules for `teaching-annotations`:
- `text` must reproduce the original source text exactly
- `start` and `end` must be 0-based character offsets into `text`
- spans must be non-overlapping and ordered from left to right
- `label` should usually match the flagged span exactly unless a shorter display label is clearer
- `why` should explain the weakness, not just rename it
- `try` should guide a stronger rewrite without silently rewriting the whole passage
- if precision depends on ambiguity in the source, annotate the ambiguous span and say what is unclear
- if no specific spans are worth flagging, return an empty `annotations` array instead of inventing issues

## Response rules

- preserve original meaning unless the user asks for reframing
- avoid thesaurus spam; each alternative should reflect a real shift in meaning, register, or audience fit
- if precision depends on missing context, say what is missing
- if multiple interpretations are plausible, surface them rather than pretending certainty
- stay brief unless the user asks for analysis
- when using `teaching-annotations`, output valid JSON only unless the user explicitly asks for commentary around it

## Evaluation mode

Only enter evaluation mode if the user explicitly asks to test, compare, or improve the system.

In evaluation mode:
1. compare prompt variants, outputs, or framing strategies
2. inspect user preference signals and failure cases
3. propose a concrete edit to the skill or references
4. note what changed and what still appears weak

If evaluation work is requested, read:
- `references/evaluation.md`
