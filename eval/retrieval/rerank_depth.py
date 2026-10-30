"""
How many candidates does the reranker need? Uses the saved reranker scores only:
no model, no Elasticsearch, runs in seconds.

For each depth N, the top N hybrid chunks are reordered by the reranker score and the
rest keep their hybrid order behind them, which is what a production setting would do.

Run from the project root (after rerank_eval.py rerank has finished):
    python eval/retrieval/rerank_depth.py
"""
import json
from datetime import datetime

import eval_drive_retrieval as ev
import rerank_eval as rr

DEPTHS = (0, 5, 10, 20, 30, 40, 50)  # 0 = no reranking (hybrid only)


def ranking_at_depth(item: dict, scores: list[float], depth: int) -> list[str]:
    cands = [(c["chunk_id"], c["doc_id"]) for c in item["candidates"]]
    head = sorted(zip(scores[:depth], cands[:depth]), key=lambda x: -x[0])  # stable sort
    return ev.to_docs([c for _, c in head] + cands[depth:])


def main():
    items = ev.load_jsonl(rr.CANDIDATES)
    cache = json.loads(rr.SCORES.read_text(encoding="utf-8"))
    missing = [it["question_id"] for it in items if it["question_id"] not in cache["scores"]]
    if missing:
        raise SystemExit(f"No reranker scores for {len(missing)} questions. Run: rerank_eval.py rerank")

    seconds_full = cache.get("seconds_per_question")
    semantic = [i for i, it in enumerate(items) if it.get("question_type") == "semantic"]

    lines = [f"# Reranking depth: quality vs cost\n",
             f"{ev.CORPUS}. {len(items)} questions ({len(semantic)} semantic). "
             f"Reranker: {cache['model']}.\n",
             "| Reranked chunks | R@1 | R@5 | R@10 | MRR | Semantic R@1 | Semantic MRR | Est. s/question |",
             "|---|---|---|---|---|---|---|---|"]
    rows = []
    for depth in DEPTHS:
        docs = [ranking_at_depth(it, cache["scores"][it["question_id"]]["scores"], depth) for it in items]
        m = ev.metrics(docs, items)
        ms = ev.metrics([docs[i] for i in semantic], [items[i] for i in semantic])
        # Reranking time grows linearly with the number of chunks scored.
        cost = seconds_full * depth / rr.N_CANDIDATES if seconds_full else float("nan")
        label = "0 (hybrid only)" if depth == 0 else str(depth)
        lines.append(f"| {label} | {m['recall@1']:.0%} | {m['recall@5']:.0%} | {m['recall@10']:.0%} "
                     f"| {m['MRR']:.3f} | {ms['recall@1']:.0%} | {ms['MRR']:.3f} | {cost:.0f} |")
        rows.append({"depth": depth, "metrics": m, "semantic": ms, "est_seconds_per_question": cost})

    lines.append(f"\nCost is estimated from the measured {seconds_full:.0f} s per question for "
                 f"{rr.N_CANDIDATES} chunks on {cache.get('device', '?')}.")
    report = "\n".join(lines)
    print(report)

    stamp = f"{datetime.now():%Y%m%d_%H%M}"
    (ev.RESULTS_DIR / f"rerank_depth_{stamp}.md").write_text(report, encoding="utf-8")
    (ev.RESULTS_DIR / f"rerank_depth_{stamp}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nSaved eval/results/rerank_depth_{stamp}.md and .json")


if __name__ == "__main__":
    main()