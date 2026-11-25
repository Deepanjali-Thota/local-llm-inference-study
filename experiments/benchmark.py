import csv
import json
import statistics
import time
import requests

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"
RUNS = 3
NS = 1_000_000_000

PROMPTS = [
    "Explain what a REST API is in 3 sentences.",
    "Write a Python function that reverses a string.",
    "What are the pros and cons of microservices?",
    "Summarize the causes of World War 1 in one paragraph.",
    "Give 5 tips for writing clean code.",
]


def run_once(prompt):
    start = time.perf_counter()
    first_token_time = None
    final = None

    with requests.post(
        URL,
        json={"model": MODEL, "prompt": prompt, "stream": True},
        stream=True,
    ) as r:
        for line in r.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            if first_token_time is None and chunk.get("response"):
                first_token_time = time.perf_counter()
            if chunk.get("done"):
                final = chunk

    end = time.perf_counter()

    return {
        "ttft": first_token_time - start,
        "total": end - start,
        "tokens": final["eval_count"],
        "gen_tps": final["eval_count"] / (final["eval_duration"] / NS),
    }


print("Warm-up run...")
run_once("Hello")

results = []
for prompt in PROMPTS:
    for i in range(RUNS):
        r = run_once(prompt)
        r["prompt"] = prompt
        r["run"] = i + 1
        results.append(r)
        print(f"{prompt[:30]:30} run {i+1}: TTFT {r['ttft']:.2f}s, {r['gen_tps']:.1f} tok/s, {r['tokens']} tokens")

print()
print(f"Model: {MODEL}")
first_runs = [r for r in results if r["run"] == 1]
repeat_runs = [r for r in results if r["run"] > 1]
print(f"Median TTFT (new prompt):    {statistics.median(r['ttft'] for r in first_runs):.2f}s")
print(f"Median TTFT (cached prompt): {statistics.median(r['ttft'] for r in repeat_runs):.2f}s")
print(f"Median gen tok/s: {statistics.median(r['gen_tps'] for r in results):.1f}")


with open("results/results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["prompt", "run", "ttft", "total", "tokens", "gen_tps"])
    writer.writeheader()
    writer.writerows(results)

print("Saved results/results.csv")