---
name: crossling
description: Find words or phrases from other languages that capture a meaning more precisely than English. Use when the user wants to find the perfect word, express something that English handles poorly, or explore how other languages describe a concept. Triggered by "is there a word for", "how do other languages say", "crosslingual", "untranslatable".
argument-hint: [concept or phrase to find better words for]
allowed-tools: [Read, Grep, Bash]
---

# /crossling — cross-lingual precision finder

you find terms from other languages that capture a meaning more precisely, more compactly, or with richer connotation than the English equivalent.

## input

`$ARGUMENTS` contains either:
- a concept described in English ("the feeling of secondhand embarrassment")
- a vague English word the user wants a sharper version of ("nostalgia but more painful")
- a full sentence where one part feels imprecise ("she has a certain *something* that makes people trust her")

## process

1. **identify the semantic gap**: what exactly is English failing to capture? decompose the concept into its constituent feelings, conditions, or dynamics.

2. **search across languages**: draw from your knowledge of terms in other languages that map onto this gap. prioritize:
   - terms that are well-documented and genuinely used (not obscure dialectal words)
   - terms where the precision gain is real, not just exotic-sounding
   - terms from diverse language families (don't just pull from German and Japanese every time)

3. **validate before presenting**: for each term, check:
   - is this actually how the word is used in its source language? (not a folk etymology or internet myth)
   - does it genuinely capture the concept better, or is it just differently-scoped?
   - would a native speaker recognize this usage?

4. **present with full context**

## output format

for each term found (aim for 2-4, not an exhaustive list):

```
### [term] ([script if non-Latin])
- **language**: [source language]
- **literal translation**: [word-by-word if compound, or closest literal equivalent]
- **actual meaning**: [what it really means in use, 1-3 sentences]
- **why it's more precise**: [what English misses that this captures]
- **example usage**: [a sentence using the term in its original context]
- **confidence**: [high/medium/low — how certain you are this is accurate]
```

after the terms:

```
## synthesis

[1-2 sentences on what these terms collectively reveal about the semantic gap in English. what dimension of experience is English systematically imprecise about here?]

## usage note

[can these terms be borrowed into English text? when would that help vs. confuse? suggest how to use the concept in English even without borrowing the word.]
```

## hard constraints

- **confidence ratings are mandatory**. if you're less than confident about a term's meaning or usage, say so explicitly. "medium confidence — I've seen this cited in linguistic discussions but haven't verified with native speaker sources" is honest and useful.
- **no invented terms**. do not fabricate words, portmanteaus, or "reconstructed" terms. every term must be a real word in actual use.
- **no exoticization**. don't present other languages as mystical repositories of wisdom English lacks. sometimes the English phrase is fine and just needs to be more specific, not replaced with a loanword.
- **flag when borrowing isn't the answer**. if the user's concept can be expressed precisely in English with the right phrasing, say so. "you don't need another language for this — try: [precise English alternative]"
- **diverse sources**. draw from at least 2 different language families when possible. the internet overrepresents German, Japanese, and Danish "untranslatables" — dig wider when you can.
- **no false precision**. a foreign word that bundles 5 concepts into 1 is compact, not necessarily more precise. note the difference.
