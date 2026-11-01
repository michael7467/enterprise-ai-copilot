"""
Compare prompts (and the reranker-score gate) on answering vs abstaining.
Reads the generation caches only: no model or Elasticsearch needed.

Run from the project root, after these runs (each resumable, about 1 hour on CPU):
    python eval/generation/generate_answers.py                               # v1, answerable
    python eval/generation/generate_answers.py --unanswerable                # v1, unanswerable
    python eval/generation/generate_answers.py --prompt v2                   # v2, answerable
    python eval/generation/generate_answers.py --prompt v2 --unanswerable    # v2, unanswerable
then:
    python eval/generation/compare_abstention.py

Groups:
    Answerable   = expected document among the sources. Good outcome: answered, citing it.
    Unanswerable = expected document missing (3 natural retrieval misses + the simulated set).
                   Good outcome: abstained.
Gate: if the top reranker score is below the threshold, abstain without calling the model.
"""
import json
import statistics
from datetime import datetime
from pathlib import Path

MODEL = "qwen3_8b"
PROMPTS = ("v1", "v2")
THRESHOLDS = (None, 0.6, 0.75)
CANDIDATES = Path("data/eval/rerank_candidates.jsonl")
SCORES = Path("data/eval/rerank_scores.json")
RERANK_DEPTH = 10
RESULTS_DIR = Path("eval/results")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def gate_scores() -> tuple[dict, dict]:
    """Top reranker score per question: normal, and with the expected document removed."""
    scores = json.loads(SCORES.read_text(encoding="utf-8"))["scores"]
    normal, removed = {}, {}
    for it in load_jsonl(CANDIDATES):
        s = scores[it["question_id"]]["scores"]
        normal[it["question_id"]] = max(s[:RERANK_DEPTH])
        kept = [x for c, x in zip(it["candidates"], s) if c["doc_id"] not in set(it["expected_doc_ids"])]
        removed[it["question_id"]] = max(kept[:RERANK_DEPTH]) if kept else 0.0
    return normal, removed


def file_for(prompt: str, unanswerable: bool) -> Path:
    name = MODEL + ("" if prompt == "v1" else f"_{prompt}") + ("_unanswerable" if unanswerable else "")
    return Path(f"data/eval/generation_{name}.jsonl")


def pct(xs: list[bool]) -> str:
    return f"{statistics.mean(1.0 if x else 0.0 for x in xs):.0%}" if xs else "n/a"


def main():
    normal, removed = gate_scores()
    lines = ["# Answering vs abstaining: prompt and score gate\n",
             "| Prompt | Gate | Answerable: answered, citing the expected doc | Answerable: wrongly abstained "
             "| Unanswerable: correctly abstained | n (answerable / unanswerable) |",
             "|---|---|---|---|---|---|"]
    found_any = False
    for prompt in PROMPTS:
        ans_file, una_file = load_jsonl(file_for(prompt, False)), load_jsonl(file_for(prompt, True))
        if not ans_file:
            lines.append(f"| {prompt} | | *not run yet* | | | |")
            continue
        found_any = True
        answerable = [r for r in ans_file if r["expected_in_sources"]]
        natural = [r for r in ans_file if not r["expected_in_sources"]]
        unanswerable = [(r, normal[r["question_id"]]) for r in natural] + \
                       [(r, removed[r["question_id"]]) for r in una_file]
        for t in THRESHOLDS:
            passes = (lambda score: True) if t is None else (lambda score, t=t: score >= t)
            good_ans = [passes(normal[r["question_id"]]) and not r["abstained"] and r["cites_expected"]
                        for r in answerable]
            false_abs = [(not passes(normal[r["question_id"]])) or r["abstained"] for r in answerable]
            good_abs = [(not passes(score)) or r["abstained"] for r, score in unanswerable]
            label = "none" if t is None else f"score < {t}"
            note = "" if una_file else " (natural only: run --unanswerable)"
            lines.append(f"| {prompt} | {label} | {pct(good_ans)} | {pct(false_abs)} | {pct(good_abs)}{note} "
                         f"| {len(answerable)} / {len(unanswerable)} |")

    if not found_any:
        raise SystemExit("No generation results found. Run generate_answers.py first.")
    lines.append("\n'Answered, citing the expected doc' is an automatic check: it does not prove the answer "
                 "is correct. Read the reports. Thresholds were chosen on the same questions (optimistic).")
    report = "\n".join(lines)
    print(report)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"abstention_{datetime.now():%Y%m%d_%H%M}.md"
    out.write_text(report, encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()