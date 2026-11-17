import json
import time
import requests

start = time.perf_counter()
first_token_time = None

with requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "llama3.2:3b",
        "prompt": "Explain what a REST API is in 3 sentences.",
        "stream": True,
    },
    stream=True,
) as r:
    for line in r.iter_lines():
        if not line:
            continue
        chunk = json.loads(line)

        if first_token_time is None and chunk.get("response"):
            first_token_time = time.perf_counter()

        print(chunk.get("response", ""), end="", flush=True)

end = time.perf_counter()

print()
print(f"TTFT: {first_token_time - start:.2f}s")
print(f"Total: {end - start:.2f}s")