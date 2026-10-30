"""
Rerank the hybrid results with a cross-encoder (BGE-reranker-v2-m3) and measure the effect.

Two steps, so Elasticsearch and the reranker never need memory at the same time:

  1. Collect candidates (Elasticsearch running):
       python eval/retrieval/rerank_eval.py collect
     -> data/eval/rerank_candidates.jsonl   top 50 hybrid chunks per question, with their text

  2. Rerank and evaluate (stop Elasticsearch first to free memory):
       python eval/retrieval/rerank_eval.py rerank
     -> data/eval/rerank_scores.json        cached scores: safe to stop with Ctrl + C and resume
     -> eval/results/rerank_<date>.json     metrics before and after, overall and per question type
"""
import json
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import eval_drive_retrieval as ev  # same folder: reuse the exact search and metric code

RERANKER = "BAAI/bge-reranker-v2-m3"
N_CANDIDATES = 50   # hybrid chunks the reranker re-scores per question
MAX_LENGTH = 640    # question + chunk (at most 500 tokens) fits without cutting the chunk
CANDIDATES = Path("data/eval/rerank_candidates.jsonl")
SCORES = Path("data/eval/rerank_scores.json")


# ---------------- Step 1: collect candidates from Elasticsearch ----------------
def collect():
    from elasticsearch import Elasticsearch

    es = Elasticsearch(ev.ES_URL, request_timeout=60)
    questions = ev.load_jsonl(ev.QUESTIONS)
    vectors = ev.question_vectors(questions)
    CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    with CANDIDATES.open("w", encoding="utf-8") as f:
        for q, v in zip(questions, vectors):
            fused = ev.rrf(ev.bm25(es, q), ev.semantic(es, v))[:N_CANDIDATES]
            res = es.search(index=ev.INDEX, size=len(fused), source_includes=["text"],
                            query={"ids": {"values": [c for c, _ in fused]}})
            text_of = {h["_id"]: h["_source"]["text"] for h in res["hits"]["hits"]}
            f.write(json.dumps({
                "question_id": q["question_id"],
                "question": q["question"],
                "question_type": q.get("question_type"),
                "expected_doc_ids": q["expected_doc_ids"],
                "candidates": [{"chunk_id": c, "doc_id": d, "text": text_of[c]} for c, d in fused],
            }, ensure_ascii=False) + "\n")
    print(f"Saved the top {N_CANDIDATES} hybrid chunks for {len(questions)} questions to {CANDIDATES}")
    print("You can stop Elasticsearch now and run:  python eval/retrieval/rerank_eval.py rerank")


# ---------------- Step 2: rerank and evaluate ----------------
def load_model():
    import torch
    from sentence_transformers import CrossEncoder

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CrossEncoder(RERANKER, max_length=MAX_LENGTH, device=device)
    batch_size = 32 if device == "cuda" else 8
    print(f"Reranker: {RERANKER}   device: {device}   batch size: {batch_size}")
    return model, batch_size, device


def score_all(items: list[dict]) -> dict:
    """Score every (question, chunk) pair; cached per question so a stopped run resumes."""
    cache = json.loads(SCORES.read_text(encoding="utf-8")) if SCORES.exists() else {}
    if cache.get("model") != RERANKER:
        cache = {"model": RERANKER, "scores": {}}

    def done(item):
        cached = cache["scores"].get(item["question_id"])
        return cached and cached["chunk_ids"] == [c["chunk_id"] for c in item["candidates"]]

    todo = [it for it in items if not done(it)]
    if todo:
        model, batch_size, device = load_model()
        print(f"Reranking {len(todo)} questions x {N_CANDIDATES} chunks...")
        times = []
        for n, it in enumerate(todo, 1):
            t0 = time.perf_counter()
            scores = model.predict([(it["question"], c["text"]) for c in it["candidates"]],
                                   batch_size=batch_size, show_progress_bar=False)
            times.append(time.perf_counter() - t0)
            cache["scores"][it["question_id"]] = {
                "chunk_ids": [c["chunk_id"] for c in it["candidates"]],
                "scores": [float(s) for s in scores],
            }
            SCORES.write_text(json.dumps(cache), encoding="utf-8")
            left = statistics.mean(times) * (len(todo) - n) / 60
            print(f"  {n}/{len(todo)}  {times[-1]:.1f} s   about {left:.0f} min left")
        cache["seconds_per_question"] = statistics.median(times)
        cache["device"] = device
        SCORES.write_text(json.dumps(cache), encoding="utf-8")
    return cache


def rankings(items: list[dict], cache: dict) -> tuple[list, list]:
    before, after = [], []
    for it in items:
        cands = [(c["chunk_id"], c["doc_id"]) for c in it["candidates"]]
        scores = cache["scores"][it["question_id"]]["scores"]
        # sorted() is stable: equal scores keep their hybrid order
        reranked = [c for _, c in sorted(zip(scores, cands), key=lambda x: -x[0])]
        before.append(ev.to_docs(cands))
        after.append(ev.to_docs(reranked))
    return before, after


def table(rows: list[tuple[str, int, str, dict]]) -> list[str]:
    head = "| Questions | n | Method | " + " | ".join(f"R@{k}" for k in ev.KS) + " | MRR |"
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    for group, n, method, m in rows:
        lines.append(f"| {group} | {n} | {method} | "
                     + " | ".join(f"{m[f'recall@{k}']:.0%}" for k in ev.KS) + f" | {m['MRR']:.3f} |")
    return lines


def rerank():
    items = ev.load_jsonl(CANDIDATES)
    cache = score_all(items)
    before, after = rankings(items, cache)

    # Overall and per question type
    groups = defaultdict(list)
    for i, it in enumerate(items):
        groups[it.get("question_type") or "unknown"].append(i)
    rows, metrics_out = [], {}
    for group, idx in [("all", list(range(len(items))))] + sorted(groups.items(), key=lambda g: -len(g[1])):
        qs = [items[i] for i in idx]
        mb = ev.metrics([before[i] for i in idx], qs)
        ma = ev.metrics([after[i] for i in idx], qs)
        rows += [(group, len(idx), f"Hybrid (top {N_CANDIDATES})", mb), ("", "", "Hybrid + reranker", ma)]
        metrics_out[group] = {"n": len(idx), "hybrid": mb, "hybrid_reranked": ma}

    lines = [f"# Reranking: {RERANKER}\n",
             f"{ev.CORPUS}. Reranker re-scores the top {N_CANDIDATES} hybrid chunks per question.",
             f"Reranking time: {cache.get('seconds_per_question', float('nan')):.1f} s per question "
             f"on {cache.get('device', '?')}.\n"]
    lines += table(rows)

    # Per question: rank of the expected document before and after
    lines.append("\n## Rank of the expected document, before -> after (- = not in the top 50 chunks)\n")
    per_question = []
    for it, b, a in zip(items, before, after):
        rb, ra = ev.first_rank(b, it["expected_doc_ids"]), ev.first_rank(a, it["expected_doc_ids"])
        per_question.append({"question_id": it["question_id"], "question_type": it.get("question_type"),
                             "rank_before": rb, "rank_after": ra})
        if rb != ra:
            better = (ra or 999) < (rb or 999)
            lines.append(f"- {it['question_id']} ({it.get('question_type')}): {rb or '-'} -> {ra or '-'}"
                         f"  {'better' if better else 'WORSE'}")
    unchanged = sum(p["rank_before"] == p["rank_after"] for p in per_question)
    lines.append(f"\n{unchanged} of {len(items)} questions unchanged.")

    report = "\n".join(lines)
    print(report)
    stamp = f"{datetime.now():%Y%m%d_%H%M}"
    ev.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (ev.RESULTS_DIR / f"rerank_{stamp}.md").write_text(report, encoding="utf-8")
    (ev.RESULTS_DIR / f"rerank_{stamp}.json").write_text(json.dumps({
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "reranker": RERANKER, "n_candidates": N_CANDIDATES, "max_length": MAX_LENGTH,
        "corpus": ev.CORPUS, "device": cache.get("device"),
        "seconds_per_question": cache.get("seconds_per_question"),
        "metrics": metrics_out, "per_question": per_question,
    }, indent=2), encoding="utf-8")
    print(f"\nSaved eval/results/rerank_{stamp}.md and .json")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step == "collect":
        collect()
    elif step == "rerank":
        rerank()
    else:
        raise SystemExit("Usage: python eval/retrieval/rerank_eval.py collect | rerank")