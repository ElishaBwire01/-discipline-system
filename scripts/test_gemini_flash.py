"""Test the top Gemini models available on this API key with school-relevant questions."""
import os, sys, json, urllib.request, urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY      = os.environ.get("GEMINI_API_KEY", "")
CURRENT_MODEL = os.environ.get("GEMINI_MODEL", "gemma-4-26b-a4b-it")

if not API_KEY:
    print("[FAIL] GEMINI_API_KEY not set"); sys.exit(1)

# Models to test - newest / most promising first based on listing
CANDIDATES = [
    "gemini-flash-latest",        # Latest Flash (auto-updated)
    "gemini-3.5-flash",           # Gemini 3.5 Flash - very new
    "gemini-3.1-flash-lite",      # Gemini 3.1 Flash Lite - fast & clean
    "gemini-3.7-flash",           # Gemini 3.7 Flash
]

QUESTIONS = [
    ("Clean short",   "What is 2 + 2? One word only."),
    ("School use",    "A student has 6 discipline reports this term. Is that critical? One sentence."),
    ("Risk advice",   "What is one quick intervention for a student who keeps skipping class?"),
]

def call_gemini(model, question):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    payload = json.dumps({
        "contents":        [{"parts": [{"text": question}]}],
        "generationConfig": {"maxOutputTokens": 80, "temperature": 0.1}
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        return body["candidates"][0]["content"]["parts"][0]["text"].strip()

def quality_score(reply, question):
    """0-3: +1 short, +1 no markdown bullets, +1 no question repeat."""
    score = 0
    if len(reply) < 120:           score += 1
    if "* " not in reply and "**" not in reply: score += 1
    if question.lower()[:20] not in reply.lower(): score += 1
    return score

# ── current model baseline ────────────────────────────────────────────────────
print(f"\nCurrent model  : {CURRENT_MODEL}")
print(f"Testing        : {', '.join(CANDIDATES)}")
print("=" * 72)

all_models = [CURRENT_MODEL] + CANDIDATES
scores = {}

for model in all_models:
    total = 0
    print(f"\n  [{model}]")
    for label, q in QUESTIONS:
        try:
            reply = call_gemini(model, q)
            sc    = quality_score(reply, q)
            total += sc
            noisy = sc < 3
            tag   = " *** NOISY ***" if noisy else " [clean]"
            print(f"    {label:14s}  score={sc}/3  => {reply[:90].replace(chr(10),' ')}{tag}")
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:120]
            print(f"    {label:14s}  FAIL HTTP {e.code}: {body[:80]}")
            total = -1
            break
        except Exception as e:
            print(f"    {label:14s}  FAIL {e}")
            total = -1
            break
    scores[model] = total
    if total >= 0:
        print(f"    TOTAL SCORE: {total}/{len(QUESTIONS)*3}")

# ── verdict ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("RANKING (higher = cleaner responses)\n")
ranked = sorted([(v, k) for k, v in scores.items() if v >= 0], reverse=True)
for i, (sc, model) in enumerate(ranked):
    tag = " <-- WINNER (recommended)" if i == 0 else ""
    old = " <-- YOUR CURRENT MODEL"   if model == CURRENT_MODEL else ""
    print(f"  #{i+1}  {model:40s}  {sc}/{len(QUESTIONS)*3}{tag}{old}")

if ranked:
    winner = ranked[0][1]
    if winner != CURRENT_MODEL:
        print(f"\n>>> To switch, run in your terminal:")
        print(f'    setx GEMINI_MODEL "{winner}"')
        print( "    Then restart your Django server.\n")
    else:
        print(f"\n>>> Your current model '{winner}' is already the best available.\n")
