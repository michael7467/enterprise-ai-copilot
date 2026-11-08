from app.generation import llm


def test_ollama_nanoseconds_become_milliseconds():
    stats = llm._stats({"load_duration": 2_000_000_000, "prompt_eval_duration": 50_000_000_000,
                        "eval_duration": 15_000_000_000, "prompt_eval_count": 2100, "eval_count": 90})
    assert stats == {"llm_load_ms": 2000, "llm_prompt_ms": 50000, "llm_generate_ms": 15000,
                     "prompt_tokens": 2100, "output_tokens": 90}