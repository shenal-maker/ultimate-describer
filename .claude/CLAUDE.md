# language-precision

a system for making language more precise, specific, and audience-aware. anti-1984: expand vocabulary, don't compress it.

## skills

- `/precise` — takes text, upgrades vague terms to specific ones. supports `--level` (0-1), `--audience`, `--domain`
- `/precise-calibrate` — 5-question quiz (or writing sample analysis) that builds a user style profile at `.claude/skills/precise/user-profile.md`
- `/describe` — generates precise descriptions of subjects (people, companies, ideas, etc.) with `--purpose` and `--level`
- `/crossling` — finds cross-lingual terms that capture a concept more precisely than English

## core principle

precision ≠ verbosity. a precise sentence can be shorter than a vague one. precision = reducing the set of things the description could refer to.

## style profile

if `.claude/skills/precise/user-profile.md` exists, `/precise` and `/describe` read it to adapt output style. created by `/precise-calibrate`.
