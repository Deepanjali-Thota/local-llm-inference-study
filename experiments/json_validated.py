from typing import Literal

import requests
from pydantic import BaseModel, ValidationError, field_validator

URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"
MAX_SUMMARY_WORDS = 6


class Ticket(BaseModel):
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str

    @field_validator("summary")
    @classmethod
    def summary_is_short(cls, v):
        words = len(v.split())
        if words > MAX_SUMMARY_WORDS:
            raise ValueError(f"summary has {words} words, max is {MAX_SUMMARY_WORDS}")
        return v


TICKETS = [
    "I was charged twice for my subscription this month and I need a refund ASAP!",
    "The mobile app crashes every time I try to upload a photo larger than 5MB on Android 14.",
    "I forgot my password and the reset email never arrives, even in spam. I've tried 4 times.",
    "Can you add a dark mode to the dashboard? It would really help when working late at night.",
    "After your last update, exporting reports to PDF takes over 10 minutes and sometimes times out completely.",
]


def build_prompt(ticket):
    return f"""Classify this support ticket.
category: billing, technical, account, or other.
priority: low, medium, or high.
summary: at most {MAX_SUMMARY_WORDS} words, no device names or version numbers.

Ticket: {ticket}"""


def classify(ticket, max_attempts=2):
    prompt = build_prompt(ticket)

    for attempt in range(1, max_attempts + 1):
        r = requests.post(URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": Ticket.model_json_schema(),
            "options": {"temperature": 0.7},
        })
        text = r.json()["response"]

        try:
            result = Ticket.model_validate_json(text)
            return {"ok": True, "attempts": attempt, "ticket": result}
        except ValidationError as e:
            error = e.errors()[0]["msg"]
            print(f"   attempt {attempt} failed: {error} | got: {text.strip()}")
            prompt = build_prompt(ticket) + f"""

Your previous answer was invalid: {error}
Previous answer: {text.strip()}
Fix the problem and answer again."""

    return {"ok": False, "attempts": max_attempts, "error": error}


ok = 0
for i, ticket in enumerate(TICKETS):
    print(f"--- Ticket {i+1} ---")
    result = classify(ticket)
    if result["ok"]:
        ok += 1
        t = result["ticket"]
        print(f">> VALID after {result['attempts']} attempt(s): {t.category} / {t.priority} / {t.summary}")
    else:
        print(f">> FAILED after {result['attempts']} attempts: {result['error']}")

print(f"\n{ok}/{len(TICKETS)} valid")