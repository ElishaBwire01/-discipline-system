"""Test all 3 AI providers with a short question."""
import os, sys, json, urllib.request, urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

QUESTION = "What is 2 + 2? Answer in one word."

def test_openrouter():
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    model   = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
    url     = "https://openrouter.ai/api/v1/chat/completions"
    if not api_key:
        return None, "no key"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": QUESTION}], "max_tokens": 10, "temperature": 0}).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        return body["choices"][0]["message"]["content"].strip(), model

def test_groq():
    api_key = os.environ.get("GROQ_API_KEY", "")
    model   = os.environ.get("GROQ_MODEL", "llama3-8b-8192")
    url     = "https://api.groq.com/openai/v1/chat/completions"
    if not api_key:
        return None, "no key"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": QUESTION}], "max_tokens": 10, "temperature": 0}).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        return body["choices"][0]["message"]["content"].strip(), model

def test_gemini():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model   = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    url     = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    if not api_key:
        return None, "no key"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"contents": [{"parts": [{"text": QUESTION}]}], "generationConfig": {"maxOutputTokens": 10, "temperature": 0}}).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        return body["candidates"][0]["content"]["parts"][0]["text"].strip(), model

print(f"\nQuestion asked: \"{QUESTION}\"\n")
print("-" * 50)

for name, fn in [("Groq", test_groq), ("OpenRouter", test_openrouter), ("Gemini", test_gemini)]:
    try:
        reply, model = fn()
        if reply is None:
            print(f"  {name:12s}  SKIPPED ({model})")
        else:
            print(f"  {name:12s}  [{model}]  =>  {reply}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        print(f"  {name:12s}  FAIL HTTP {e.code}: {body}")
    except Exception as e:
        print(f"  {name:12s}  FAIL {type(e).__name__}: {e}")

print("-" * 50)
