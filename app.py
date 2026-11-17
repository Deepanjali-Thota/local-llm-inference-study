import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"
NS = 1_000_000_000

app = FastAPI(title="Local LLM API")


class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    model: str
    response: str
    tokens: int
    gen_tps: float
    total_s: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    start = time.perf_counter()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": req.prompt,
                "stream": False,
                "options": {"temperature": req.temperature},
            },
            timeout=120,
        )
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama is not running")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Model took too long to respond")

    data = r.json()

    return GenerateResponse(
        model=MODEL,
        response=data["response"],
        tokens=data["eval_count"],
        gen_tps=data["eval_count"] / (data["eval_duration"] / NS),
        total_s=time.perf_counter() - start,
    )