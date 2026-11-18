# Structured Output

Task: support ticket triage → {category, priority, summary}
Model: llama3.2:3b, temperature 0.7

## Experiment 1: Prompt-only vs schema (same ticket, 5 runs)

| Approach | Parseable JSON | Correct category |
|---|---|---|
| Prompt-only ("Return JSON...") | 0/5 | n/a |
| Ollama `format` + Pydantic schema | 5/5 | 4/5 |

## Experiment 2: Business rule + retry (5 different tickets)

Rule: summary ≤ 6 words (Pydantic `field_validator`, not expressible in the schema).

| Approach | Valid | Retries that recovered | Correct category |
|---|---|---|---|
| Rule in code only, no retry | 3/5 | n/a | n/a |
| Rule in code only + feedback retry | 3/5 | 0/2 | n/a |
| Rule stated in prompt + code | 5/5 (first attempt) | none needed | 3/5 |

## Observations
- Prompt-only: the model reasoned correctly every time but wrapped the JSON in preamble, code fences and explanations, so `json.loads` failed 100% of the time.
- Constrained decoding fixed format completely (5/5) but not correctness: 1 run returned `account` for a double-charge ticket. Format validity ≠ answer correctness.
- Feedback retry (whole answer regenerated) recovered 0/2 failures. Ticket 2: model reordered the same 10 words instead of shortening. Ticket 5: summary unchanged, but a previously correct category (technical → billing) and priority (medium → high) regressed. Regenerating everything to fix one field risks breaking fields that were correct.
- Likely cause: models see tokens, not words, so a 3B model counts words poorly.
- Stating the rule in the prompt ("at most 6 words, no device names or version numbers") gave 5/5 valid on the first attempt with zero retries. Prevention beat retry.
- But only 3/5 categories were correct (password reset → technical, feature request → account). Validation checks format and rules, not correctness.