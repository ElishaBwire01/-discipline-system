"""Quick terminal test for the OpenRouter API — reads from system env + .env file."""
import os
import sys
import json
import urllib.request
import urllib.error

# Load .env first (system env already loaded by OS)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # fall back to system env only

api_key = os.environ.get("OPENROUTER_API_KEY", "")
model   = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
url     = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

if not api_key:
    print("[FAIL] OPENROUTER_API_KEY is not set in .env or system environment")
    sys.exit(1)

masked = api_key[:10] + "..." + api_key[-4:]
print(f"[INFO] Key   : {masked}")
print(f"[INFO] Model : {model}")
print(f"[INFO] URL   : {url}")
print("[INFO] Sending test request...\n")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "DisciplineSystem-Test",
}
payload = json.dumps({
    "model": model,
    "messages": [{"role": "user", "content": "Reply with exactly the word: WORKING"}],
    "max_tokens": 10,
    "temperature": 0,
}).encode()

req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = json.loads(resp.read())
        reply     = body["choices"][0]["message"]["content"].strip()
        model_used = body.get("model", model)
        usage      = body.get("usage", {})

        print(f"[OK]  Reply      : {reply}")
        print(f"[OK]  Model used : {model_used}")
        if usage:
            print(f"[OK]  Tokens     : prompt={usage.get('prompt_tokens','?')}  completion={usage.get('completion_tokens','?')}")
        print("\n>>> OpenRouter API is WORKING <<<")

except urllib.error.HTTPError as e:
    body_text = e.read().decode("utf-8", errors="replace")
    print(f"[FAIL] HTTP {e.code} {e.reason}")
    try:
        err_json = json.loads(body_text)
        msg = err_json.get("error", {})
        print(f"[FAIL] Error    : {msg.get('message', body_text[:400])}")
        print(f"[FAIL] Code     : {msg.get('code', '-')}")
    except Exception:
        print(f"[FAIL] Body     : {body_text[:500]}")
    sys.exit(1)

except urllib.error.URLError as e:
    print(f"[FAIL] Network error: {e.reason}")
    print("[FAIL] Check internet connection or firewall/proxy settings")
    sys.exit(1)

except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    sys.exit(1)
