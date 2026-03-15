import argparse
import base64
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parent
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
OPENAI_MODEL_BASELINE = "gpt-5.4"
OPENAI_MODEL_SKILL = "gpt-5.4"
OPENAI_MODEL_JUDGE = "gpt-5-mini"
OPENAI_MODEL_IMAGE = "gpt-image-1"


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def require_openai_key() -> str:
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required in .env or environment")
    return api_key


def openai_chat(
    system: str,
    user: str,
    *,
    model: str,
    temperature: float = 0.6,
    max_tokens: int | None = None,
) -> str:
    api_key = require_openai_key()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if model.startswith("gpt-5"):
        if max_tokens is not None:
            payload["max_completion_tokens"] = max_tokens
        if temperature == 1:
            payload["temperature"] = temperature
    else:
        payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
    req = request.Request(
        OPENAI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise RuntimeError("openai request failed (401): check OPENAI_API_KEY in .env") from exc
        raise RuntimeError(f"openai request failed ({exc.code}): {detail[:240]}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"openai request failed: {exc.reason}") from exc

    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"unexpected openai response shape: {body}") from exc


def judge_json(prompt: str) -> dict[str, Any]:
    text = openai_chat(
        "you are a strict evaluator for a language precision system. respond with json only.",
        prompt,
        model=os.environ.get("OPENAI_MODEL_JUDGE", OPENAI_MODEL_JUDGE),
        temperature=0.2,
        max_tokens=int(os.environ["OPENAI_MAX_TOKENS_JUDGE"]) if os.environ.get("OPENAI_MAX_TOKENS_JUDGE") else None,
    )
    match = re.search(r"\{.*\}", text, re.DOTALL)
    payload = match.group() if match else text
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"failed to parse evaluator json: {text[:300]}") from exc


def openai_image_generate(prompt: str) -> dict[str, Any]:
    api_key = require_openai_key()
    payload = {
        "model": os.environ.get("OPENAI_MODEL_IMAGE", OPENAI_MODEL_IMAGE),
        "prompt": prompt,
        "size": os.environ.get("OPENAI_IMAGE_SIZE", "1024x1024"),
        "quality": os.environ.get("OPENAI_IMAGE_QUALITY", "medium"),
    }
    req = request.Request(
        OPENAI_IMAGES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise RuntimeError("openai image request failed (401): check OPENAI_API_KEY in .env") from exc
        raise RuntimeError(f"openai image request failed ({exc.code}): {detail[:240]}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"openai image request failed: {exc.reason}") from exc

    data = (body.get("data") or [{}])[0]
    if data.get("b64_json"):
        return {
            "mime_type": "image/png",
            "data_url": f"data:image/png;base64,{data['b64_json']}",
        }
    if data.get("url"):
        return {"mime_type": "url", "data_url": data["url"]}
    raise RuntimeError(f"unexpected image response shape: {body}")


def stream_chunks(text: str, *, chunk_words: int = 3):
    parts = re.findall(r"\S+\s*", text)
    if not parts:
        yield ""
        return
    for index in range(0, len(parts), chunk_words):
        yield "".join(parts[index:index + chunk_words])


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.!?]+", text) if part.strip()]


def metric_cell(label: str, numeric: float | None) -> dict[str, Any]:
    return {"label": label, "numeric": numeric}


def fmt_score(value: float) -> str:
    return f"{value:.1f}/10"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def fmt_density(value: float) -> str:
    return f"{value:.3f} f/w"


def fmt_ratio(value: float) -> str:
    if value >= 10:
        return f"{value:.0f}x"
    return f"{value:.1f}x"


def signed_delta(value: float, suffix: str = "") -> str:
    prefix = "+" if value > 0 else ""
    number = f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{prefix}{number}{suffix}"


@dataclass
class LiveContext:
    subject_type: str
    purpose: str | None
    audience: str | None


def infer_context(prompt: str) -> LiveContext:
    result = judge_json(
        "infer minimal metadata from the request below. "
        "return json with subject_type, purpose, audience. "
        "subject_type must be one of person, company, experience, idea, place, skill, group, thing. "
        "use null when purpose or audience are not stated or not strongly inferable.\n\n"
        f"request: {prompt}\n\n"
        'respond as: {"subject_type":"...","purpose":null or "...","audience":null or "..."}'
    )
    subject_type = result.get("subject_type") or "thing"
    purpose = result.get("purpose")
    audience = result.get("audience")
    return LiveContext(subject_type=subject_type, purpose=purpose, audience=audience)


def generate_baseline(prompt: str) -> str:
    return openai_chat(
        "you answer user requests directly in plain prose. "
        "be competent but generic. avoid analysis headers. output only the final text.",
        prompt,
        model=os.environ.get("OPENAI_MODEL_BASELINE", OPENAI_MODEL_BASELINE),
        temperature=0.8,
        max_tokens=int(os.environ["OPENAI_MAX_TOKENS_BASELINE"]) if os.environ.get("OPENAI_MAX_TOKENS_BASELINE") else None,
    )


# distilled from skills/articulate, skills/describe, skills/precise, and
# skills/describe-well/references/*. strips claude-code scaffolding ($ARGUMENTS,
# file i/o, tool calls) and keeps the methodology so any LLM can run it.
DISTILLED_SKILL_PROMPT = """\
you are a precision description engine. core principle: precision ≠ verbosity. \
a precise sentence can be shorter than a vague one. precision = reducing the set \
of things the description could refer to.

## step 1 — calibrate for the audience

before writing anything, map the audience and purpose to four axes and derive \
concrete operating targets from them.

axes (each 0-10):
- domain fluency: how much jargon, abstraction, and background they absorb. \
  0 = child, 4-6 = practitioner, 9-10 = expert evaluator.
- attention budget: how much setup and detail density they tolerate. \
  0 = one-shot skim, 4-6 = compact explanation, 9-10 = deep reader.
- epistemic stance: how much evidence and qualification they expect. \
  0 = wants a clear take, 7-8 = skeptical (needs evidence and scope conditions).
- action orientation: whether they need to decide, compare, or just notice. \
  0 = passive appreciation, 7-8 = active chooser needing tradeoffs.

derived targets:
- vocabulary ceiling: highest acceptable jargon and abstraction level.
- compression target: how dense or unpacked the prose should be.
- evidence threshold: how much support claims need.
- differentiation pressure: how aggressively to separate this subject from similar ones.

critical interactions:
- high fluency + low attention → keep specialist terms, compress setup, skip definitions.
- low fluency + high epistemic stance → explain plainly, make evidence explicit and legible.
- high action + high epistemic stance → state tradeoffs, evidence limits, consequence-bearing details.
- low action + high attention → richer texture, stay under vocabulary ceiling.
- low attention + high action → front-load decision-relevant distinctions, cut decoration.

## step 2 — map dimensions for the subject type

identify what matters for this type of subject, then filter by purpose.

- person: behavior patterns, competencies, energy, values, quirks, how they make others feel, \
  what they actually do vs what their title says.
- company: what they actually do (not mission statement), culture as visible behavior, trajectory, \
  market position, distinctive choices they made that others didn't.
- experience: sensory details, emotional arc, before/after delta, what you'd tell someone who wasn't there.
- idea: core mechanism, why it's non-obvious, what it predicts, what it replaces, boundary conditions.
- place: atmosphere, what you notice first, what you notice after 10 minutes, who belongs there.
- skill: when to use it, what changes in the output, when NOT to use it, learning curve shape.
- group: individual roles/contributions, dynamic between members, shared energy, what an outsider notices first.
- thing/practice: what it actually does mechanically, observable effects, how it differs from the closest alternative.

not all dimensions matter for every purpose. rank by relevance and drop the rest.

## step 3 — draft with precision rules

writing rules (apply all of these):
- replace every generic term with a specific one. "does well" → what specifically? \
  "innovative" → what did they build? "passionate" → what do they actually do that shows it?
- prefer concrete evidence over adjectives. show the behavior, not the label. \
  "she's organized" → "she turns chaotic plans into lists with owners and dates within ten minutes."
- no resume-speak. no "passionate leader", "driven individual", "proven track record". \
  these describe thousands of people. be specific enough to describe one.
- no empty intensifiers. "very", "really", "incredibly", "truly" almost never add precision.
- if something is vague because you lack information, flag what you'd need rather than guessing.
- match voice to purpose. a friend introduction sounds different from an investor brief. \
  precision within the register, not a register shift.

referent reduction test (the core quality check):
for each descriptive choice, ask: "how many other {subject_type}s could this also describe?" \
if the answer is "most of them", try harder. aim for 10x+ referent set reduction per key sentence.

example calibration shifts (study these — they show the target quality level):
- "our startup is doing well" (vague) → "grew from 14 to 41 paying customers in two quarters, \
  cut churn below 3%, 11 months of runway at current burn" (calibrated for vc_pitch: high epistemic, \
  high action orientation, required terms)
- "it performs semantic entropy analysis over ambiguous lexical spans" (over-specified for audience) → \
  "it spots vague phrases in your writing and suggests sharper replacements" (calibrated for blog reader: \
  low domain fluency, moderate attention)
- describing a cofounder for an investor: "former manufacturing engineer who runs product like a \
  constraint solver: turns fuzzy requests into weekly shipping plans, notices cost leaks early, \
  kills ideas once the numbers stop working" (high action orientation, evidence-backed)
- same cofounder for a friend: "she has the rare habit of making chaotic plans feel executable. \
  after ten minutes with her, vague ideas become lists with owners and dates" (lower evidence burden, \
  behavioral core preserved)
- a sunset (literary reader): "the light thickens unevenly - amber pooling near the horizon, \
  the overhead blue not fading but deepening, as if the sky were gaining density rather than \
  losing color. clouds closest to the sun turn the specific orange of heated metal cooling. \
  the transition is slow enough that you only notice it has happened, never catch it happening." \
  (low action orientation, high attention budget — texture and observation over information)

## step 4 — mandatory self-check

for every sentence in your draft:
1. "could this sentence describe a different {subject_type} equally well?" → if yes, revise or cut.
2. "does this add information not already in a prior sentence?" → if no, merge or delete.
3. "is this calibrated for THIS audience, or just more detailed?" → recalibrate if needed.

## step 5 — cross-lingual enrichment (optional, max 2 terms)

if another language captures a concept more precisely than english, consider using it with an \
inline gloss in italics. only if: the precision gain is real, a native speaker would recognize \
the usage, and the audience would benefit. exotic is not better. skip if english handles it fine.

## step 6 — compression pass

- delete filler sentences, circling clauses, restated ideas.
- collapse redundant sentences that make the same point differently.
- if a word count target is given, respect it — but never cut below the point where a \
  load-bearing distinction is lost. overshooting by 20% is better than losing a dimension \
  that makes the description unique.

## domain profiles (apply when purpose matches)

vc_pitch: required terms include market, traction, runway, burn rate. forbidden: hopefully, maybe, \
revolutionary, game-changing. every strong claim ties to traction, distribution, unit economics, or \
team evidence. no fake precision beyond 2 sig figs. no aspirational hype without operating facts.

technical_docs: required terms include interface, constraint, failure mode. forbidden: intuitive, \
simply, obviously. don't hide prerequisites. don't imply guarantees where only best-effort exists.

blog_post: requires concrete examples. forbidden: leverage, paradigm, robust. define specialist \
language. avoid stacking multiple new concepts per sentence. don't confuse accessibility with vagueness.

## hard constraints

- no hallucinated specificity. don't invent facts to sound precise.
- preserve the input's voice and register.
- coherence over per-word precision. the description must read as a whole, not a bag of sharp fragments.
- calibration before escalation. don't exceed audience fit for narrowness.
- no fake etymology or dubious cross-lingual claims.
- short is fine. do not pad.
- output ONLY the final polished description text. no headers, no "## output", no report, \
  no pipeline commentary, no meta-discussion of your process.\
"""


def generate_skill(prompt: str, context: LiveContext) -> str:
    user_msg = (
        f"subject_type: {context.subject_type}\n"
        f"purpose: {context.purpose or 'not explicitly stated'}\n"
        f"audience: {context.audience or 'not explicitly stated'}\n\n"
        f"request:\n{prompt}"
    )
    return openai_chat(
        DISTILLED_SKILL_PROMPT,
        user_msg,
        model=os.environ.get("OPENAI_MODEL_SKILL", OPENAI_MODEL_SKILL),
        temperature=0.7,
        max_tokens=int(os.environ["OPENAI_MAX_TOKENS_SKILL"]) if os.environ.get("OPENAI_MAX_TOKENS_SKILL") else None,
    )


def judge_axes(prompt: str, text: str) -> dict[str, float]:
    result = judge_json(
        "rate this response to the user request on three axes from 0-10.\n"
        "- precision: how specifically and usefully it narrows what matters\n"
        "- voice_naturalness: how natural and tonally fitting the prose feels\n"
        "- coherence: how well the response hangs together as writing\n\n"
        f"user request: {prompt}\n\n"
        f"candidate response: {text}\n\n"
        'respond as: {"precision": 0-10, "voice_naturalness": 0-10, "coherence": 0-10}'
    )
    return {
        "precision": float(result.get("precision", 0)),
        "voice_naturalness": float(result.get("voice_naturalness", 0)),
        "coherence": float(result.get("coherence", 0)),
    }


def judge_referent_count(subject_type: str, text: str) -> int:
    result = judge_json(
        f"how many distinct {subject_type}s could this description plausibly apply to? "
        "give a single integer estimate. use order-of-magnitude realism rather than false precision.\n\n"
        f"description: {text}\n\n"
        'respond as: {"referent_count": <integer>}'
    )
    return max(int(result.get("referent_count", 1)), 1)


def judge_selfcheck(subject_type: str, text: str) -> tuple[int, int]:
    sentences = split_sentences(text)
    if not sentences:
        return 0, 0
    numbered = "\n".join(f"{index + 1}. {sentence}" for index, sentence in enumerate(sentences))
    result = judge_json(
        f"for each sentence below, answer whether it could describe a different {subject_type} equally well.\n\n"
        f"{numbered}\n\n"
        'respond as: {"results":[{"sentence":1,"could_describe_other":"yes/no"}]}'
    )
    rows = result.get("results", [])
    passing = sum(
        1
        for row in rows
        if str(row.get("could_describe_other", "yes")).strip().lower() == "no"
    )
    return passing, len(sentences)


def judge_fact_count(text: str) -> int:
    result = judge_json(
        "list every distinct concrete fact stated in this text. do not count generic praise or restatements.\n\n"
        f"text: {text}\n\n"
        'respond as: {"count": <integer>}'
    )
    return max(int(result.get("count", 0)), 0)


def judge_purpose_fit(prompt: str, text: str) -> float:
    result = judge_json(
        "rate 0-10 how well this response fits the user's apparent purpose.\n\n"
        f"user request: {prompt}\n\n"
        f"response: {text}\n\n"
        'respond as: {"score": 0-10}'
    )
    return float(result.get("score", 0))


def judge_summary(prompt: str, baseline: str, skill: str) -> str:
    return openai_chat(
        "compare a baseline response and a more precise response to the same request. "
        "write 2 concise sentences about what changed and whether the precision upgrade helped. "
        "no bullets, no headings.",
        f"user request:\n{prompt}\n\nbaseline:\n{baseline}\n\nskill:\n{skill}",
        model=os.environ.get("OPENAI_MODEL_JUDGE", OPENAI_MODEL_JUDGE),
        temperature=0.3,
        max_tokens=int(os.environ["OPENAI_MAX_TOKENS_JUDGE"]) if os.environ.get("OPENAI_MAX_TOKENS_JUDGE") else None,
    )


def build_metric_event(name: str, baseline_label: str, baseline_numeric: float | None, skill_label: str, skill_numeric: float | None, delta: str) -> dict[str, Any]:
    return {
        "type": "metric",
        "name": name,
        "baseline": metric_cell(baseline_label, baseline_numeric),
        "skill": metric_cell(skill_label, skill_numeric),
        "delta": delta,
    }


def emit_event(handler: SimpleHTTPRequestHandler, payload: dict[str, Any]) -> None:
    handler.wfile.write((json.dumps(payload) + "\n").encode("utf-8"))
    handler.wfile.flush()


def handle_live_generate(handler: SimpleHTTPRequestHandler, body: dict[str, Any]) -> None:
    prompt = str(body.get("prompt", "")).strip()
    generate_image = bool(body.get("generate_image"))
    if not prompt:
        raise RuntimeError("prompt is required")

    handler.send_response(200)
    handler.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
    handler.send_header("Cache-Control", "no-cache")
    handler.send_header("Connection", "close")
    handler.end_headers()

    emit_event(handler, {"type": "status", "message": "inferring context"})
    context = infer_context(prompt)
    emit_event(
        handler,
        {
            "type": "context",
            "context": {
                "subject_type": context.subject_type,
                "purpose": context.purpose,
                "audience": context.audience,
            },
        },
    )

    emit_event(handler, {"type": "phase", "phase": "baseline", "status": "active", "label": "generating"})
    baseline = generate_baseline(prompt)
    for chunk in stream_chunks(baseline):
        emit_event(handler, {"type": "baseline_delta", "text": chunk})
        time.sleep(0.03)
    emit_event(handler, {"type": "phase", "phase": "baseline", "status": "done", "label": "complete"})

    emit_event(handler, {"type": "phase", "phase": "skill", "status": "active", "label": "generating"})
    skill = generate_skill(prompt, context)
    for chunk in stream_chunks(skill):
        emit_event(handler, {"type": "skill_delta", "text": chunk})
        time.sleep(0.03)
    emit_event(handler, {"type": "phase", "phase": "skill", "status": "done", "label": "complete"})

    if generate_image:
        emit_event(handler, {"type": "phase", "phase": "image", "status": "active", "label": "rendering"})
        emit_event(handler, {"type": "status", "message": "rendering baseline and skill images"})
        baseline_image_prompt = (
            "create a single compelling image that visualizes this description faithfully. "
            "favor concrete visual details over text overlays.\n\n"
            f"{baseline}"
        )
        skill_image_prompt = (
            "create a single compelling image that visualizes this description faithfully. "
            "favor concrete visual details over text overlays.\n\n"
            f"{skill}"
        )
        baseline_image = openai_image_generate(baseline_image_prompt)
        emit_event(handler, {"type": "image_prompt", "side": "baseline", "text": baseline_image_prompt})
        emit_event(handler, {"type": "image", "side": "baseline", "image": baseline_image})
        skill_image = openai_image_generate(skill_image_prompt)
        emit_event(handler, {"type": "image_prompt", "side": "skill", "text": skill_image_prompt})
        emit_event(handler, {"type": "image", "side": "skill", "image": skill_image})
        emit_event(handler, {"type": "phase", "phase": "image", "status": "done", "label": "complete"})

    emit_event(handler, {"type": "phase", "phase": "eval", "status": "active", "label": "judging"})
    emit_event(handler, {"type": "status", "message": "drawing evals"})

    baseline_axes = judge_axes(prompt, baseline)
    skill_axes = judge_axes(prompt, skill)
    emit_event(
        handler,
        build_metric_event(
            "precision vector",
            fmt_score(baseline_axes["precision"]),
            baseline_axes["precision"],
            fmt_score(skill_axes["precision"]),
            skill_axes["precision"],
            signed_delta(skill_axes["precision"] - baseline_axes["precision"]),
        ),
    )
    emit_event(
        handler,
        build_metric_event(
            "voice naturalness",
            fmt_score(baseline_axes["voice_naturalness"]),
            baseline_axes["voice_naturalness"],
            fmt_score(skill_axes["voice_naturalness"]),
            skill_axes["voice_naturalness"],
            signed_delta(skill_axes["voice_naturalness"] - baseline_axes["voice_naturalness"]),
        ),
    )
    emit_event(
        handler,
        build_metric_event(
            "coherence",
            fmt_score(baseline_axes["coherence"]),
            baseline_axes["coherence"],
            fmt_score(skill_axes["coherence"]),
            skill_axes["coherence"],
            signed_delta(skill_axes["coherence"] - baseline_axes["coherence"]),
        ),
    )

    baseline_referents = judge_referent_count(context.subject_type, baseline)
    skill_referents = judge_referent_count(context.subject_type, skill)
    emit_event(
        handler,
        build_metric_event(
            "referent set size",
            f"{baseline_referents}",
            float(baseline_referents),
            f"{skill_referents}",
            float(skill_referents),
            fmt_ratio(baseline_referents / max(skill_referents, 1)),
        ),
    )

    passing, total = judge_selfcheck(context.subject_type, skill)
    pass_rate = (passing / total) if total else 0.0
    emit_event(
        handler,
        build_metric_event(
            "self-check",
            "—",
            None,
            f"{fmt_pct(pass_rate)} ({passing}/{total})" if total else "0% (0/0)",
            pass_rate,
            signed_delta(pass_rate * 100, "pp"),
        ),
    )

    baseline_facts = judge_fact_count(baseline)
    skill_facts = judge_fact_count(skill)
    baseline_density = baseline_facts / max(word_count(baseline), 1)
    skill_density = skill_facts / max(word_count(skill), 1)
    emit_event(
        handler,
        build_metric_event(
            "info density",
            fmt_density(baseline_density),
            baseline_density,
            fmt_density(skill_density),
            skill_density,
            fmt_ratio(skill_density / max(baseline_density, 0.001)),
        ),
    )

    baseline_fit = judge_purpose_fit(prompt, baseline)
    skill_fit = judge_purpose_fit(prompt, skill)
    emit_event(
        handler,
        build_metric_event(
            "voice-to-purpose fit",
            fmt_score(baseline_fit),
            baseline_fit,
            fmt_score(skill_fit),
            skill_fit,
            signed_delta(skill_fit - baseline_fit),
        ),
    )

    summary = judge_summary(prompt, baseline, skill)
    emit_event(handler, {"type": "narrative", "text": summary})
    emit_event(handler, {"type": "phase", "phase": "eval", "status": "done", "label": "complete"})
    emit_event(handler, {"type": "status", "message": "live generation complete"})
    emit_event(handler, {"type": "done"})


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        if self.path != "/api/live-generate":
            self.send_error(404, "unknown endpoint")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw_body or "{}")
            handle_live_generate(self, body)
        except Exception as exc:
            if self.wfile.closed:
                return
            try:
                emit_event(self, {"type": "error", "message": str(exc)})
            except Exception:
                pass

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"[live-server] {fmt % args}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="serve proto.html plus live generation api")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8123)
    args = parser.parse_args()

    os.chdir(ROOT)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"serving on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
