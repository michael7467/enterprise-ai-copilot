
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG = PROJECT_ROOT / "logs" / "requests.jsonl"


def load(path: Path, since: str | None) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue  # a half-written line must not stop the report
        if since is None or r.get("time", "") >= since:
            records.append(r)
    return records


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    k = (len(values) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def seconds(ms: float) -> str:
    return f"{ms / 1000:.1f} s"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG)
    ap.add_argument("--since", help="only requests on or after this date, e.g. 2026-11-08")
    args = ap.parse_args()

    if not args.log.exists():
        raise SystemExit(f"No log yet at {args.log}. Ask a question in the chat first.")
    records = load(args.log, args.since)
    if not records:
        raise SystemExit("No requests in the selected period.")

    ok = [r for r in records if r.get("status") == "ok"]
    failed = [r for r in records if r.get("status") != "ok"]
    print(f"Requests: {len(records)}   ok: {len(ok)}   failed: {len(failed)} "
          f"({len(failed) / len(records):.0%})")
    print(f"Period: {records[0].get('time')}  to  {records[-1].get('time')}")
    models = sorted({r.get("model", "?") for r in records})
    print(f"Models: {', '.join(models)}\n")

    # Latency per route (successful requests only)
    by_route = defaultdict(list)
    for r in ok:
        by_route[r.get("route", "?")].append(r.get("latency_ms", 0))
    print(f"{'Route':<16}{'n':>4}{'median':>10}{'p95':>10}{'max':>10}")
    for route, ms in sorted(by_route.items()):
        print(f"{route:<16}{len(ms):>4}{seconds(statistics.median(ms)):>10}"
              f"{seconds(percentile(ms, 95)):>10}{seconds(max(ms)):>10}")

    # Answer behaviour
    answered = [r for r in ok if r.get("route") in ("knowledge_base", "uploaded_file")]
    if answered:
        abstained = sum(1 for r in answered if r.get("abstained") or r.get("confidence") == "abstained")
        no_citation = sum(1 for r in answered if not r.get("cited") and not r.get("abstained"))
        print(f"\nDocument questions: {len(answered)}")
        print(f"  abstained ('could not find'): {abstained} ({abstained / len(answered):.0%})")
        print(f"  answered without any citation: {no_citation} ({no_citation / len(answered):.0%})")

    # Failures, grouped by type
    if failed:
        print("\nFailures:")
        kinds = defaultdict(int)
        for r in failed:
            err = r.get("error", "")
            kind = "out of memory" if "alloc" in err or "memory" in err else err[:60]
            kinds[(r.get("status"), kind)] += 1
        for (status, kind), n in sorted(kinds.items(), key=lambda x: -x[1]):
            print(f"  {n:>3} x {status}: {kind}")


if __name__ == "__main__":
    main()