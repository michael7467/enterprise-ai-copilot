"""All settings in one place. Override any of them in backend/.env (see .env.example)."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Elasticsearch (the index built by benchmarks/enterprise_rag/index_chunks.py)
    es_url: str = "http://localhost:9200"
    es_index: str = "drive_chunks_structure_v1"
    uploads_index: str = "uploaded_documents"   # one index for all uploads, filtered by file_id

    # Retrieval: the evaluated setup (hybrid BM25 + BGE-M3, RRF), reranker optional
    semantic_enabled: bool = True  # false = "light mode": BM25 only, BGE-M3 never loaded (saves ~2.5 GB)
    embed_model: str = "BAAI/bge-m3"
    top_chunks: int = 100        # per search method, before fusion
    num_candidates: int = 500    # kNN search breadth
    rrf_k: int = 60
    top_k: int = 4               # chunks given to the language model

    # Reranker + confidence gate: off by default (about 30 s per question on a laptop CPU)
    rerank_enabled: bool = False
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    rerank_depth: int = 10       # best depth from the evaluation
    gate_threshold: float = 0.6  # below: abstain without calling the LLM
    low_confidence: float = 0.85 # below: answer, but flag as low confidence

    # Language model (Ollama)
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen3:8b"
    llm_num_ctx: int = 6144
    llm_max_tokens: int = 300
    llm_timeout_s: int = 600

    # Uploads
    upload_dir: Path = PROJECT_ROOT / "data" / "uploads"
    max_upload_mb: int = 20

    # Frontend origins allowed to call the API
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]


settings = Settings()
