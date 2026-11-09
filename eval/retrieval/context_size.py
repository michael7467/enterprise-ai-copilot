
import json
import statistics
from datetime import datetime
from pathlib import Path

ES_URL = "http://127.0.0.1:9200"
INDEX = "drive_chunks_structure_v1"
QUESTIONS = Path("data/eval/drive_questions.jsonl")
QVEC = Path("data/embeddings/bge-m3/question_vectors.npy")
QVEC_IDS = Path("data/embeddings/bge-m3/question_ids.json")
RESULTS_DIR = Path("eval/results")

TOP_CHUNKS = 100
NUM_CANDIDATES = 500
RRF_K = 60
KS = (1, 2, 3, 4, 5, 6)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def bm25(es, text: str) -> list[tuple[str, str]]:
    res = es.search(index=INDEX, size=TOP_CHUNKS, source_includes=["doc_id"], query={"match": {"text": text}})
    return [(h["_id"], h["_source"]["doc_id"]) for h in res["hits"]["hits"]]


def semantic(es, vector) -> list[tuple[str, str]]:
    res = es.search(index=INDEX, size=TOP_CHUNKS, source_includes=["doc_id"],
                    knn={"field": "embedding", "query_vector": list(map(float, vector)),
                         "k": TOP_CHUNKS, "num_candidates": NUM_CANDIDATES})
    return [(h["_id"], h["_source"]["doc_id"]) for h in res["hits"]["hits"]]


def rrf(*rankings):
    scores, doc_of = {}, {}
    for ranking in rankings:
        for rank, (chunk_id, doc_id) in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
            doc_of[chunk_id] = doc_id
    return [(c, doc_of[c]) for c in sorted(scores, key=scores.get, reverse=True)]


def first_hit(ranking, expected: list[str]) -> int | None:
    """Position (1-based) of the first chunk from an expected document."""
    for pos, (_, doc_id) in enumerate(ranking, start=1):
        if doc_id in expected:
            return pos
    return None


def hit_rates(positions: list[int | None]) -> dict[str, float]:
    return {f"hit@{k}": statistics.mean(1.0 if p is not None and p <= k else 0.0 for p in positions) for k in KS}


def cached_vectors(questions: list[dict]):
    if not (QVEC.exists() and QVEC_IDS.exists()):
        return None
    if json.loads(QVEC_IDS.read_text(encoding="utf-8")) != [q["question_id"] for q in questions]:
        return None
    import numpy as np
    return np.load(QVEC)


def main():
    from elasticsearch import Elasticsearch

    questions = load_jsonl(QUESTIONS)
    es = Elasticsearch(ES_URL, request_timeout=60)
    vectors = cached_vectors(questions)
    methods = ["BM25 (light mode)"] + (["Hybrid (RRF)"] if vectors is not None else [])
    if vectors is None:
        print("Question vectors not cached: running BM25 only.")

    positions = {m: [] for m in methods}
    for i, q in enumerate(questions):
        b = bm25(es, q["question"])
        positions["BM25 (light mode)"].append(first_hit(b, q["expected_doc_ids"]))
        if vectors is not None:
            positions["Hybrid (RRF)"].append(first_hit(rrf(b, semantic(es, vectors[i])), q["expected_doc_ids"]))

    results = {m: hit_rates(p) for m, p in positions.items()}
    print(f"Questions: {len(questions)}. Share of questions where the right document is in the first k chunks:\n")
    header = f"{'Method':20s}" + "".join(f"{f'k={k}':>8s}" for k in KS)
    print(header)
    print("-" * len(header))
    for m, r in results.items():
        print(f"{m:20s}" + "".join(f"{r[f'hit@{k}']:8.0%}" for k in KS))

    lost = {m: [q["question_id"] for q, p in zip(questions, positions[m]) if p == 4] for m in methods}
    for m, ids in lost.items():
        print(f"\n{m}: going from 4 to 3 chunks loses {len(ids)} question(s): {', '.join(ids) or 'none'}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"context_size_{datetime.now():%Y%m%d_%H%M}.json"
    out.write_text(json.dumps({
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "index": INDEX,
        "questions": len(questions),
        "metric": "hit@k at chunk level: an expected document among the first k chunks",
        "results": results,
        "first_hit_position": {m: dict(zip([q["question_id"] for q in questions], p)) for m, p in positions.items()},
    }, indent=2), encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()