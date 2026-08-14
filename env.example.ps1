<#
env.example.ps1 - Example PowerShell environment loader for local development.

COPY THIS FILE to `env.ps1` and fill in your secrets. Never commit `env.ps1`.
Run with: `. .\env.ps1` to load keys into the current session.

This file contains placeholders only — do not paste real keys to public places.
#>

Write-Host "Loading local API key placeholders (example)" -ForegroundColor Cyan

# Replace the values below with your own keys in a copied file named env.ps1
$env:GEMINI_API_KEY = "YOUR_GEMINI_KEY"
$env:GEMINI_MODEL = "gemma-4-26b"
$env:GROQ_API_KEY = "YOUR_GROQ_KEY"
$env:OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"
$env:OPENAI_API_KEY = "YOUR_OPENAI_KEY"

# Optional: print short prefixes so you know values are loaded (no secrets shown)
if ($env:GEMINI_API_KEY) { Write-Host "Gemini: $($env:GEMINI_API_KEY.Substring(0,10))..." }
if ($env:GROQ_API_KEY) { Write-Host "Groq: $($env:GROQ_API_KEY.Substring(0,10))..." }
if ($env:OPENROUTER_API_KEY) { Write-Host "OpenRouter: $($env:OPENROUTER_API_KEY.Substring(0,10))..." }

# Verify keys are present (uses Get-ChildItem to support dynamic names)
$keys = @('GEMINI_API_KEY','GROQ_API_KEY','OPENROUTER_API_KEY','OPENAI_API_KEY')
foreach ($key in $keys) {
    $entry = Get-ChildItem env:$key -ErrorAction SilentlyContinue
    if (-not $entry) {
        Write-Host "WARNING: $key is not set" -ForegroundColor Yellow
    }
}

Write-Host "env.example.ps1 loaded (example only). Copy to env.ps1 and insert real keys." -ForegroundColor Green
