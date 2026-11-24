# Local LLM Inference Study

![tests](https://github.com/deepanjali-thota/local-llm-inference-study/actions/workflows/tests.yml/badge.svg)

Running open-source LLMs locally on a CPU-only laptop with Ollama: measuring speed, enforcing structured output, and choosing a model with data.

**Hardware:** Intel i5-1335U, 16 GB RAM, no GPU · **Models:** llama3.2:3b, phi4-mini, mistral:7b (Q4_K_M)

## Key results

| Model | Accuracy (40 tickets) | Accuracy (held-out 16) | Latency | Gen tok/s | RAM |
|---|---|---|---|---|---|
| llama3.2:3b | 95% | 69% | 2.3s | 13.8 | 4.1 GB |
| phi4-mini | 98% | 88% | 3.1s | 11.7 | 4.8 GB |
| mistral:7b | 95% | 88% | 6.6s | 5.9 | 6.8 GB |


![Accuracy vs latency](tradeoff.png)

## What I found

- **Prompt beat model size:** adding category definitions raised accuracy +15–18 points; moving 3B → 7B gave +8.
- **Held-out testing exposed overfitting:** llama3.2:3b dropped from 95% to 69% on unseen tickets. Error analysis showed part of the drop was a labeling-policy mismatch, not just model error.
- **Format ≠ correctness:** schema-constrained decoding took valid JSON from 0/5 to 5/5, but answers could still be wrong.
- **Prevention beat retry:** stating a rule in the prompt fixed 100% of violations; feedback retries fixed 0/2 and sometimes broke correct fields.
- **Temperature 0 ≠ identical output:** prompt-cache numerics changed near-tied words between runs.
- **Quantization:** Q8 was ~1.6x slower than Q4 with no accuracy gain.
- **Cold start:** ~12x slower than warm (4.2s vs 0.36s TTFT).
- **Windows `localhost` bug:** IPv6 fallback added ~2s to every request; `127.0.0.1` fixed it.

## Project phases

1. **Inference benchmarks** → [BENCHMARKS.md](BENCHMARKS.md): TTFT, tokens/sec, cold vs warm start
2. **Structured output** → [STRUCTURED_OUTPUT.md](STRUCTURED_OUTPUT.md): JSON schema, Pydantic validation, retry, temperature study
3. **Model comparison** → [MODEL_COMPARISON.md](MODEL_COMPARISON.md): 3 models, held-out test, quantization

## Run it

```bash
pip install -r requirements.txt
ollama pull llama3.2:3b
uvicorn app:app --reload        # API at http://127.0.0.1:8000/docs
python compare_models.py        # model comparison
```

**API endpoints:** `GET /health` · `POST /generate` (free text) · `POST /classify` (validated JSON ticket triage with retry)