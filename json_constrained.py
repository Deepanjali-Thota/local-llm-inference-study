import json
from typing import Literal

import requests
from pydantic import BaseModel, ValidationError

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"


class Ticket(BaseModel):
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str


TICKET = "I was charged twice for my subscription this month and I need a refund ASAP!"

PROMPT = f"""Classify this support ticket.
category: billing, technical, account, or other.
priority: low, medium, or high.
summary: one short sentence.

Ticket: {TICKET}"""

print("Schema sent to Ollama:")
print(json.dumps(Ticket.model_json_schema(), indent=2))

ok = 0
for i in range(5):
    r = requests.post(URL, json={
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False,
        "format": Ticket.model_json_schema(),
        "options": {"temperature": 0.7},
    })
    text = r.json()["response"]
    print(f"--- Run {i+1} ---")
    print(text)
    try:
        ticket = Ticket.model_validate_json(text)
        ok += 1
        print(f">> VALID: {ticket.category} / {ticket.priority}")
    except ValidationError as e:
        print(f">> INVALID: {e}")

print(f"\n{ok}/5 valid")