import time
from typing import Literal

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError, field_validator

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"
NS = 1_000_000_000
MAX_SUMMARY_WORDS = 6

app = FastAPI(title="Local LLM API")


# ---------- Models ----------

class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    model: str
    response: str
    tokens: int
    gen_tps: float
    total_s: float


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


class ClassifyRequest(BaseModel):
    ticket: str


class ClassifyResponse(BaseModel):
    model: str
    result: Ticket
    attempts: int
    total_s: float


# ---------- Ollama helper ----------

def call_ollama(payload):
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama is not running")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Model took too long to respond")


def build_prompt(ticket):
    return f"""Classify this support ticket.

category:
- billing: payments, charges, refunds, invoices, receipts, pricing, discounts, plans
- technical: bugs, errors, crashes, slowness, something not working as expected
- account: login, password, profile, permissions, security, deleting or changing an account
- other: feature requests, feedback, company questions, legal, partnerships, anything else

priority: low, medium, or high.
summary: at most {MAX_SUMMARY_WORDS} words, no device names or version numbers.

Ticket: {ticket}"""

# ---------- Endpoints ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/generate",
    response_model=GenerateResponse,
    responses={
        503: {"description": "Ollama is not running"},
        504: {"description": "Model took too long to respond"},
    },
)
def generate(req: GenerateRequest):
    start = time.perf_counter()
    data = call_ollama({
        "model": MODEL,
        "prompt": req.prompt,
        "stream": False,
        "options": {"temperature": req.temperature},
    })
    return GenerateResponse(
        model=MODEL,
        response=data["response"],
        tokens=data["eval_count"],
        gen_tps=data["eval_count"] / (data["eval_duration"] / NS),
        total_s=time.perf_counter() - start,
    )


@app.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={
        502: {"description": "Model output failed validation after all retries"},
        503: {"description": "Ollama is not running"},
        504: {"description": "Model took too long to respond"},
    },
)
def classify(req: ClassifyRequest, max_attempts: int = 2):
    start = time.perf_counter()
    prompt = build_prompt(req.ticket)

    for attempt in range(1, max_attempts + 1):
        data = call_ollama({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": Ticket.model_json_schema(),
            "options": {"temperature": 0},
        })
        text = data["response"]

        try:
            result = Ticket.model_validate_json(text)
            return ClassifyResponse(
                model=MODEL,
                result=result,
                attempts=attempt,
                total_s=time.perf_counter() - start,
            )
        except ValidationError as e:
            error = e.errors()[0]["msg"]
            prompt = build_prompt(req.ticket) + f"""

Your previous answer was invalid: {error}
Previous answer: {text.strip()}
Fix the problem and answer again."""

    raise HTTPException(
        status_code=502,
        detail=f"Model output invalid after {max_attempts} attempts: {error}",
    )