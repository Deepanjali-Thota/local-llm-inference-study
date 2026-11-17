# Benchmarks

## Hardware
- Windows laptop, 16 GB RAM, CPU only (no GPU)
- Ollama 0.40.16

## Benchmark conditions
- Close Chrome and other heavy apps before every run
- Laptop plugged in, Windows Power mode set to "Best performance"
- Note whether the model was warm (already loaded) or cold
- First run of each prompt = new-prompt TTFT; repeat runs use the prompt cache

## Results

5 prompts × 3 runs, after warm-up, charger plugged in, Best performance mode.

| Model | Quant | TTFT (new prompt) | TTFT (cached) | Gen tok/s (median) | RAM | Notes |
|---|---|---|---|---|---|---|
| llama3.2:3b | (default) | 0.57s | 0.16s | 9.6 | 4.1 GB | CPU only, ctx 16384 |

### Cold vs warm start (llama3.2:3b)

| State | When it happens | TTFT | Load time |
|---|---|---|---|
| True cold (from disk) | First request after reboot | 7.07s | 6.14s |
| Semi-cold (OS file cache) | Model unloaded, file recently used | 3.43–4.21s | 2.71–3.44s |
| Warm (model in RAM) | Within keep_alive window (5 min default) | 0.36s | 0.01s |

## Observations
- llama3.2:3b expanded REST as "Representational State of Resource" on every run. The correct expansion is "Representational State Transfer", so small models can be confidently and consistently wrong on basic facts.
- Prompt caching inflates prompt tok/s on repeated prompts. Measure only uncached tokens.
- Prompt tok/s is unreliable for short or cached prompts; fixed overhead dominates.
- On Windows, using `localhost` added ~2s to TTFT due to IPv6 (::1) fallback. Switching to `127.0.0.1` reduced TTFT from 2.24s to 0.21s. Server-side metrics (`--verbose`) did not show this; only client-side timing did.
- A single short run showed 14 tok/s, but sustained benchmarking gave 9.6 tok/s. Single runs overstate speed.
- Long answers (500+ tokens) generate slightly slower (~9.1 tok/s) than short ones (~10–11 tok/s).
- Power mode (Best performance + charger) made little difference: 9.4 → 9.6 tok/s.
- Cold start is ~12x slower than warm (median 4.21s vs 0.36s TTFT). The first cold load from disk took 7.07s; later loads were faster because Windows cached the model file in RAM.
- Trade-off: keeping the model loaded (`keep_alive: -1`) removes cold starts but holds ~4 GB of RAM permanently.
