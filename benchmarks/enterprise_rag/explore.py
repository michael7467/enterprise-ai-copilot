import duckdb
from datasets import load_dataset

REPO = "onyx-dot-app/EnterpriseRAG-Bench"
CACHE = "data/hf_cache"
DOCS = "C:/Users/micha/.cache/huggingface/hub/datasets--onyx-dot-app--EnterpriseRAG-Bench/snapshots/69916e31c68aa5963c00248fd7f0bc12d04fd235/data/documents/test.parquet"
DRIVE = "google_drive"

con = duckdb.connect()
con.execute("SET memory_limit='2GB'")

# 1. How many documents per source?
print(con.execute(f"""
    SELECT source_type, count(*) AS n
    FROM read_parquet('{DOCS}')
    GROUP BY source_type ORDER BY n DESC
""").df(), "\n")

# 2. What do Drive documents look like?
rows = con.execute(f"""
    SELECT title, content FROM read_parquet('{DOCS}')
    WHERE source_type = ? LIMIT 2
""", [DRIVE]).fetchall()
for title, content in rows:
    print("=" * 80)
    print("TITLE:", title)
    print(content[:1500])

# 3. How long are they?
print("\nDrive content length (characters):")
print(con.execute(f"""
    SELECT count(*) AS docs,
           avg(length(content))::INT AS avg_chars,
           median(length(content))::INT AS median_chars,
           max(length(content)) AS max_chars
    FROM read_parquet('{DOCS}') WHERE source_type = ?
""", [DRIVE]).df())

# 4. Which questions are answered by Drive documents? (small file, loads normally)
qs = load_dataset(REPO, "questions", cache_dir=CACHE)["test"].to_pandas()
drive_qs = qs[qs["source_types"].apply(lambda s: DRIVE in list(s))]
print(f"\nQuestions involving Drive: {len(drive_qs)} of {len(qs)}")
print(drive_qs[["question", "expected_doc_ids"]].head(3).to_string())