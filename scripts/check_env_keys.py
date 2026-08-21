"""Show which AI provider keys are set (masked for safety)."""
import os

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env_vars[k.strip()] = v.strip().strip('"').strip("'")

keys_to_check = [
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "OPENAI_API_KEY",
]

for key in keys_to_check:
    val = env_vars.get(key, "")
    if not val:
        print(f"  {key:30s}  [EMPTY - not configured]")
    else:
        masked = val[:8] + "..." + val[-4:] if len(val) > 14 else val[:4] + "***"
        print(f"  {key:30s}  {masked}  [SET, {len(val)} chars]")
