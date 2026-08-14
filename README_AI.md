AI provider setup
=================

This project supports multiple AI providers with automatic failover.

Environment variables
- `OPENAI_API_KEY` : OpenAI-compatible API key
- `OPENROUTER_API_KEY` : OpenRouter API key (alternative)
- `GROQ_API_KEY` : Groq API key
- `GEMINI_API_KEY` : Google Gemini/API key
- `POLLINATION_API_KEY` : Pollinations API key

Key formats (examples):
- Groq: starts with `gsk_...` (set `GROQ_API_KEY`)
- Google Gemini: starts with `AQ.` (set `GEMINI_API_KEY`)
- OpenRouter: starts with `sk-or-...` (set `OPENROUTER_API_KEY`)
- OpenAI: starts with `sk-` (set `OPENAI_API_KEY`)

Optional configuration
- `OPENAI_MODEL`, `OPENROUTER_MODEL`, `GROQ_MODEL`, `GEMINI_MODEL`, `POLLINATION_MODEL` to override default model names
- `AI_CACHE_SECONDS` : cache duration in seconds (default 300)
- `AI_MAX_RETRIES` : retries per provider (default 2)
- `AI_BACKOFF_FACTOR` : backoff multiplier in seconds (default 0.5)

Quick test
1. Export keys in your shell, e.g. (PowerShell):

```powershell
$env:OPENAI_API_KEY = "sk-..."
python -m scripts.ai_integration_test
```

If no keys are set, the script will exercise the fallback/data-driven path and print the response.

Security notes
- Never commit API keys or secrets to source control. Use environment variables or a secrets manager.
- The system avoids exposing `SECRET_KEY` or other secrets to model prompts.

Files of interest
- `core/ai_chat.py` — main AI client with provider failover
- `core/ai_providers.py` — central provider key/model loader
- `scripts/ai_integration_test.py` — simple integration test script
