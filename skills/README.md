# language precision skills

## `/language-precision` — the unified skill

one command that runs the full pipeline. auto-detects whether you're editing existing text or describing something new, checks your style profile (runs a fast 1-question calibration if you don't have one yet), upgrades precision, and enriches with cross-lingual terms when they genuinely help.

```
/language-precision "she's a really nice person who does interesting work" --level 0.8
/language-precision "my cofounder" --purpose "investor pitch" --audience "YC partners"
/language-precision "the feeling when a great idea surfaces mid-conversation and immediately evaporates"
```

### flags

- `--level` (0–1, default 0.6): specificity depth. 0.2 = light touch. 0.8 = instance-level. 1.0 = forensic.
- `--audience`: who's reading. shifts register and assumed knowledge.
- `--purpose`: what the description is for. "job application", "investor pitch", "personal journal", etc.
- `--domain`: framing lens. "mathematical", "literary", "first-principles", "technical", "colloquial".

### what it does (5-stage pipeline)

1. **profile check** — reads your style preferences (or runs a fast 1-question calibration on first use)
2. **mode detection** — auto-detects editing vs generative mode, maps salient dimensions
3. **precision engine** — replaces vague terms, applies self-check ("could this describe something else?"), frames in requested domain
4. **cross-lingual enrichment** — surfaces terms from other languages only when they genuinely add precision
5. **output assembly** — compiled result with change table, dimension coverage, and alternatives considered

---

## individual skills

the pipeline stages are also available as standalone skills for when you want just one piece:

### `/precise` — precision engine only

takes existing text, upgrades vague terms. same `--level`, `--audience`, `--domain` flags.

```
/precise "the company has a great culture" --level 0.7 --audience "job candidates"
```

### `/precise-calibrate` — full style calibration

5-round adaptive quiz or writing sample analysis. builds a detailed profile across 5 axes: abstract↔concrete, emotional↔analytical, terse↔elaborate, formal↔colloquial, metaphorical↔literal.

use this when you want a thorough calibration instead of the 1-question fast version built into `/language-precision`.

```
/precise-calibrate
/precise-calibrate path/to/my-writing-sample.md
```

### `/describe` — generative descriptions only

generates descriptions from scratch for a subject (person, company, idea, experience, place, skill, emotion). `--purpose` is the most important flag.

```
/describe "the mass resignation at Twitter post-acquisition" --purpose "case study"
```

### `/crossling` — cross-lingual search only

finds terms from other languages that capture a concept more precisely than english. includes confidence ratings and flags when english works fine.

```
/crossling "the satisfaction of watching someone get what they deserve"
```

## personalization

`/precise-calibrate` (or the first run of `/language-precision`) writes a style profile to `.claude/skills/precise/user-profile.md`. all skills read it automatically. re-run calibration anytime or edit the file directly.
