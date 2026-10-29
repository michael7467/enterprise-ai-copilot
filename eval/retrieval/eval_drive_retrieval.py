"""
Retrieval evaluation on the EnterpriseRAG-Bench Drive questions: BM25 vs semantic vs hybrid (RRF).

Run from the project root, with Elasticsearch running and the index built:
    python eval/retrieval/eval_drive_retrieval.py

Metrics are at document level: chunks are mapped to their documents, duplicates removed,
and the ranking of distinct documents is compared with the expected documents.
    recall@k  share of expected documents found in the top k documents (averaged over questions)
    MRR       1 / rank of the first expected document (0 if not in the top 100 chunks)

Writes eval/results/drive_retrieval_<date>.json (small; commit it, it backs the README table).
"""
import json
import statistics
import time
from datetime import datetime
from pathlib import Path

import numpy as np

ES_URL = "http://localhost:9200"
INDEX = "drive_chunks_structure_v1"
CORPUS = "5,000 Drive documents (EnterpriseRAG-Bench), structure_v1 chunks"

QUESTIONS = Path("data/eval/drive_questions.jsonl")
QVEC = Path("data/embeddings/bge-m3/question_vectors.npy")
QVEC_IDS = Path("data/embeddings/bge-m3/question_ids.json")
RESULTS_DIR = Path("eval/results")

TOP_CHUNKS = 100       # chunks retrieved per method before mapping to documents
NUM_CANDIDATES = 500   # kNN search breadth (higher = closer to exact search)
RRF_K = 60             # standard RRF constant
KS = (1, 5, 10)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------- Question vectors (computed once, then cached) ----------------
def question_vectors(questions: list[dict]) -> np.ndarray:
    ids = [q["question_id"] for q in questions]
    if QVEC.exists() and QVEC_IDS.exists() and json.loads(QVEC_IDS.read_text(encoding="utf-8")) == ids:
        return np.load(QVEC).astype(np.float32)

    print("Embedding the questions with BGE-M3 on CPU (first run only, about 1-3 minutes)...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-m3", device="cpu")
    model.max_seq_length = 512
    vectors = model.encode([q["question"] for q in questions], batch_size=8,
                           normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)
    QVEC.parent.mkdir(parents=True, exist_ok=True)
    np.save(QVEC, vectors)
    QVEC_IDS.write_text(json.dumps(ids), encoding="utf-8")
    return vectors


# ---------------- Retrieval methods: each returns [(chunk_id, doc_id), ...] best first ----------------
def bm25(es, question: dict) -> list[tuple[str, str]]:
    res = es.search(index=INDEX, size=TOP_CHUNKS, source_includes=["doc_id"],
                    query={"match": {"text": question["question"]}})
    return [(h["_id"], h["_source"]["doc_id"]) for h in res["hits"]["hits"]]


def semantic(es, vector: np.ndarray) -> list[tuple[str, str]]:
    res = es.search(index=INDEX, size=TOP_CHUNKS, source_includes=["doc_id"],
                    knn={"field": "embedding", "query_vector": vector.tolist(),
                         "k": TOP_CHUNKS, "num_candidates": NUM_CANDIDATES})
    return [(h["_id"], h["_source"]["doc_id"]) for h in res["hits"]["hits"]]


def rrf(*rankings: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Reciprocal rank fusion: score = sum over lists of 1 / (RRF_K + rank). Ranks only, no raw scores."""
    scores, doc_of = {}, {}
    for ranking in rankings:
        for rank, (chunk_id, doc_id) in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
            doc_of[chunk_id] = doc_id
    return [(c, doc_of[c]) for c in sorted(scores, key=scores.get, reverse=True)]


# ---------------- Metrics ----------------
def to_docs(ranking: list[tuple[str, str]]) -> list[str]:
    return list(dict.fromkeys(doc_id for _, doc_id in ranking))  # distinct documents, in order


def first_rank(docs: list[str], expected: list[str]) -> int | None:
    for rank, doc_id in enumerate(docs, start=1):
        if doc_id in expected:
            return rank
    return None


def metrics(doc_rankings: list[list[str]], questions: list[dict]) -> dict:
    out = {}
    for k in KS:
        out[f"recall@{k}"] = statistics.mean(
            len(set(docs[:k]) & set(q["expected_doc_ids"])) / len(q["expected_doc_ids"])
            for docs, q in zip(doc_rankings, questions))
    ranks = [first_rank(docs, q["expected_doc_ids"]) for docs, q in zip(doc_rankings, questions)]
    out["MRR"] = statistics.mean(1 / r if r else 0.0 for r in ranks)
    return out


# ---------------- Main ----------------
def main():
    from elasticsearch import Elasticsearch

    questions = load_jsonl(QUESTIONS)
    vectors = question_vectors(questions)
    es = Elasticsearch(ES_URL, request_timeout=60)
    print(f"Questions: {len(questions)}   index: {INDEX} ({es.count(index=INDEX)['count']} chunks)\n")

    docs = {"BM25": [], "Semantic (BGE-M3)": [], "Hybrid (RRF)": []}
    latency = {"BM25": [], "Semantic (BGE-M3)": [], "Hybrid (RRF)": []}
    for q, v in zip(questions, vectors):
        t0 = time.perf_counter()
        b = bm25(es, q)
        t1 = time.perf_counter()
        s = semantic(es, v)
        t2 = time.perf_counter()
        h = rrf(b, s)
        t3 = time.perf_counter()
        docs["BM25"].append(to_docs(b))
        docs["Semantic (BGE-M3)"].append(to_docs(s))
        docs["Hybrid (RRF)"].append(to_docs(h))
        latency["BM25"].append(t1 - t0)
        latency["Semantic (BGE-M3)"].append(t2 - t1)
        latency["Hybrid (RRF)"].append(t3 - t0)  # both searches + fusion

    # Summary table
    results = {m: metrics(d, questions) for m, d in docs.items()}
    header = f"{'Method':20s}" + "".join(f"{f'R@{k}':>8s}" for k in KS) + f"{'MRR':>8s}{'ms/query':>10s}"
    print(header)
    print("-" * len(header))
    for m, r in results.items():
        ms = statistics.median(latency[m]) * 1000
        print(f"{m:20s}" + "".join(f"{r[f'recall@{k}']:8.0%}" for k in KS) + f"{r['MRR']:8.3f}{ms:10.0f}")
    print("(Latency excludes embedding the question; semantic search needs that too, about 50-200 ms on CPU.)")

    # Per-question ranks: where each method put the first expected document
    per_question = []
    print("\nRank of the expected document per question (- = not in the top 100 chunks):")
    print(f"{'question':10s}{'BM25':>6s}{'Sem':>6s}{'Hyb':>6s}   question")
    for i, q in enumerate(questions):
        ranks = {m: first_rank(docs[m][i], q["expected_doc_ids"]) for m in docs}
        per_question.append({"question_id": q["question_id"], "question": q["question"],
                             "question_type": q.get("question_type"), "expected_doc_ids": q["expected_doc_ids"],
                             "ranks": ranks})
        cells = "".join(f"{(str(r) if r else '-'):>6s}" for r in ranks.values())
        missed = all((r is None or r > 10) for r in ranks.values())
        flag = "  MISSED BY ALL (top 10)" if missed else ""
        print(f"{q['question_id']:10s}{cells}   {q['question'][:70]}{flag}")

    # Save the run
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"drive_retrieval_{datetime.now():%Y%m%d_%H%M}.json"
    out.write_text(json.dumps({
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "index": INDEX,
        "corpus": CORPUS,
        "questions": len(questions),
        "config": {"top_chunks": TOP_CHUNKS, "num_candidates": NUM_CANDIDATES, "rrf_k": RRF_K,
                   "embedding_model": "BAAI/bge-m3", "bm25_analyzer": "english"},
        "metrics": results,
        "median_latency_ms": {m: statistics.median(v) * 1000 for m, v in latency.items()},
        "per_question": per_question,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()