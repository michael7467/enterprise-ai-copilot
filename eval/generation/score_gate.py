"""
Can the reranker score tell us when to abstain? Uses saved scores only (no model, no Elasticsearch).

For every question, "top score" = the highest reranker score among the top 10 hybrid chunks
(the chunks the generator's sources come from).

  Answerable:   the expected document is among the 4 sources given to the model.
  Unanswerable: (a) natural: retrieval missed the expected document;
                (b) simulated: the expected document's chunks are removed from the candidates,
                    so only similar-topic documents remain (the trap seen in qst_0291 / qst_0297).

A gate "abstain if top score < t" is good if it blocks unanswerable questions
while keeping answerable ones.

Run from the project root:
    python eval/generation/score_gate.py
"""
import json
import statistics
from datetime import datetime
from pathlib import Path

CANDIDATES = Path("data/eval/rerank_candidates.jsonl")
SCORES = Path("data/eval/rerank_scores.json")
RESULTS_DIR = Path("eval/results")
RERANK_DEPTH = 10
TOP_K = 4
KEEP_LEVELS = (1.00, 0.97, 0.95, 0.90, 0.85, 0.80, 0.70)  # share of answerable questions to keep


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def head(cands: list[dict], scores: list[float]) -> list[tuple[float, dict]]:
    """Top RERANK_DEPTH chunks (hybrid order) with their reranker scores, best score first."""
    return sorted(zip(scores[:RERANK_DEPTH], cands[:RERANK_DEPTH]), key=lambda x: -x[0])


def auc(pos: list[float], neg: list[float]) -> float:
    """Probability that a random answerable question scores higher than a random unanswerable one."""
    pairs = [(p > n) + 0.5 * (p == n) for p in pos for n in neg]
    return sum(pairs) / len(pairs)


def main():
    items = load_jsonl(CANDIDATES)
    cache = json.loads(SCORES.read_text(encoding="utf-8"))["scores"]

    answerable, natural, simulated = [], [], []
    for it in items:
        cands, scores = it["candidates"], cache[it["question_id"]]["scores"]
        expected = set(it["expected_doc_ids"])
        ranked = head(cands, scores)
        sources = [c for _, c in ranked][:TOP_K]
        top = ranked[0][0]
        if any(c["doc_id"] in expected for c in sources):
            answerable.append((top, it["question_id"]))
            # simulated unanswerable: drop the expected document, keep everything else in hybrid order
            kept = [(c, s) for c, s in zip(cands, scores) if c["doc_id"] not in expected]
            if kept:
                c2, s2 = zip(*kept)
                simulated.append((head(list(c2), list(s2))[0][0], it["question_id"]))
        else:
            natural.append((top, it["question_id"]))

    pos = [s for s, _ in answerable]
    neg = [s for s, _ in natural + simulated]
    lines = [
        "# Abstention gate: reranker top score\n",
        f"Answerable: {len(pos)}. Unanswerable: {len(natural)} natural + {len(simulated)} simulated "
        f"(expected document removed).\n",
        "| Group | n | min | median | max |", "|---|---|---|---|---|",
    ]
    for name, group in (("Answerable", answerable), ("Unanswerable (natural)", natural),
                        ("Unanswerable (simulated)", simulated)):
        s = [x for x, _ in group]
        if s:
            lines.append(f"| {name} | {len(s)} | {min(s):.3f} | {statistics.median(s):.3f} | {max(s):.3f} |")

    lines.append(f"\n**Separation (AUC): {auc(pos, neg):.2f}** "
                 "(1.0 = a threshold separates them perfectly, 0.5 = the score is no help)\n")

    lines += ["| Threshold: abstain if top score below | Answerable kept | Unanswerable blocked "
              "(natural) | Unanswerable blocked (simulated) |", "|---|---|---|---|"]
    sorted_pos = sorted(pos)
    seen = set()
    for keep in KEEP_LEVELS:
        idx = max(0, int(round((1 - keep) * len(sorted_pos))))
        t = sorted_pos[min(idx, len(sorted_pos) - 1)]
        if t in seen:
            continue
        seen.add(t)
        kept = sum(p >= t for p in pos) / len(pos)
        nat = sum(n < t for n, _ in natural) / len(natural) if natural else float("nan")
        sim = sum(n < t for n, _ in simulated) / len(simulated)
        lines.append(f"| {t:.3f} | {kept:.0%} | {nat:.0%} | {sim:.0%} |")

    lines.append("\nNatural unanswerable questions: " +
                 ", ".join(f"{q} (top score {s:.3f})" for s, q in sorted(natural)))
    lines.append("Lowest-scoring answerable questions: " +
                 ", ".join(f"{q} ({s:.3f})" for s, q in sorted(answerable)[:5]))
    lines.append("\nThe threshold is chosen on the same questions it is tested on, so the "
                 "numbers are optimistic. Simulated questions are a stand-in, not real user questions.")

    report = "\n".join(lines)
    print(report)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"score_gate_{datetime.now():%Y%m%d_%H%M}.md"
    out.write_text(report, encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()