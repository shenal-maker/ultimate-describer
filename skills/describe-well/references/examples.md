## example calibration shifts

same source input, different audience profile and domain profile, different output.

## example 1: under-precision corrected for skeptical decision-makers

source:

`our startup is doing well and growing fast`

overly vague:

`the company has strong momentum and real customer love`

calibrated for `vc_pitch`:

`grew from 14 to 41 paying customers in two quarters, cut churn below 3%, and has 11 months of runway at the current burn rate`

why it changed:
- high epistemic stance raised the evidence threshold
- high action orientation increased differentiation pressure
- required VC terms replaced empty praise

## example 2: over-precision corrected for low-attention readers

source:

`what does this product do?`

over-specified draft:

`it performs semantic entropy analysis over ambiguous lexical spans, ranks rewrite candidates via constrained generation, and exposes a continuous specificity control surface`

calibrated for a general blog reader:

`it spots vague phrases in your writing and suggests sharper replacements so your meaning lands faster`

why it changed:
- low domain fluency lowered the vocabulary ceiling
- moderate attention budget pushed toward one clear sentence

## example 3: same idea, two different audience fits

source:

`describe our infra migration`

for `technical_docs`:

`we moved the job queue from a single Redis instance to partitioned workers behind SQS, which removed the fan-out bottleneck but introduced eventual-consistency edge cases in retry ordering`

for `blog_post`:

`we replaced one overloaded queue with a setup that spreads jobs across more workers, which fixed the bottleneck but made retries trickier to reason about`

visible differences:
- technical docs keep the system names and failure mode
- blog post version preserves the mechanism but lowers jargon density

## example 4: action orientation changes emphasis

source:

`describe my cofounder`

for an investor:

`former manufacturing engineer who now runs product like a constraint solver: turns fuzzy requests into weekly shipping plans, notices cost leaks early, and kills ideas once the numbers stop working`

for a friend:

`she has the rare habit of making chaotic plans feel executable. after ten minutes with her, vague ideas become lists with owners and dates`

visible differences:
- investor version emphasizes operating consequences and differentiation
- friend version keeps the behavioral core but lowers evidence burden and domain framing
