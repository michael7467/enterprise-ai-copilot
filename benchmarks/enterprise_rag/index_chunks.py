"""
Load the Drive chunks and their BGE-M3 vectors into Elasticsearch.

Each chunk is indexed twice from the same record:
  - "text"      -> BM25 keyword search (English analyzer: stemming, stop words)
  - "embedding" -> semantic (kNN) search with the BGE-M3 vector

Run from the project root, with Elasticsearch running:
    python benchmarks/enterprise_rag/index_chunks.py

Re-running deletes and rebuilds the index, so it is always a clean copy of the files.
"""
import json
import time
from pathlib import Path

import numpy as np
from elasticsearch import Elasticsearch, helpers

ES_URL = "http://localhost:9200"
INDEX = "drive_chunks_structure_v1"

CHUNKS = Path("data/chunks/drive_structure_v1.jsonl")
VECTORS = Path("data/embeddings/bge-m3/vectors.npy")
VECTOR_IDS = Path("data/embeddings/bge-m3/chunk_ids.json")
QUESTIONS = Path("data/eval/drive_questions.jsonl")

SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,  # single node: no copies, so the index health is green
}

MAPPINGS = {
    "properties": {
        "chunk_id": {"type": "keyword"},
        "doc_id": {"type": "keyword"},
        "title": {"type": "text", "analyzer": "english"},
        "section": {"type": "text", "analyzer": "english"},
        "source": {"type": "keyword"},     # later: filter by source
        "strategy": {"type": "keyword"},   # later: compare chunking strategies in one index
        "position": {"type": "integer"},
        "n_tokens": {"type": "integer"},
        "text": {"type": "text", "analyzer": "english"},  # header + body: what BM25 searches
        "body": {"type": "text", "index": False},         # stored for the answer generator, not searched
        "embedding": {
            "type": "dense_vector",
            "dims": 1024,
            "index": True,
            "similarity": "cosine",
            # Full-precision HNSW. Elasticsearch's default compresses vectors, which saves memory
            # but changes results slightly; for 35k vectors, exact numbers are worth ~150 MB.
            "index_options": {"type": "hnsw"},
        },
    }
}


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def actions(chunks: list[dict], vectors: np.ndarray):
    for chunk, vector in zip(chunks, vectors):
        yield {
            "_index": INDEX,
            "_id": chunk["chunk_id"],
            "_source": {**chunk, "embedding": vector.astype(np.float32).tolist()},
        }


def main():
    # 1. Load files and check that vectors and chunks line up
    chunks = load_jsonl(CHUNKS)
    vectors = np.load(VECTORS)
    vector_ids = json.loads(VECTOR_IDS.read_text(encoding="utf-8"))
    if vector_ids != [c["chunk_id"] for c in chunks]:
        raise SystemExit("Vectors do not match the chunk file. Re-run the embedding for these chunks.")
    print(f"Chunks: {len(chunks)}   vectors: {vectors.shape}")

    # 2. Connect
    es = Elasticsearch(ES_URL, request_timeout=120)
    info = es.info()
    print(f"Connected to Elasticsearch {info['version']['number']}")

    # 3. Create a fresh index
    if es.indices.exists(index=INDEX):
        es.indices.delete(index=INDEX)
        print(f"Deleted old index '{INDEX}'")
    es.indices.create(index=INDEX, settings=SETTINGS, mappings=MAPPINGS)
    es.indices.put_settings(index=INDEX, settings={"refresh_interval": "-1"})  # faster bulk loading

    # 4. Bulk load
    start, done = time.time(), 0
    for ok, item in helpers.streaming_bulk(es, actions(chunks, vectors), chunk_size=200, raise_on_error=True):
        done += 1
        if done % 5000 == 0:
            print(f"  indexed {done}/{len(chunks)}   ({done / (time.time() - start):.0f} chunks/s)")

    es.indices.put_settings(index=INDEX, settings={"refresh_interval": "1s"})
    es.indices.refresh(index=INDEX)
    count = es.count(index=INDEX)["count"]
    print(f"\nIndexed {count} chunks into '{INDEX}' in {time.time() - start:.0f} s")
    if count != len(chunks):
        raise SystemExit(f"Expected {len(chunks)} chunks in the index, found {count}.")

    # 5. Smoke tests
    # BM25: the first evaluation question, top 3 chunks
    question = load_jsonl(QUESTIONS)[0]
    res = es.search(index=INDEX, query={"match": {"text": question["question"]}}, size=3,
                    source_includes=["doc_id", "section", "title"])
    print(f"\nBM25 test. Question: {question['question'][:100]}...")
    print(f"Expected document: {question['expected_doc_ids']}")
    for hit in res["hits"]["hits"]:
        s = hit["_source"]
        mark = "  <- expected" if s["doc_id"] in question["expected_doc_ids"] else ""
        print(f"  {hit['_score']:6.2f}  {s['doc_id']}  {s['title'][:50]} | {s['section'][:30]}{mark}")

    # kNN: searching with a chunk's own vector must return that chunk first
    probe = chunks[1234]
    res = es.search(index=INDEX, size=1, source_includes=["chunk_id"],
                    knn={"field": "embedding", "query_vector": vectors[1234].astype(np.float32).tolist(),
                         "k": 1, "num_candidates": 50})
    top = res["hits"]["hits"][0]["_source"]["chunk_id"]
    print(f"\nkNN test: searched with the vector of {probe['chunk_id']}, got {top} "
          f"-> {'OK' if top == probe['chunk_id'] else 'PROBLEM'}")


if __name__ == "__main__":
    main()