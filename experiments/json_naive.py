import json
import requests

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"

TICKET = "I was charged twice for my subscription this month and I need a refund ASAP!"

PROMPT = f"""Classify this support ticket. Return JSON with fields:
category (one of: billing, technical, account, other),
priority (one of: low, medium, high),
summary (one short sentence).

Ticket: {TICKET}"""

ok = 0
for i in range(5):
    r = requests.post(URL, json={
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False,
        "options": {"temperature": 0.7},
    })
    text = r.json()["response"]
    print(f"--- Run {i+1} ---")
    print(text)
    try:
        json.loads(text)
        ok += 1
        print(">> VALID JSON")
    except json.JSONDecodeError:
        print(">> FAILED TO PARSE")

print(f"\n{ok}/5 parsed as valid JSON")