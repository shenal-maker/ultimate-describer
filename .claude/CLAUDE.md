# language-precision

a system for making language more precise, specific, and audience-aware. anti-1984: expand vocabulary, don't compress it.

## skills

- `/articulate on` — activates always-on precision mode. quizzes you on level, audience, purpose, domain. from then on, all descriptive output is automatically sharpened. clean output only (no reports).
- `/articulate off` — deactivates always-on mode.
- `/articulate [thing]` — one-shot precise description or rewrite with full analysis: word choices explained, alternatives considered, calibration summary, cross-lingual enrichment.
- `/precise` — takes text, upgrades vague terms to specific ones. supports `--level` (0-1), `--audience`, `--domain`
- `/precise-calibrate` — 5-question quiz (or writing sample analysis) that builds a user style profile at `.claude/skills/precise/user-profile.md`
- `/describe` — generates precise descriptions of subjects (people, companies, ideas, etc.) with `--purpose` and `--level`
- `/crossling` — finds cross-lingual terms that capture a concept more precisely than English
- `/eval` — evaluate precision outputs across 15 metrics

## always-on articulate mode

if `.claude/skills/articulate/active-config.md` exists, articulate mode is ON. when active:
1. read the config file for saved preferences (level, audience, purpose, domain)
2. apply the 7-stage precision pipeline to all descriptive output you generate
3. output clean text only — no precision reports, no alternatives, no calibration summaries
4. if a preference is "varies", infer from context
5. be invisible — the user should feel like you're naturally articulate, not running a pipeline

this check should happen at conversation start. the config file's existence is the toggle.

## core principle

precision ≠ verbosity. a precise sentence can be shorter than a vague one. precision = reducing the set of things the description could refer to.

## style profile

if `.claude/skills/precise/user-profile.md` exists, `/precise`, `/describe`, and `/articulate` read it to adapt output style. created by `/precise-calibrate`.
