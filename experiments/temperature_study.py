from collections import Counter
from typing import Literal

import requests
from pydantic import BaseModel, ValidationError

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"
RUNS = 5


class Ticket(BaseModel):
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str


TICKETS = [
    ("I was charged twice for my subscription this month and I need a refund ASAP!", "billing"),
    ("The mobile app crashes every time I try to upload a photo larger than 5MB on Android 14.", "technical"),
    ("I forgot my password and the reset email never arrives, even in spam. I've tried 4 times.", "account"),
    ("Can you add a dark mode to the dashboard? It would really help when working late at night.", "other"),
    ("After your last update, exporting reports to PDF takes over 10 minutes and sometimes times out completely.", "technical"),
]


def build_prompt(ticket):
    return f"""Classify this support ticket.
category: billing, technical, account, or other.
priority: low, medium, or high.
summary: at most 6 words, no device names or version numbers.

Ticket: {ticket}"""


def classify(ticket, temperature):
    r = requests.post(URL, json={
        "model": MODEL,
        "prompt": build_prompt(ticket),
        "stream": False,
        "format": Ticket.model_json_schema(),
        "options": {"temperature": temperature, "seed": 42},
    })
    try:
        return Ticket.model_validate_json(r.json()["response"])
    except ValidationError:
        return None


for temp in [0.0, 0.7]:
    print(f"\n===== Temperature {temp} =====")
    total_correct = 0
    for i, (ticket, expected) in enumerate(TICKETS):
        results = [classify(ticket, temp) for _ in range(RUNS)]
        categories = [r.category if r else "INVALID" for r in results]
        summaries = {r.summary for r in results if r}
        counts = Counter(categories)
        if temp == 0.0:
            print("   ", [r.summary if r else None for r in results])
        correct = counts[expected]
        total_correct += correct
        print(f"Ticket {i+1} (expected {expected}): {dict(counts)} | "
              f"{correct}/{RUNS} correct | {len(summaries)} unique summaries")
    print(f"Accuracy: {total_correct}/{len(TICKETS) * RUNS}")