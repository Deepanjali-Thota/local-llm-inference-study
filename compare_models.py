import csv
import json
import statistics
import time
import sys
import requests
from pydantic import ValidationError

from app import Ticket, build_prompt

GEN_URL = "http://127.0.0.1:11434/api/generate"
PS_URL = "http://127.0.0.1:11434/api/ps"
MODELS = ["llama3.2:3b", "phi4-mini", "mistral:7b"]
if len(sys.argv) > 2:
    MODELS = sys.argv[2].split(",")
NS = 1_000_000_000



TICKETS_FILE = sys.argv[1] if len(sys.argv) > 1 else "data/tickets.json"
with open(TICKETS_FILE, encoding="utf-8") as f:
    TICKETS = json.load(f)


def unload(model):
    requests.post(GEN_URL, json={"model": model, "keep_alive": 0})


def ram_gb(model):
    for m in requests.get(PS_URL).json()["models"]:
        if m["name"].startswith(model):
            return m["size"] / 1e9
    return 0.0


def classify(model, text):
    start = time.perf_counter()
    data = requests.post(GEN_URL, json={
        "model": model,
        "prompt": build_prompt(text),
        "stream": False,
        "format": Ticket.model_json_schema(),
        "options": {"temperature": 0},
    }, timeout=300).json()
    latency = time.perf_counter() - start

    raw = data["response"]
    try:
        category = Ticket.model_validate_json(raw).category
        valid = True
    except ValidationError:
        valid = False
        try:
            category = json.loads(raw).get("category")
        except json.JSONDecodeError:
            category = None

    return {
        "category": category,
        "valid": valid,
        "latency": latency,
        "gen_tps": data["eval_count"] / (data["eval_duration"] / NS),
    }


all_rows = []
summary = []

for model in MODELS:
    for m in MODELS:
        unload(m)
    time.sleep(2)

    print(f"\n===== {model} =====")
    classify(model, "Warm-up ticket: hello")  # load model, not measured
    ram = ram_gb(model)

    rows = []
    for i, t in enumerate(TICKETS):
        r = classify(model, t["text"])
        r.update({
            "model": model,
            "ticket": i + 1,
            "expected": t["category"],
            "hard": t["hard"],
            "correct": r["category"] == t["category"],
        })
        rows.append(r)
        mark = "OK " if r["correct"] else "XX "
        print(f"{mark} #{i+1:2} expected {t['category']:9} got {str(r['category']):9} "
              f"{r['latency']:.1f}s {'' if r['valid'] else '(invalid)'}")

    hard = [r for r in rows if r["hard"]]
    summary.append({
        "model": model,
        "accuracy": sum(r["correct"] for r in rows) / len(rows),
        "hard_accuracy": sum(r["correct"] for r in hard) / len(hard),
        "valid_rate": sum(r["valid"] for r in rows) / len(rows),
        "median_latency": statistics.median(r["latency"] for r in rows),
        "median_tps": statistics.median(r["gen_tps"] for r in rows),
        "ram_gb": ram,
    })
    all_rows.extend(rows)

print("\n\n| Model | Accuracy | Hard acc. | Valid | Latency (s) | Gen tok/s | RAM (GB) |")
print("|---|---|---|---|---|---|---|")
for s in summary:
    print(f"| {s['model']} | {s['accuracy']:.0%} | {s['hard_accuracy']:.0%} | "
          f"{s['valid_rate']:.0%} | {s['median_latency']:.2f} | "
          f"{s['median_tps']:.1f} | {s['ram_gb']:.1f} |")

with open("results/comparison_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
    writer.writeheader()
    writer.writerows(all_rows)

print("\nSaved comparison_results.csv")