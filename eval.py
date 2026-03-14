"""
language precision eval — measures how well the precision system works.

10 metrics, one judge function, one file.

setup:
    pip install anthropic
    export ANTHROPIC_API_KEY=your-api-key-here

usage:
    python eval.py --test-cases tests.json --output results.json
    python eval.py --test-cases tests.json --metrics referent_reduction,sentence_selfcheck
    python eval.py --test-cases tests.json --repeats 3
"""

import anthropic
import json
import argparse
import time
import statistics
import re
from datetime import datetime, timezone

MODEL = "claude-sonnet-4-20250514"

JUDGE_SYSTEM = (
    "you are an evaluator for a language precision system. "
    "you assess text quality along specific dimensions. "
    "respond ONLY in the JSON format specified. "
    "be calibrated: use the full range of your scales. "
    "a score of 5/10 means genuinely mediocre, not 'pretty good.' "
    "do not be generous. do not be cruel. be accurate."
)

ALL_METRICS = [
    "referent_reduction",
    "sentence_selfcheck",
    "information_density",
    "discriminability",
    "precision_vector",
    "voice_preservation",
    "coherence",
    "vagueness_detection",
    "crossling_validation",
    "audience_adaptation",
]

client = anthropic.Anthropic()


def judge(prompt, retries=2):
    """single point of contact with the API. returns parsed JSON dict."""
    for attempt in range(retries + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=JUDGE_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
            # extract JSON from response (may be wrapped in markdown)
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            if attempt < retries:
                time.sleep(1)
                continue
            return {"error": f"failed to parse judge response: {text[:200]}"}
        except anthropic.APIError as e:
            if attempt < retries:
                time.sleep(2)
                continue
            return {"error": str(e)}


def load_test_cases(path):
    with open(path) as f:
        data = json.load(f)
    return data.get("test_cases", data) if isinstance(data, dict) else data


def word_count(text):
    return len(text.split())


def split_sentences(text):
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


# --- metrics ---


def eval_referent_reduction(cases, repeats=1):
    """how many things could each description apply to?"""
    scores = []
    for tc in cases:
        baseline = tc.get("baseline_output", tc.get("input_text", ""))
        skill = tc["skill_output"]
        subject = tc.get("subject_type", "thing")

        results = []
        for _ in range(repeats):
            b = judge(
                f'how many distinct {subject}s could this description apply to? '
                f'give your best order-of-magnitude estimate as an integer.\n\n'
                f'description: "{baseline}"\n\n'
                f'respond as: {{"referent_count": <integer>, "reasoning": "<1 sentence>"}}'
            )
            s = judge(
                f'how many distinct {subject}s could this description apply to? '
                f'give your best order-of-magnitude estimate as an integer.\n\n'
                f'description: "{skill}"\n\n'
                f'respond as: {{"referent_count": <integer>, "reasoning": "<1 sentence>"}}'
            )
            if "error" not in b and "error" not in s:
                results.append((b.get("referent_count", 1), s.get("referent_count", 1)))

        if results:
            b_counts, s_counts = zip(*results)
            b_med = statistics.median(b_counts)
            s_med = max(statistics.median(s_counts), 1)
            scores.append({
                "id": tc.get("id", ""),
                "baseline_referent_count": b_med,
                "skill_referent_count": s_med,
                "reduction_ratio": round(b_med / s_med, 1),
            })
    return scores


def eval_sentence_selfcheck(cases, repeats=1):
    """for each sentence: could this describe a different subject equally well?"""
    scores = []
    for tc in cases:
        skill = tc["skill_output"]
        subject = tc.get("subject_type", "thing")
        sentences = split_sentences(skill)
        if not sentences:
            continue

        # batch all sentences into one judge call
        numbered = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))
        result = judge(
            f"for each numbered sentence below, answer: could this sentence describe "
            f"a DIFFERENT {subject} equally well? answer yes or no for each.\n\n"
            f"{numbered}\n\n"
            f'respond as: {{"results": [{{"sentence": 1, "could_describe_other": "yes/no"}},...]}}'
        )

        if "error" not in result:
            results = result.get("results", [])
            passing = sum(1 for r in results if r.get("could_describe_other", "yes").lower() == "no")
            scores.append({
                "id": tc.get("id", ""),
                "total_sentences": len(sentences),
                "passing_sentences": passing,
                "pass_rate": round(passing / len(sentences), 2),
            })
    return scores


def eval_information_density(cases, repeats=1):
    """distinct concrete facts per word."""
    scores = []
    for tc in cases:
        baseline = tc.get("baseline_output", tc.get("input_text", ""))
        skill = tc["skill_output"]

        b = judge(
            f"list every distinct, concrete, verifiable fact in this text. "
            f"only count things that are specific (not generic platitudes).\n\n"
            f'text: "{baseline}"\n\n'
            f'respond as: {{"facts": ["fact1", "fact2", ...], "count": <integer>}}'
        )
        s = judge(
            f"list every distinct, concrete, verifiable fact in this text. "
            f"only count things that are specific (not generic platitudes).\n\n"
            f'text: "{skill}"\n\n'
            f'respond as: {{"facts": ["fact1", "fact2", ...], "count": <integer>}}'
        )

        if "error" not in b and "error" not in s:
            b_count = b.get("count", 0)
            s_count = s.get("count", 0)
            b_wc = max(word_count(baseline), 1)
            s_wc = max(word_count(skill), 1)
            scores.append({
                "id": tc.get("id", ""),
                "baseline_facts": b_count,
                "baseline_density": round(b_count / b_wc, 3),
                "skill_facts": s_count,
                "skill_density": round(s_count / s_wc, 3),
                "density_gain": round((s_count / s_wc) / max(b_count / b_wc, 0.001), 2),
            })
    return scores


def eval_discriminability(cases, repeats=1):
    """can a judge match descriptions to their subjects? needs 3+ cases of same type."""
    from itertools import groupby

    sorted_cases = sorted(cases, key=lambda c: c.get("subject_type", ""))
    scores = []

    for stype, group in groupby(sorted_cases, key=lambda c: c.get("subject_type", "")):
        group = list(group)
        if len(group) < 3:
            continue

        batch = group[:5]
        descriptions = [tc["skill_output"] for tc in batch]
        subjects = [tc.get("input_text", tc.get("id", f"subject_{i}")) for i, tc in enumerate(batch)]

        import random
        shuffled_indices = list(range(len(descriptions)))
        random.shuffle(shuffled_indices)
        shuffled_descs = [descriptions[i] for i in shuffled_indices]

        desc_block = "\n\n".join(f"Description {i+1}: {d}" for i, d in enumerate(shuffled_descs))
        subj_block = "\n".join(f"{chr(65+i)}. {s}" for i, s in enumerate(subjects))

        result = judge(
            f"match each description to its subject. each description corresponds to exactly one subject.\n\n"
            f"subjects:\n{subj_block}\n\n{desc_block}\n\n"
            f'respond as: {{"matches": [{{"description": 1, "subject": "A"}}, ...]}}'
        )

        if "error" not in result:
            matches = result.get("matches", [])
            correct = 0
            for m in matches:
                desc_idx = m.get("description", 0) - 1
                subj_letter = m.get("subject", "")
                expected_subj_idx = shuffled_indices[desc_idx] if desc_idx < len(shuffled_indices) else -1
                actual_letter = chr(65 + expected_subj_idx) if expected_subj_idx >= 0 else ""
                if subj_letter == actual_letter:
                    correct += 1

            scores.append({
                "subject_type": stype,
                "total": len(batch),
                "correct": correct,
                "accuracy": round(correct / len(batch), 2),
            })
    return scores


def eval_precision_vector(cases, repeats=1):
    """3-axis precision score: denotative, connotative, pragmatic."""
    scores = []
    for tc in cases:
        skill = tc["skill_output"]
        purpose = tc.get("purpose", "general communication")
        subject = tc.get("subject_type", "thing")

        result = judge(
            f"rate this description of a {subject} on three precision axes (0-10 each):\n\n"
            f"purpose of this description: {purpose}\n\n"
            f'description: "{skill}"\n\n'
            f"axes:\n"
            f"- denotative: how well does it narrow down WHICH {subject} this is? (referent reduction)\n"
            f"- connotative: how well does it convey the emotional/tonal feel of the {subject}?\n"
            f"- pragmatic: how well does it achieve the stated purpose ({purpose})?\n\n"
            f'respond as: {{"denotative": <0-10>, "connotative": <0-10>, "pragmatic": <0-10>, "reasoning": "<brief>"}}'
        )

        if "error" not in result:
            scores.append({
                "id": tc.get("id", ""),
                "denotative": result.get("denotative", 0),
                "connotative": result.get("connotative", 0),
                "pragmatic": result.get("pragmatic", 0),
                "mean": round(statistics.mean([
                    result.get("denotative", 0),
                    result.get("connotative", 0),
                    result.get("pragmatic", 0),
                ]), 1),
            })
    return scores


def eval_voice_preservation(cases, repeats=1):
    """does the precision upgrade preserve the writer's voice?"""
    scores = []
    for tc in cases:
        original = tc.get("baseline_output", tc.get("input_text", ""))
        skill = tc["skill_output"]

        result = judge(
            f"compare the original text to the rewritten version. "
            f"rate 0-10 how well the rewrite preserves the original writer's voice, tone, and register. "
            f"10 = identical voice, just more precise. 0 = completely different voice.\n\n"
            f'original: "{original}"\n\n'
            f'rewrite: "{skill}"\n\n'
            f'respond as: {{"score": <0-10>, "markers_preserved": ["..."], "markers_lost": ["..."]}}'
        )

        if "error" not in result:
            scores.append({
                "id": tc.get("id", ""),
                "score": result.get("score", 0),
                "markers_preserved": result.get("markers_preserved", []),
                "markers_lost": result.get("markers_lost", []),
            })
    return scores


def eval_coherence(cases, repeats=1):
    """does the output read as natural prose?"""
    scores = []
    for tc in cases:
        skill = tc["skill_output"]

        result = judge(
            f"rate 0-10 how natural this text reads as prose. "
            f"0 = thesaurus vomit, unreadable. 5 = functional but awkward. "
            f"10 = could appear in published writing.\n\n"
            f'text: "{skill}"\n\n'
            f'respond as: {{"score": <0-10>, "issues": ["..."]}}'
        )

        if "error" not in result:
            scores.append({
                "id": tc.get("id", ""),
                "score": result.get("score", 0),
                "issues": result.get("issues", []),
            })
    return scores


def eval_vagueness_detection(cases, repeats=1):
    """can the judge correctly identify vague vs precise text?"""
    scored_cases = [tc for tc in cases if "expected_vague" in tc]
    if not scored_cases:
        return []

    scores = []
    for tc in scored_cases:
        text = tc.get("input_text", tc.get("baseline_output", ""))
        expected = tc["expected_vague"]

        result = judge(
            f"is this text vague or precise? vague = uses generic terms, hedges, "
            f"could describe many things. precise = uses specific terms, narrows referent set.\n\n"
            f'text: "{text}"\n\n'
            f'respond as: {{"classification": "vague" or "precise", "vague_terms": ["..."], "confidence": <0-1>}}'
        )

        if "error" not in result:
            classified_vague = result.get("classification", "").lower() == "vague"
            correct = classified_vague == expected
            scores.append({
                "id": tc.get("id", ""),
                "expected": "vague" if expected else "precise",
                "predicted": result.get("classification", "unknown"),
                "correct": correct,
                "vague_terms": result.get("vague_terms", []),
            })
    return scores


def eval_crossling_validation(cases, repeats=1):
    """are surfaced cross-lingual terms actually real and correctly used?"""
    scored_cases = [tc for tc in cases if tc.get("crossling_terms")]
    if not scored_cases:
        return []

    scores = []
    for tc in scored_cases:
        for term in tc["crossling_terms"]:
            result = judge(
                f'is the word "{term["term"]}" from {term["language"]} actually used '
                f'to mean what is claimed here? rate your confidence 0-1 that this is '
                f'a real, accurately described term.\n\n'
                f'stated meaning context: used in a description to add precision\n\n'
                f'respond as: {{"is_real": true/false, "confidence": <0-1>, "correction": "<if wrong, what it actually means>"}}'
            )

            if "error" not in result:
                stated = {"high": 0.9, "medium": 0.6, "low": 0.3}.get(
                    term.get("stated_confidence", "medium"), 0.5
                )
                actual = result.get("confidence", 0)
                scores.append({
                    "id": tc.get("id", ""),
                    "term": term["term"],
                    "language": term["language"],
                    "is_real": result.get("is_real", False),
                    "stated_confidence": stated,
                    "judge_confidence": actual,
                    "calibration_error": round(abs(stated - actual), 2),
                })
    return scores


def eval_audience_adaptation(cases, repeats=1):
    """given same input with different audiences, does output actually differ appropriately?"""
    # group by input_text to find pairs
    by_input = {}
    for tc in cases:
        key = tc.get("input_text", "")
        if key and tc.get("audience"):
            by_input.setdefault(key, []).append(tc)

    pairs = {k: v for k, v in by_input.items() if len(v) >= 2}
    if not pairs:
        return []

    scores = []
    for input_text, group in pairs.items():
        a, b = group[0], group[1]
        result = judge(
            f"two descriptions were generated from the same input but for different audiences.\n\n"
            f'input: "{input_text}"\n\n'
            f'audience A ({a["audience"]}): "{a["skill_output"]}"\n\n'
            f'audience B ({b["audience"]}): "{b["skill_output"]}"\n\n'
            f"rate 0-10: how well do these differ in ways appropriate for their respective audiences? "
            f"0 = identical outputs. 10 = perfectly adapted to each audience.\n\n"
            f'respond as: {{"score": <0-10>, "differences_noted": ["..."]}}'
        )

        if "error" not in result:
            scores.append({
                "input": input_text[:80],
                "audience_a": a["audience"],
                "audience_b": b["audience"],
                "score": result.get("score", 0),
                "differences": result.get("differences_noted", []),
            })
    return scores


# --- aggregation ---


def aggregate(metric_name, scores):
    if not scores:
        return {"n": 0, "note": "no applicable test cases"}

    if metric_name == "referent_reduction":
        ratios = [s["reduction_ratio"] for s in scores]
        return {"n": len(ratios), "mean_reduction": round(statistics.mean(ratios), 1),
                "median_reduction": round(statistics.median(ratios), 1)}

    if metric_name == "sentence_selfcheck":
        rates = [s["pass_rate"] for s in scores]
        return {"n": len(rates), "mean_pass_rate": round(statistics.mean(rates), 2)}

    if metric_name == "information_density":
        gains = [s["density_gain"] for s in scores]
        return {"n": len(gains), "mean_density_gain": round(statistics.mean(gains), 2)}

    if metric_name == "discriminability":
        accs = [s["accuracy"] for s in scores]
        return {"n": len(accs), "mean_accuracy": round(statistics.mean(accs), 2)}

    if metric_name == "precision_vector":
        return {
            "n": len(scores),
            "mean_denotative": round(statistics.mean([s["denotative"] for s in scores]), 1),
            "mean_connotative": round(statistics.mean([s["connotative"] for s in scores]), 1),
            "mean_pragmatic": round(statistics.mean([s["pragmatic"] for s in scores]), 1),
            "mean_overall": round(statistics.mean([s["mean"] for s in scores]), 1),
        }

    if metric_name in ("voice_preservation", "coherence"):
        vals = [s["score"] for s in scores]
        return {"n": len(vals), "mean_score": round(statistics.mean(vals), 1)}

    if metric_name == "vagueness_detection":
        correct = sum(1 for s in scores if s["correct"])
        return {"n": len(scores), "accuracy": round(correct / len(scores), 2)}

    if metric_name == "crossling_validation":
        real = sum(1 for s in scores if s["is_real"])
        cal_errors = [s["calibration_error"] for s in scores]
        return {"n": len(scores), "real_rate": round(real / len(scores), 2),
                "mean_calibration_error": round(statistics.mean(cal_errors), 2)}

    if metric_name == "audience_adaptation":
        vals = [s["score"] for s in scores]
        return {"n": len(vals), "mean_score": round(statistics.mean(vals), 1)}

    return {"n": len(scores)}


# --- runner ---


METRIC_FUNCS = {
    "referent_reduction": eval_referent_reduction,
    "sentence_selfcheck": eval_sentence_selfcheck,
    "information_density": eval_information_density,
    "discriminability": eval_discriminability,
    "precision_vector": eval_precision_vector,
    "voice_preservation": eval_voice_preservation,
    "coherence": eval_coherence,
    "vagueness_detection": eval_vagueness_detection,
    "crossling_validation": eval_crossling_validation,
    "audience_adaptation": eval_audience_adaptation,
}


def run_eval(test_cases_path, metrics=None, output_path="results.json", repeats=1):
    cases = load_test_cases(test_cases_path)
    metrics = metrics or ALL_METRICS

    print(f"loaded {len(cases)} test cases")
    print(f"running metrics: {', '.join(metrics)}")
    print(f"repeats per judgment: {repeats}")
    print()

    results = {
        "run_id": f"eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "model": MODEL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repeats": repeats,
        "test_case_count": len(cases),
        "metrics": {},
    }

    for metric in metrics:
        if metric not in METRIC_FUNCS:
            print(f"  unknown metric: {metric}, skipping")
            continue

        print(f"  running {metric}...", end=" ", flush=True)
        start = time.time()
        scores = METRIC_FUNCS[metric](cases, repeats=repeats)
        elapsed = round(time.time() - start, 1)
        agg = aggregate(metric, scores)

        results["metrics"][metric] = {
            "scores": scores,
            "aggregate": agg,
            "elapsed_seconds": elapsed,
        }
        print(f"done ({elapsed}s, {agg.get('n', 0)} scored)")

    # summary
    summary = {}
    for name, data in results["metrics"].items():
        agg = data["aggregate"]
        if "mean_score" in agg:
            summary[name] = agg["mean_score"]
        elif "mean_pass_rate" in agg:
            summary[name] = agg["mean_pass_rate"]
        elif "mean_reduction" in agg:
            summary[name] = agg["mean_reduction"]
        elif "mean_overall" in agg:
            summary[name] = agg["mean_overall"]
        elif "accuracy" in agg:
            summary[name] = agg["accuracy"]
        elif "mean_density_gain" in agg:
            summary[name] = agg["mean_density_gain"]
        elif "mean_accuracy" in agg:
            summary[name] = agg["mean_accuracy"]

    if summary:
        best = max(summary, key=summary.get)
        worst = min(summary, key=summary.get)
        results["summary"] = {
            "scores": summary,
            "best_metric": best,
            "worst_metric": worst,
        }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nresults written to {output_path}")
    if summary:
        print(f"best: {best} ({summary[best]})")
        print(f"worst: {worst} ({summary[worst]})")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="language precision eval")
    parser.add_argument("--test-cases", required=True, help="path to test cases JSON")
    parser.add_argument("--output", default="results.json", help="output path")
    parser.add_argument("--metrics", default=None, help="comma-separated metric names (default: all)")
    parser.add_argument("--repeats", type=int, default=1, help="repeat each judgment N times, take median")
    args = parser.parse_args()

    metrics = args.metrics.split(",") if args.metrics else None
    run_eval(args.test_cases, metrics=metrics, output_path=args.output, repeats=args.repeats)
