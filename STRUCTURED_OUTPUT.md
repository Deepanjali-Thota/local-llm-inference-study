# Structured Output

Task: support ticket triage → {category, priority, summary}
Model: llama3.2:3b, temperature 0.7, 5 runs on the same ticket

| Approach | Parseable JSON | Correct category |
|---|---|---|
| Prompt-only ("Return JSON...") | 0/5 | n/a |
| Ollama `format` + Pydantic schema | 5/5 | 4/5 |

## Observations
- Prompt-only: the model reasoned correctly every time but wrapped the JSON in preamble, code fences and explanations, so `json.loads` failed 100% of the time.
- Constrained decoding fixed format completely (5/5) but not correctness: 1 run returned `account` for a double-charge ticket. Format validity ≠ answer correctness.