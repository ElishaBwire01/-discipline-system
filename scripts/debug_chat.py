"""Quick test of the 3 questions that were failing in the chat."""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

django.setup()
from core.ai_chat import PollinationAIChat
ai = PollinationAIChat()

QUESTIONS = [
    "what is the name of this school",
    "how many students are in this school",
    "list all students",
]

for q in QUESTIONS:
    print(f"\nQ: {q}")
    result = ai.chat(q)
    print(f"   mode     : {result.get('mode')}")
    print(f"   provider : {result.get('provider', 'n/a')}")
    resp = result.get("response", "")
    print(f"   response : {resp[:200].replace(chr(10), ' ')}")
    print()
