"""
Structure-aware chunking of EnterpriseRAG-Bench Google Drive documents.

Run from the project root:
    python benchmarks/enterprise_rag/chunk_drive.py

Writes (all inside data/, which git ignores):
    data/eval/drive_questions.jsonl              questions answered only by Drive documents
    data/chunks/drive_structure_v1.jsonl         one chunk per line, ready to embed and index
    data/chunks/drive_structure_v1_preview.txt   the chunks of 10 documents, to check by eye
"""
import json
import random
import re
import statistics
from pathlib import Path

# ---------------- Settings ----------------
REPO = "onyx-dot-app/EnterpriseRAG-Bench"
CACHE = "data/hf_cache"
DOCS = "C:/Users/micha/.cache/huggingface/hub/datasets--onyx-dot-app--EnterpriseRAG-Bench/snapshots/69916e31c68aa5963c00248fd7f0bc12d04fd235/data/documents/test.parquet"
DRIVE = "google_drive"

SUBSET_SIZE = 5000   # documents to chunk (all answer documents + random others)
SEED = 42            # same seed -> same subset every run
MAX_TOKENS = 500     # hard upper limit per chunk, header included
TARGET_TOKENS = 400  # consecutive small sections are packed together up to this size
MIN_TOKENS = 60      # smaller sections are merged into the next one
STRATEGY = "structure_v1"

OUT_CHUNKS = Path("data/chunks/drive_structure_v1.jsonl")
OUT_PREVIEW = Path("data/chunks/drive_structure_v1_preview.txt")
OUT_QUESTIONS = Path("data/eval/drive_questions.jsonl")

# ---------------- Token counting (BGE-M3's own tokenizer) ----------------
_tokenizer = None


def count_tokens(text: str) -> int:
    global _tokenizer
    if _tokenizer is None:
        from tokenizers import Tokenizer
        _tokenizer = Tokenizer.from_pretrained("BAAI/bge-m3")
    return len(_tokenizer.encode(text, add_special_tokens=False).ids)


# ---------------- Chunking rules ----------------
LIST_ITEM = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def is_heading(line: str) -> bool:
    """A short line of its own, not a list item, not ending like a sentence."""
    s = line.strip()
    if not re.search(r"\w", s):   # dividers like --- or *** are not headings
        return False
    if not s or len(s) > 80 or len(s.split()) > 8:
        return False
    if LIST_ITEM.match(s) or s.endswith((".", ",", ";")):
        return False
    return True


def split_sections(content: str) -> list[dict]:
    """Blocks are separated by blank lines; a block whose first line is a heading starts a section."""
    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", content)
              if b.strip() and re.search(r"\w", b)]   # drop divider-only blocks
    sections = []
    current = {"heading": "Introduction", "blocks": []}
    for block in blocks:
        first, _, rest = block.partition("\n")
        if is_heading(first):
            heading = first.strip().rstrip(":").strip()
            if current["blocks"]:
                sections.append(current)
            elif current["heading"] != "Introduction":
                # heading directly followed by another heading: treat as parent / child
                heading = f"{current['heading']} / {heading}"
            current = {"heading": heading, "blocks": []}
            if rest.strip():
                current["blocks"].append(rest)
        else:
            current["blocks"].append(block)
    if current["blocks"]:
        sections.append(current)
    return sections


def blocks_with_heading(section: dict) -> list[tuple[str, str]]:
    """(heading, block) pairs, with each heading line put back in front of its first block."""
    pairs = []
    for heading, blocks in section["parts"]:
        for i, block in enumerate(blocks):
            if i == 0 and heading != "Introduction":
                block = f"{heading}\n{block}"
            pairs.append((heading, block))
    return pairs


def make_label(headings: list[str]) -> str:
    """'A / B / C', or 'A / … / F' when more than three headings are in one chunk."""
    headings = list(dict.fromkeys(headings))  # unique, in order
    if len(headings) > 3:
        headings = [headings[0], "…", headings[-1]]
    return " / ".join(headings)


def combine(a: dict, b: dict) -> dict:
    """Join two sections; each keeps its own heading."""
    return {"parts": a["parts"] + b["parts"]}


def section_tokens(section: dict) -> int:
    return count_tokens("\n\n".join(b for _, b in blocks_with_heading(section)))


def merge_small(sections: list[dict]) -> list[dict]:
    """Sections under MIN_TOKENS are merged into the next section (the last one into the previous)."""
    sections = [{"parts": [(s["heading"], s["blocks"])]} for s in sections]
    merged, pending = [], None
    for s in sections:
        if pending is not None:
            s, pending = combine(pending, s), None
        if section_tokens(s) < MIN_TOKENS:
            pending = s
        else:
            merged.append(s)
    if pending is not None:
        if merged:
            merged[-1] = combine(merged[-1], pending)
        else:
            merged.append(pending)
    return merged


def split_block(block: str) -> list[str]:
    """Split a block into list items. Sub-items stay with their parent; a lead-in line stays with the first item."""
    units, current = [], []
    for line in block.split("\n"):
        top_item = bool(LIST_ITEM.match(line)) and not line[:1].isspace()
        lead_in_only = len(current) == 1 and not LIST_ITEM.match(current[0])
        if top_item and current and not lead_in_only:
            units.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        units.append("\n".join(current))
    return units


def _greedy(pieces: list[str], joiner: str, budget: int, prefix: str = "") -> list[str]:
    """Join pieces up to the budget; any piece still too long is split further."""
    parts, current = [], ""
    for piece in pieces:
        candidate = f"{current}{joiner}{piece}" if current else prefix + piece
        if count_tokens(candidate) <= budget:
            current = candidate
            continue
        if current:
            parts.append(current)
        if count_tokens(prefix + piece) <= budget:
            current = prefix + piece
        else:
            parts.extend(split_long(piece, budget - count_tokens(prefix)))
            current = ""
    if current:
        parts.append(current)
    return parts


def split_long(text: str, budget: int) -> list[str]:
    """Split text that is over budget: at line breaks, then sentences, then words.
    Tables (lines starting with '|') repeat their header rows on every piece."""
    if count_tokens(text) <= budget:
        return [text]

    lines = [l for l in text.split("\n") if l.strip()]
    if len(lines) > 1:
        table = sum(l.lstrip().startswith("|") for l in lines) > len(lines) / 2
        if table and len(lines) > 3:
            header = "\n".join(lines[:2]) + "\n"
            return _greedy(lines[2:], "\n", budget, prefix=header)
        return _greedy(lines, "\n", budget)

    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) > 1:
        return _greedy(sentences, " ", budget)

    words = text.split()
    if len(words) > 1:
        return _greedy(words, " ", budget)

    # A single enormous "word" (a hash, URL or encoded blob): cut it into slices.
    size = max(50, len(text) * budget // max(1, count_tokens(text)))
    return [text[i:i + size] for i in range(0, len(text), size)]


def pack(section: dict, budget: int) -> list[tuple[str, str]]:
    """Fill chunks of balanced size, never over budget, never splitting inside a list item or sentence.
    Returns (label, text) pairs; the label names only the headings that appear in that chunk."""
    units = []  # (text, starts_new_block, heading)
    for heading, block in blocks_with_heading(section):
        for i, unit in enumerate(split_block(block)):
            for j, piece in enumerate(split_long(unit, budget)):
                units.append((piece, i == 0 and j == 0, heading))

    # Aim for equal-sized chunks: 520 tokens -> two of ~260, not 500 + 20.
    sizes = [count_tokens(u[0]) for u in units]
    n_chunks = max(1, -(-sum(sizes) // budget))  # ceiling division
    target = sum(sizes) / n_chunks

    chunks, current, current_tokens = [], [], 0
    for unit, tokens in zip(units, sizes):
        over_budget = current_tokens + tokens > budget
        past_target = current_tokens + tokens / 2 > target  # most of this unit would land past the target
        if current and (over_budget or past_target):
            chunks.append(current)
            current, current_tokens = [], 0
        current.append(unit)
        current_tokens += tokens
    if current:
        chunks.append(current)

    out = []
    for chunk in chunks:
        text = chunk[0][0]
        for piece, new_block, _ in chunk[1:]:
            text += ("\n\n" if new_block else "\n") + piece
        out.append((make_label([h for _, _, h in chunk]), text))
    return out


def readable_title(title: str) -> str:
    """'routing-and-controlplane-runbook' -> 'Routing and controlplane runbook'."""
    t = (title or "").strip()
    if t and " " not in t and re.search(r"[-_]", t):
        t = re.sub(r"[-_]+", " ", t).strip()
        t = t[:1].upper() + t[1:]
    return t or "Untitled"


def header_tokens(nice_title: str, section: dict) -> int:
    """Tokens of the longest header any chunk of this section could get.
    A label holds at most three headings, so reserve room for the three longest."""
    longest = sorted({h for h, _ in section["parts"]}, key=len, reverse=True)[:3]
    return count_tokens(f"Document: {nice_title} | Section: {' / '.join(longest)}") + 2


def group_sections(sections: list[dict], nice_title: str) -> list[dict]:
    """Pack consecutive sections together while the result stays under TARGET_TOKENS.
    Chunks still break only at section boundaries (unless one section alone is too big)."""
    groups, current = [], None
    for s in sections:
        if current is not None:
            candidate = combine(current, s)
            if section_tokens(candidate) + header_tokens(nice_title, candidate) <= TARGET_TOKENS:
                current = candidate
                continue
            groups.append(current)
        current = s
    if current is not None:
        groups.append(current)
    return groups


def chunk_document(doc_id: str, title: str, content: str) -> list[dict]:
    nice_title = readable_title(title)
    records = []
    sections = group_sections(merge_small(split_sections(content or "")), nice_title)
    for section in sections:
        # Reserve room for the longest possible header of this section.
        budget = MAX_TOKENS - header_tokens(nice_title, section)
        for label, body in pack(section, budget):
            text = f"Document: {nice_title} | Section: {label}\n\n{body}"
            records.append({
                "chunk_id": f"{doc_id}::{len(records):03d}",
                "doc_id": doc_id,
                "title": title,
                "section": label,
                "position": len(records),
                "source": DRIVE,
                "strategy": STRATEGY,
                "n_tokens": count_tokens(text),
                "text": text,   # what gets embedded and BM25-indexed
                "body": body,   # what the answer generator will see
            })
    return records


# ---------------- Main ----------------
def main():
    import duckdb
    import pandas as pd
    from datasets import load_dataset

    random.seed(SEED)
    con = duckdb.connect()
    con.execute("SET memory_limit='2GB'")

    # 1. Questions whose expected documents are all Drive documents
    drive_ids = {r[0] for r in con.execute(
        f"SELECT doc_id FROM read_parquet('{DOCS}') WHERE source_type = ?", [DRIVE]).fetchall()}
    qs = load_dataset(REPO, "questions", cache_dir=CACHE)["test"].to_pandas()
    qs["expected"] = qs["expected_doc_ids"].apply(list)
    eval_qs = qs[qs["expected"].apply(lambda ids: len(ids) > 0 and all(i in drive_ids for i in ids))]

    OUT_QUESTIONS.parent.mkdir(parents=True, exist_ok=True)
    with OUT_QUESTIONS.open("w", encoding="utf-8") as f:
        for _, q in eval_qs.iterrows():
            f.write(json.dumps({
                "question_id": q["question_id"],
                "question": q["question"],
                "question_type": q["question_type"],
                "expected_doc_ids": q["expected"],
                "gold_answer": q["gold_answer"],
            }, ensure_ascii=False) + "\n")

    # 2. Subset: every answer document + random other Drive documents
    gold = sorted({i for ids in eval_qs["expected"] for i in ids})
    others = sorted(drive_ids - set(gold))
    sample = gold + random.sample(others, max(0, SUBSET_SIZE - len(gold)))
    con.register("wanted", pd.DataFrame({"doc_id": sample}))
    rows = con.execute(f"""
        SELECT d.doc_id, d.title, d.content
        FROM read_parquet('{DOCS}') d JOIN wanted USING (doc_id)
        WHERE d.source_type = ?
    """, [DRIVE]).fetchall()
    order = {doc_id: i for i, doc_id in enumerate(sample)}
    rows.sort(key=lambda r: order[r[0]])  # answer documents first, so the preview shows them

    # 3. Chunk
    from collections import Counter
    OUT_CHUNKS.parent.mkdir(parents=True, exist_ok=True)
    all_chunks, per_doc = [], []
    heading_counts = Counter()
    with OUT_CHUNKS.open("w", encoding="utf-8") as f, OUT_PREVIEW.open("w", encoding="utf-8") as preview:
        for n, (doc_id, title, content) in enumerate(rows, 1):
            heading_counts.update(s["heading"] for s in split_sections(content or ""))
            chunks = chunk_document(doc_id, title, content)
            per_doc.append(len(chunks))
            all_chunks.extend(c["n_tokens"] for c in chunks)
            for c in chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
            if n <= 10:
                preview.write("#" * 100 + f"\nDOC {doc_id}  ({len(chunks)} chunks)\n")
                for c in chunks:
                    preview.write("-" * 100 + f"\n[{c['chunk_id']}  {c['n_tokens']} tokens]\n{c['text']}\n")
            if n % 500 == 0:
                print(f"  chunked {n}/{len(rows)} documents")

    # 4. Summary
    print(f"\nEvaluation questions (answers only in Drive): {len(eval_qs)}  ->  {OUT_QUESTIONS}")
    print(f"Answer documents: {len(gold)}   Documents chunked: {len(rows)}")
    print(f"Chunks: {len(all_chunks)}   per document: avg {statistics.mean(per_doc):.1f}, max {max(per_doc)}")
    print(f"Tokens per chunk: min {min(all_chunks)}, median {statistics.median(all_chunks):.0f}, max {max(all_chunks)}")
    print(f"Chunks over {MAX_TOKENS} tokens: {sum(t > MAX_TOKENS for t in all_chunks)}")
    print(f"Chunks under {MIN_TOKENS} tokens: {sum(t < MIN_TOKENS for t in all_chunks)}")

    # Heading check: common ones should look like real headings; the random ones show false positives.
    print(f"\nDetected headings: {sum(heading_counts.values())} ({sum(heading_counts.values()) / len(rows):.1f} per document)")
    print("Most common:")
    for h, n in heading_counts.most_common(15):
        print(f"  {n:6d}  {h}")
    rare = [h for h, n in heading_counts.items() if n == 1]
    print("Random rare ones (check these for false headings):")
    for h in random.sample(rare, min(15, len(rare))):
        print(f"          {h}")

    print(f"\nWrote {OUT_CHUNKS}\nCheck by eye: {OUT_PREVIEW}")


if __name__ == "__main__":
    main()