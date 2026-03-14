# language precision skills

four claude code skills that form a pipeline: calibrate who you are → make existing text sharper → generate new descriptions → raid other languages when english falls short.

## `/precise` — the core engine

takes text you've already written and makes it more specific. three levers:

- **`--level`** (0–1): how aggressive. 0.2 just kills the worst offenders ("nice", "stuff", "things"). 0.8 replaces every vague adjective with something that narrows who/what you could be talking about. 1.0 goes borderline forensic — descriptions that could only refer to one thing.
- **`--audience`**: who's reading. "hiring managers" gets different word choices than "my best friend." shifts register and assumed knowledge.
- **`--domain`**: which lens to describe through. "mathematical" quantifies. "literary" uses precise metaphor. "first-principles" decomposes to causes.

detects five types of vagueness: hedge words ("kind of"), hypernyms used where hyponyms exist ("animal" when you mean "border collie"), emotional vagueness ("felt bad"), quantifier vagueness ("some", "many"), and dead metaphors ("think outside the box").

output: rewritten text + a table showing every replacement and what ambiguity it removed. also flags dimensions it *didn't* cover, so you know what's still missing.

if you've run `/precise-calibrate`, it reads your profile and adapts the output style automatically.

## `/precise-calibrate` — the preference quiz

learns how *you* like things described. two modes:

**quiz mode** (default): 5 rounds. each round shows 3 descriptions of the same thing in different styles — one abstract, one concrete, one analytical (varies each round). you pick the one you like. it infers your position on 5 axes:

1. abstract ↔ concrete
2. emotional ↔ analytical
3. terse ↔ elaborate
4. formal ↔ colloquial
5. metaphorical ↔ literal

uses adaptive selection — if your first two answers both lean concrete, it stops asking about that axis and probes the ones it's still uncertain about.

**corpus mode**: give it a path to something you've written. it analyzes sentence length, adjective density, abstraction level, metaphor frequency, and infers the same 5-axis profile from your actual writing.

output: writes a profile file that `/precise` and `/describe` read automatically on every future invocation. you can re-run it anytime or edit the file directly.

## `/describe` — generative descriptions

give it a subject (person, company, idea, experience, place, skill, emotion) and it generates a description from scratch. unlike `/precise`, this isn't editing your text — it's writing new text about something.

**`--purpose`** is the most important flag. "job application" and "introducing to a friend" produce fundamentally different descriptions of the same person because different dimensions matter. it maps the salient dimensions for the subject type (e.g., for a person: behavior patterns, competencies, energy, values, quirks) then filters by purpose.

the hard constraint: every sentence gets a self-check — "could this sentence describe something else equally well?" if yes, it's not precise enough and gets revised. "dynamic self-starter with a passion for innovation" fails this test because it describes everyone. "published three papers that changed how the field models protein folding" passes because it's one person.

flags information gaps. if it can't be specific because it doesn't know enough, it tells you exactly what questions to answer rather than hallucinating details.

## `/crossling` — cross-lingual precision

give it a concept english handles poorly, and it finds words from other languages that capture it better.

example: "the specific type of nostalgia for a place you've never been" → might surface portuguese *saudade*, welsh *hiraeth*, romanian *dor* — each slightly different in what they capture.

for each term it returns: the word, source language, literal translation, actual meaning in use, why it's more precise than the english equivalent, an example sentence, and a **confidence rating** (high/medium/low).

the built-in skepticism is the important part. it flags when:
- a foreign word isn't actually more precise, just more compact (bundling ≠ precision)
- borrowing the word would confuse your audience more than help
- english can handle it fine with the right phrasing — and suggests that phrasing instead
- it's not confident enough in a term's actual usage to recommend it

draws from diverse language families rather than defaulting to the usual german/japanese "untranslatable" lists.

## how they connect

`/precise-calibrate` writes a style profile → `/precise` and `/describe` read it automatically → output adapts to how you actually like things described. the personalization loop works through the filesystem, no database needed.

## quick start

```
/precise "she's a really nice person who does interesting work" --level 0.8
/precise-calibrate
/describe "the feeling of being mid-conversation when a great idea surfaces and immediately evaporates" --purpose "product pitch"
/crossling "the specific type of nostalgia for a place you've never been"
```
