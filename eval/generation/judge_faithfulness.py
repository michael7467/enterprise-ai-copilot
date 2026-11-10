
import argparse
import json
import re
import statistics
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

CANDIDATES = Path("data/eval/rerank_candidates.jsonl")
RESULTS_DIR = Path("eval/results")
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
NUM_CTX = 4096
VERDICTS = ("supported", "partial", "unsupported")

JUDGE_PROMPT = """You check whether statements are supported by numbered source documents.

For each numbered statement, give one verdict:
- "supported": the sources state it (a paraphrase is fine).
- "partial": part of it is stated in the sources, part is not.
- "unsupported": the sources do not state it, or contradict it.

Judge only against the sources, never against your own knowledge. Citation numbers like [1] inside a
statement are not evidence: check the content itself.
Reply with JSON only, one verdict per statement, in order: {"verdicts": ["supported", "unsupported"]}"""


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def split_statements(answer: str) -> list[str]:
    """Answers are short: split into list items and sentences."""
    parts = []
    for line in answer.splitlines():
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", line).strip()   # list markers
        if line:
            parts += re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", line)
    return [p.strip() for p in parts if len(re.sub(r"\[\d+\]", "", p).strip()) > 3]


def judge_messages(statements: list[str], source_texts: list[str]) -> list[dict]:
    sources = "\n\n".join(f"[{i}] {t}" for i, t in enumerate(source_texts, 1))
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(statements, 1))
    return [{"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": f"Sources:\n\n{sources}\n\nStatements:\n{numbered}"}]


def call_judge(model: str, messages: list[dict]) -> str:
    body = {"model": model, "messages": messages, "stream": False, "format": "json", "keep_alive": "15m",
            "options": {"temperature": 0, "num_ctx": NUM_CTX, "num_predict": 200}}
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=1800) as resp:
            return json.loads(resp.read().decode("utf-8"))["message"]["content"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Ollama returned an error ({e.code}): {e.read().decode('utf-8', 'replace')[:300]}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Cannot reach Ollama at {OLLAMA_URL}. Is it running? ({e.reason})")


def parse_verdicts(raw: str, n: int) -> list[str] | None:
    try:
        verdicts = json.loads(raw).get("verdicts")
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(verdicts, list) or len(verdicts) != n:
        return None
    verdicts = [str(v).strip().lower() for v in verdicts]
    return verdicts if all(v in VERDICTS for v in verdicts) else None


def faithfulness(verdicts: list[str]) -> float:
    return sum({"supported": 1.0, "partial": 0.5}.get(v, 0.0) for v in verdicts) / len(verdicts)


def summarize(records: list[dict]) -> dict:
    judged = [r for r in records if r.get("verdicts")]
    groups = {"all judged answers": judged,
              "cites an expected document": [r for r in judged if r["cites_expected"]],
              "does NOT cite an expected document": [r for r in judged if not r["cites_expected"]]}
    out = {}
    for name, rs in groups.items():
        if rs:
            out[name] = {"answers": len(rs),
                         "mean_faithfulness": statistics.mean(r["faithfulness"] for r in rs),
                         "fully_faithful": statistics.mean(1.0 if r["faithfulness"] == 1.0 else 0.0 for r in rs)}
    out["skipped_abstentions"] = sum(1 for r in records if r.get("skipped") == "abstained")
    out["judge_errors"] = sum(1 for r in records if r.get("skipped") == "judge_error")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="qwen3_8b_v2", help="generation run name: data/eval/generation_<run>.jsonl")
    ap.add_argument("--judge", default="qwen3:4b-instruct-2507-q4_K_M", help="Ollama model used as the judge")
    ap.add_argument("--limit", type=int, default=None, help="only the first N answers")
    args = ap.parse_args()

    answers = load_jsonl(Path(f"data/eval/generation_{args.run}.jsonl"))
    if not answers:
        raise SystemExit(f"No answers in data/eval/generation_{args.run}.jsonl. Check the --run name.")
    texts = {c["chunk_id"]: c["text"] for item in load_jsonl(CANDIDATES) for c in item["candidates"]}
    if args.limit:
        answers = answers[: args.limit]

    judge_tag = re.sub(r"[^a-z0-9]+", "_", args.judge.lower()).strip("_")
    cache = Path(f"data/eval/faithfulness_{args.run}_{judge_tag}.jsonl")
    done = {r["question_id"]: r for r in load_jsonl(cache)}
    print(f"Answers: {len(answers)} from generation_{args.run}   judge: {args.judge}   "
          f"({sum(a['question_id'] in done for a in answers)} already judged)")

    for n, a in enumerate(answers, 1):
        qid = a["question_id"]
        if qid in done:
            continue
        record = {"question_id": qid, "set": a.get("set"), "judge": args.judge,
                  "cites_expected": a.get("cites_expected", False), "answer": a["answer"]}
        statements = split_statements(a["answer"])
        if a.get("abstained") or not statements:
            record["skipped"] = "abstained"
        else:
            missing = [s["chunk_id"] for s in a["sources"] if s["chunk_id"] not in texts]
            if missing:
                raise SystemExit(f"{qid}: source chunks {missing} not found in {CANDIDATES}")
            messages = judge_messages(statements, [texts[s["chunk_id"]] for s in a["sources"]])
            verdicts = parse_verdicts(call_judge(args.judge, messages), len(statements))
            if verdicts is None:   # one retry: small models sometimes miscount
                verdicts = parse_verdicts(call_judge(args.judge, messages), len(statements))
            if verdicts is None:
                record["skipped"] = "judge_error"
            else:
                record.update(statements=statements, verdicts=verdicts, faithfulness=faithfulness(verdicts))
        cache.parent.mkdir(parents=True, exist_ok=True)
        with cache.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        done[qid] = record
        score = f"{record['faithfulness']:.2f}" if "faithfulness" in record else record["skipped"]
        print(f"  {n}/{len(answers)}  {qid}  faithfulness: {score}")

    records = [done[a["question_id"]] for a in answers if a["question_id"] in done]
    summary = summarize(records)
    print(f"\n{'Group':38s}{'answers':>9s}{'mean':>8s}{'fully faithful':>16s}")
    for name, s in summary.items():
        if isinstance(s, dict):
            print(f"{name:38s}{s['answers']:>9d}{s['mean_faithfulness']:>8.2f}{s['fully_faithful']:>16.0%}")
    print(f"Skipped: {summary['skipped_abstentions']} abstentions, {summary['judge_errors']} judge errors")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"faithfulness_{args.run}_{judge_tag}_{datetime.now():%Y%m%d_%H%M}.json"
    out.write_text(json.dumps({"run_at": datetime.now().isoformat(timespec="seconds"), "generation_run": args.run,
                               "judge": args.judge, "summary": summary, "per_answer": records},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()