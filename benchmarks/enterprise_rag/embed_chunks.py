"""
Embed the Drive chunks with BGE-M3 (dense vectors) and save them to disk.

It is safe to stop (Ctrl + C) and run again: finished shards are kept and skipped.

Run from the project root:
    python benchmarks/enterprise_rag/embed_chunks.py

Writes (inside data/, which git ignores):
    data/embeddings/bge-m3/shards/        partial results while it runs
    data/embeddings/bge-m3/vectors.npy    all vectors (float16), one row per chunk
    data/embeddings/bge-m3/chunk_ids.json the chunk_id of each row, in the same order
"""
import json
import os
import time
from pathlib import Path

import numpy as np

CHUNKS = Path("data/chunks/drive_structure_v1.jsonl")
QUESTIONS = Path("data/eval/drive_questions.jsonl")
OUT_DIR = Path("data/embeddings/bge-m3")
MODEL = "BAAI/bge-m3"
SHARD_SIZE = 1000      # chunks per saved file; progress is never lost beyond one shard
MAX_SEQ_LENGTH = 512   # chunks are at most 500 tokens, so nothing gets cut off


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_model():
    import torch
    from sentence_transformers import SentenceTransformer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL, device=device)
    model.max_seq_length = MAX_SEQ_LENGTH
    if device == "cuda":
        model.half()  # twice as fast on GPU, no meaningful loss in quality
    batch_size = 32 if device == "cuda" else 8
    print(f"Model: {MODEL}   device: {device}   batch size: {batch_size}")
    return model, batch_size


def embed(model, texts: list[str], batch_size: int) -> np.ndarray:
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,  # unit length, so dot product = cosine similarity
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vectors.astype(np.float16)


def main():
    chunks = load_jsonl(CHUNKS)
    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    print(f"Chunks to embed: {len(texts)}")

    # Never mix vectors from two different chunk files.
    shard_dir = OUT_DIR / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    ids_path = OUT_DIR / "chunk_ids.json"
    if ids_path.exists() and json.loads(ids_path.read_text(encoding="utf-8")) != ids:
        raise SystemExit(
            "The chunk file changed since the last run.\n"
            f"Delete the folder {OUT_DIR} and run again."
        )
    ids_path.write_text(json.dumps(ids), encoding="utf-8")

    model, batch_size = load_model()

    n_shards = -(-len(texts) // SHARD_SIZE)
    start, embedded_now = time.time(), 0
    for s in range(n_shards):
        path = shard_dir / f"shard_{s:05d}.npy"
        if path.exists():
            continue
        lo, hi = s * SHARD_SIZE, min(len(texts), (s + 1) * SHARD_SIZE)
        vectors = embed(model, texts[lo:hi], batch_size)

        tmp = path.with_suffix(".tmp.npy")  # write then rename: an interrupted save never leaves a broken shard
        np.save(tmp, vectors)
        os.replace(tmp, path)

        embedded_now += hi - lo
        rate = embedded_now / (time.time() - start)
        remaining_min = (len(texts) - hi) / rate / 60
        print(f"  shard {s + 1}/{n_shards}   {hi}/{len(texts)} chunks   "
              f"{rate:.1f} chunks/s   about {remaining_min:.0f} min left")

    # Combine the shards into one file.
    vectors = np.concatenate([np.load(shard_dir / f"shard_{s:05d}.npy") for s in range(n_shards)])
    assert len(vectors) == len(ids), "number of vectors does not match number of chunks"
    np.save(OUT_DIR / "vectors.npy", vectors)
    print(f"\nSaved {vectors.shape[0]} vectors of {vectors.shape[1]} dimensions to {OUT_DIR / 'vectors.npy'}")

    # Quick sanity check: plain semantic search over all chunks, no Elasticsearch yet.
    questions = load_jsonl(QUESTIONS)
    q_vectors = embed(model, [q["question"] for q in questions], batch_size).astype(np.float32)
    scores = q_vectors @ vectors.astype(np.float32).T
    doc_of = np.array([c["doc_id"] for c in chunks])
    hits = 0
    for q, row in zip(questions, scores):
        top_chunks = np.argsort(-row)[:100]
        top_docs = list(dict.fromkeys(doc_of[top_chunks]))[:10]  # first 10 distinct documents
        hits += bool(set(q["expected_doc_ids"]) & set(top_docs))
    print(f"Quick check: an expected document is in the top 10 for {hits} of {len(questions)} questions "
          f"({hits / len(questions):.0%}).")


if __name__ == "__main__":
    main()