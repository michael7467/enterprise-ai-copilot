"""
Break the latest retrieval results down by question type. Reads the saved results file only:
no Elasticsearch or model needed.

Run from the project root:
    python eval/retrieval/by_question_type.py                         # latest results file
    python eval/retrieval/by_question_type.py eval/results/<file>.json

Metrics use the rank of the first expected document:
    hit@k  share of questions with an expected document in the top k documents
    MRR    mean of 1 / that rank (0 if not found)
For questions with one expected document, hit@k equals recall@k.
"""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path("eval/results")
KS = (1, 5, 10)


def load(path_arg: str | None) -> tuple[Path, dict]:
    if path_arg:
        path = Path(path_arg)
    else:
        files = sorted(RESULTS_DIR.glob("drive_retrieval_*.json"))
        if not files:
            raise SystemExit("No results file found. Run eval_drive_retrieval.py first.")
        path = files[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def summarize(ranks: list) -> dict:
    out = {f"hit@{k}": statistics.mean(1.0 if r and r <= k else 0.0 for r in ranks) for k in KS}
    out["MRR"] = statistics.mean(1 / r if r else 0.0 for r in ranks)
    return out


def main():
    path, results = load(sys.argv[1] if len(sys.argv) > 1 else None)
    per_q = results["per_question"]
    methods = list(per_q[0]["ranks"].keys())

    groups = defaultdict(list)
    for p in per_q:
        groups[p.get("question_type") or "unknown"].append(p)
    multi = sum(len(p["expected_doc_ids"]) > 1 for p in per_q)

    lines = [f"# Retrieval by question type\n",
             f"Source: `{path.name}`. {results['corpus']}. {len(per_q)} questions"
             f"{f' ({multi} with more than one expected document)' if multi else ''}.\n"]
    header = "| Question type | n | Method | " + " | ".join(f"hit@{k}" for k in KS) + " | MRR |"
    lines += [header, "|" + "---|" * (header.count("|") - 1)]

    for qtype in sorted(groups, key=lambda t: -len(groups[t])):
        qs = groups[qtype]
        for i, m in enumerate(methods):
            s = summarize([p["ranks"][m] for p in qs])
            label = f"{qtype} | {len(qs)}" if i == 0 else " | "
            lines.append(f"| {label} | {m} | " + " | ".join(f"{s[f'hit@{k}']:.0%}" for k in KS)
                         + f" | {s['MRR']:.2f} |")

    lines.append("\n## Questions not in the hybrid top 10, by type\n")
    hybrid = methods[-1]
    for qtype, qs in sorted(groups.items()):
        missed = [p for p in qs if not p["ranks"][hybrid] or p["ranks"][hybrid] > 10]
        if missed:
            lines.append(f"**{qtype}** ({len(missed)} of {len(qs)}): "
                         + ", ".join(f"{p['question_id']} (rank {p['ranks'][hybrid] or '-'})" for p in missed))

    lines.append(f"\nSmall groups are unreliable: with n = 5, one question moves a score by 20 points.")
    report = "\n".join(lines)
    print(report)

    out = RESULTS_DIR / path.name.replace("drive_retrieval_", "by_type_").replace(".json", ".md")
    out.write_text(report, encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()