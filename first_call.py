import requests

response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "llama3.2:3b",
        "prompt": "Explain what a REST API is in 3 sentences.",
        "stream": False,
    },
)

data = response.json()
NS = 1_000_000_000  # nanoseconds in one second

load_s = data["load_duration"] / NS
prompt_s = data["prompt_eval_duration"] / NS
gen_s = data["eval_duration"] / NS
total_s = data["total_duration"] / NS

gen_tps = data["eval_count"] / gen_s
cached = data.get("prompt_eval_cached_count", 0)
new_prompt_tokens = data["prompt_eval_count"] - cached
prompt_tps = new_prompt_tokens / prompt_s

print(data["response"])
print(f"Load: {load_s:.2f}s")
print(f"Prompt: {new_prompt_tokens} new tokens ({cached} cached), {prompt_tps:.1f} tok/s")
print(f"Generated: {data['eval_count']} tokens, {gen_tps:.1f} tok/s")
print(f"Total: {total_s:.2f}s")