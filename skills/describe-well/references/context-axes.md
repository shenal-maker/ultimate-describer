## context axes

this file defines the four calibration dimensions used by `/describe-well`, `/precise`, and `/describe`.

## domain fluency

- 0-1: child or uninformed general reader. avoid jargon. define even common specialist terms.
- 2-3: broad educated audience. allow common public terms, but explain field-specific language.
- 4-6: practitioner. use normal working vocabulary for the field, but do not assume niche subculture shorthand.
- 7-8: specialized professional. concise use of jargon is fine if it saves time.
- 9-10: expert evaluator. assume deep familiarity. optimize for sharp distinctions, not onboarding.

controls:
- vocabulary ceiling
- definition burden
- acceptable jargon density

## attention budget

- 0-1: one-shot skim. lead with the point immediately.
- 2-3: short pitch or update. every sentence must earn its place.
- 4-6: willing to read a compact explanation if it is obviously relevant.
- 7-8: patient reader. can absorb setup, caveats, and comparisons.
- 9-10: deep reader. can handle a long chain of reasoning if it pays off.

controls:
- compression target
- ordering of evidence
- tolerance for setup and parenthetical context

## epistemic stance

- 0-1: wants a clear take, minimal caveating.
- 2-3: tolerates light hedging but does not want every uncertainty foregrounded.
- 4-6: expects claims to be tethered to examples or mechanisms.
- 7-8: skeptical reader. wants evidence, scope conditions, and explicit uncertainty handling.
- 9-10: evaluator or reviewer. weakly supported claims should be reframed or removed.

controls:
- evidence threshold
- confidence labeling
- claim compression vs qualification

## action orientation

- 0-1: passive appreciation. reader mainly wants a feel for the thing.
- 2-3: informal understanding. reader may repeat the description, but not act on it.
- 4-6: moderate decision pressure. reader needs practical relevance.
- 7-8: active chooser. reader needs tradeoffs, consequences, and discriminators.
- 9-10: high-stakes evaluator. reader needs fast comparison against alternatives.

controls:
- differentiation pressure
- emphasis on consequences and tradeoffs
- degree of contrast against nearby alternatives

## derived targets

- `vocabulary ceiling`: highest acceptable jargon and abstraction level
- `compression target`: how dense or unpacked the prose should be
- `evidence threshold`: how much support and uncertainty labeling claims need
- `differentiation pressure`: how aggressively the text should separate the subject from nearby alternatives

## common interactions

| pairing | implication |
|---------|-------------|
| high fluency + low attention | keep specialist terms, compress setup, skip basic definitions |
| low fluency + high epistemic stance | explain concepts plainly and make support explicit |
| low attention + high action | front-load decision-relevant distinctions |
| high attention + low action | allow more texture and scene-setting |
| high epistemic stance + high action | state tradeoffs, evidence limits, and consequence-bearing details |

## calibration heuristics

- if domain fluency and attention budget conflict, preserve the best jargon but cut explanatory side paths
- if epistemic stance is high, unsupported adjectives should usually be replaced with mechanisms or evidence
- if action orientation is low, do not over-index on comparison tables and ranking language
- if action orientation is high, omit decorative details unless they change the decision
