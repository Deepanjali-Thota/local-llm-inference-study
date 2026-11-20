# Model Comparison

Hardware: Intel i5-1335U, 16 GB RAM, CPU only. All models Q4_K_M, temperature 0.
Task: support ticket classification, 40 manually labeled tickets (10 per category, 9 marked hard).

## Run 1: category names only in prompt

| Model | Params | Accuracy | Hard acc. | Valid | Latency (s) | Gen tok/s | RAM (GB) |
|---|---|---|---|---|---|---|---|
| llama3.2:3b | 3.2B | 80% | 78% | 100% | 2.28 | 13.9 | 4.1 |
| phi4-mini | 3.8B | 80% | 78% | 92% | 2.82 | 11.7 | 4.8 |
| mistral:7b | 7.2B | 88% | 56% | 85% | 6.43 | 6.4 | 6.8 |

## Run 2: category definitions added to prompt

| Model | Params | Accuracy | Hard acc. | Valid | Latency (s) | Gen tok/s | RAM (GB) |
|---|---|---|---|---|---|---|---|
| llama3.2:3b | 3.2B | 95% | 89% | 100% | 2.32 | 13.8 | 4.1 |
| phi4-mini | 3.8B | 98% | 100% | 95% | 3.07 | 11.7 | 4.8 |
| mistral:7b | 7.2B | 95% | 89% | 80% | 6.56 | 5.9 | 6.8 |

## Findings
- Category definitions improved accuracy by +15 to +18 points for the small models. Moving from 3B to 7B gave only +8 in Run 1. Prompt design mattered more than model size.
- In Run 1, llama3.2:3b and phi4-mini made the same errors (receipt, student discount, and most "other" tickets → account). Shared errors across models pointed to the prompt, not the model.
- In Run 1, mistral:7b was 97% accurate on easy tickets but worst on hard ones (5/9); its errors were mostly defensible (feature requests → technical).
- mistral:7b had the lowest valid rate (80–85%): it wrote summaries over 6 words most often, which would trigger retries in production.
- mistral:7b is ~2.8x slower and uses ~65% more RAM than llama3.2:3b, with no accuracy gain after the prompt fix.

## Limitations
- 40 tickets: a 1-ticket difference is 2.5 points, so 95% vs 98% is not a meaningful gap. Hard accuracy uses only 9 tickets.
- Definitions were written after seeing Run 1 errors on the same tickets, so Run 2 may overfit. Needs a held-out test set.
- Labels are one person's judgment; hard tickets are genuinely ambiguous.
- Run 1 per-ticket CSV was reconstructed from the console log (no per-ticket gen tok/s; latency rounded to 0.1s).