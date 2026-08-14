## Removed literal API keys. Set real keys in your shell or CI secrets.
# Example (do NOT commit real keys):
# $env:GROQ_API_KEY = "gsk_..."
# $env:GEMINI_API_KEY = "AQ...."
# $env:OPENROUTER_API_KEY = "sk-or-..."
# $env:OPENAI_API_KEY = "sk-..."
# $env:POLLINATION_API_KEY = "pl-..."

# To run tests locally, set env vars in your shell or use a secrets manager.
$env:GROQ_API_KEY = ""
$env:GEMINI_API_KEY = ""
$env:OPENROUTER_API_KEY = ""
$env:OPENAI_API_KEY = ""
$env:POLLINATION_API_KEY = ""

python -m scripts.ai_integration_test
python -m scripts.ai_smoke_tests