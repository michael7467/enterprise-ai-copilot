"""
Failure analysis: for each missed question, show the question, its expected document
(and which of its chunks holds the answer), and what each method retrieved instead.

Run from the project root, with Elasticsearch running:
    python eval/retrieval/inspect_misses.py                      # questions missed by all methods (top 10)
    python eval/retrieval/inspect_misses.py qst_0291 qst_0186    # or any questions you choose

Writes a readable report to eval/results/misses_<date>.md
"""
import json
import re
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

import eval_drive_retrieval as ev  # same folder: reuse the exact search code from the evaluation

VECTORS = Path("data/embeddings/bge-m3/vectors.npy")
VECTOR_IDS = Path("data/embeddings/bge-m3/chunk_ids.json")
STOP = set("""a an the and or of to in on for with by from at as is are was were be been this that these those
what which who whom when where how why does did do it its into than then there their our your about over under
per vs via""".split())


def content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9][a-z0-9\-_.%]*", (text or "").lower()) if len(w) > 2 and w not in STOP}


def answer_overlap(answer: str, chunk: str) -> float:
    """Share of the gold answer's content words that appear in the chunk: points to where the answer lives."""
    words = content_words(answer)
    return len(words & content_words(chunk)) / len(words) if words else 0.0


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def latest_results() -> dict:
    files = sorted(ev.RESULTS_DIR.glob("drive_retrieval_*.json"))
    if not files:
        raise SystemExit("No results file found. Run eval_drive_retrieval.py first.")
    return json.loads(files[-1].read_text(encoding="utf-8"))


def main():
    from elasticsearch import Elasticsearch

    es = Elasticsearch(ev.ES_URL, request_timeout=60)
    questions = ev.load_jsonl(ev.QUESTIONS)
    by_id = {q["question_id"]: q for q in questions}
    qvecs = dict(zip([q["question_id"] for q in questions], ev.question_vectors(questions)))
    chunk_vectors = np.load(VECTORS).astype(np.float32)
    row_of = {cid: i for i, cid in enumerate(json.loads(VECTOR_IDS.read_text(encoding="utf-8")))}

    results = latest_results()
    ranks_of = {p["question_id"]: p["ranks"] for p in results["per_question"]}
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = [qid for qid, r in ranks_of.items() if all(v is None or v > 10 for v in r.values())]
    print(f"Inspecting: {', '.join(targets)}")

    out = [f"# Missed questions ({datetime.now():%Y-%m-%d %H:%M})\n",
           f"Index: `{ev.INDEX}`. Ranks are document ranks (- = not in the top 100 chunks).\n"]

    for qid in targets:
        q = by_id[qid]
        qvec = qvecs[qid]
        expected = q["expected_doc_ids"]
        ranks = ranks_of.get(qid, {})
        out.append(f"\n---\n\n## {qid}\n\n**Question:** {q['question']}\n")
        out.append(f"**Gold answer:** {q.get('gold_answer', '')}\n")
        out.append("**Ranks:** " + ", ".join(f"{m}: {r if r else '-'}" for m, r in ranks.items()) + "\n")

        # --- The expected document: which chunk holds the answer, and how did each chunk score?
        for doc_id in expected:
            res = es.search(index=ev.INDEX, size=200, sort=[{"position": "asc"}],
                            query={"term": {"doc_id": doc_id}},
                            source_includes=["chunk_id", "title", "section", "body", "text", "position"])
            chunks = [h["_source"] for h in res["hits"]["hits"]]
            if not chunks:
                out.append(f"\n**Expected document {doc_id} is not in the index.**\n")
                continue

            # BM25 score of each of its chunks for this question (same index statistics as the real search)
            scored = es.search(index=ev.INDEX, size=200, source_includes=["chunk_id"],
                               query={"bool": {"must": {"match": {"text": q["question"]}},
                                               "filter": {"term": {"doc_id": doc_id}}}})
            bm25_score = {h["_source"]["chunk_id"]: h["_score"] for h in scored["hits"]["hits"]}

            out.append(f"\n### Expected document: \"{chunks[0]['title']}\" ({doc_id}, {len(chunks)} chunks)\n")
            out.append("| pos | section | BM25 | cosine | answer words |\n|---|---|---|---|---|")
            best = None
            for c in chunks:
                cos = float(chunk_vectors[row_of[c["chunk_id"]]] @ qvec)
                ov = answer_overlap(q.get("gold_answer", ""), c["body"])
                out.append(f"| {c['position']} | {c['section'][:50]} | {bm25_score.get(c['chunk_id'], 0):.1f} "
                           f"| {cos:.3f} | {ov:.0%} |")
                if best is None or ov > best[1]:
                    best = (c, ov)
            c, ov = best
            out.append(f"\n**Chunk most likely holding the answer** (position {c['position']}, "
                       f"{ov:.0%} of the answer's words):\n\n```\n{c['text'][:1500]}\n```\n")

        # --- What each method returned instead
        b = ev.bm25(es, q)
        s = ev.semantic(es, qvec)
        h = ev.rrf(b, s)
        top_score = {}
        out.append("\n### What each method returned instead (top 3 documents)\n")
        for name, ranking in (("BM25", b), ("Semantic", s), ("Hybrid", h)):
            out.append(f"\n**{name}**\n")
            seen = []
            for chunk_id, doc_id in ranking:
                if doc_id in seen:
                    continue
                seen.append(doc_id)
                hit = es.get(index=ev.INDEX, id=chunk_id, source_includes=["title", "section", "body"])["_source"]
                exp_title = chunks[0]["title"] if chunks else ""
                sim = title_similarity(hit["title"], exp_title)
                dup = "  **(similar title: possible near-duplicate)**" if sim > 0.6 else ""
                mark = "  **(expected)**" if doc_id in expected else ""
                out.append(f"{len(seen)}. \"{hit['title']}\" | section: {hit['section'][:50]} "
                           f"| title similarity {sim:.2f}{dup}{mark}\n"
                           f"   > {hit['body'][:300].replace(chr(10), ' ')}\n")
                if len(seen) == 3:
                    break

    path = ev.RESULTS_DIR / f"misses_{datetime.now():%Y%m%d_%H%M}.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Report written to {path}  (open it in VS Code and press Ctrl+Shift+V for the formatted view)")


if __name__ == "__main__":
    main()