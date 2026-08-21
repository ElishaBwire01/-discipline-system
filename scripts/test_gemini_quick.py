"""Quick live test of gemini-3.1-flash-lite with simple questions."""
import os, sys, json, urllib.request, urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL   = "gemini-3.1-flash-lite"

if not API_KEY:
    print("[FAIL] GEMINI_API_KEY not set"); sys.exit(1)

def ask(question):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={API_KEY}")
    payload = json.dumps({
        "contents": [{"parts": [{"text": question}]}],
        "generationConfig": {"maxOutputTokens": 100, "temperature": 0.1}
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        return body["candidates"][0]["content"]["parts"][0]["text"].strip()

TESTS = [
    "What is 2 + 2?",
    "What is the capital of Uganda?",
    "Say hi in one sentence.",
    "A student missed school 10 times this month. Should a teacher be worried? Yes or no and one reason.",
    "List 3 common student discipline problems in schools.",
]

print(f"\nModel: {MODEL}")
print(f"Key  : {API_KEY[:8]}...{API_KEY[-4:]}")
print("=" * 60)

all_passed = True
for q in TESTS:
    print(f"\nQ: {q}")
    try:
        reply = ask(q)
        print(f"A: {reply}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        print(f"FAIL HTTP {e.code}: {body}")
        all_passed = False
    except Exception as e:
        print(f"FAIL: {e}")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print(f"RESULT: {MODEL} is WORKING — safe to use.\n")
else:
    print(f"RESULT: Some tests failed — check errors above.\n")
