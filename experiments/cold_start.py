import json
import statistics
import time
import requests

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"
RUNS = 3
NS = 1_000_000_000


def unload():
    requests.post(URL, json={"model": MODEL, "keep_alive": 0})
    time.sleep(2)  # give Ollama time to free the memory


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

    return {
        "ttft": first_token_time - start,
        "load": final["load_duration"] / NS,
    }


cold, warm = [], []
for i in range(RUNS):
    unload()
    c = run_once("Explain what a REST API is in 3 sentences.")
    w = run_once("Give 5 tips for writing clean code.")
    cold.append(c)
    warm.append(w)
    print(f"Run {i+1}: cold TTFT {c['ttft']:.2f}s (load {c['load']:.2f}s) | warm TTFT {w['ttft']:.2f}s (load {w['load']:.2f}s)")

print()
print(f"Median cold TTFT: {statistics.median(r['ttft'] for r in cold):.2f}s")
print(f"Median cold load: {statistics.median(r['load'] for r in cold):.2f}s")
print(f"Median warm TTFT: {statistics.median(r['ttft'] for r in warm):.2f}s")