"""Smoke tests for core.ai_chat PollinationAIChat client.

Runs a few example queries to validate intent parsing and response modes.
"""
import os
import sys
import django

# Ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Minimal Django setup guard
if os.path.exists(os.path.join(ROOT, "manage.py")):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")

try:
    django.setup()
except Exception:
    pass

from core.ai_chat import PollinationAIChat


def run_test(message, student_id=None):
    client = PollinationAIChat()
    result = client.chat(message, student_id=student_id)
    print("---")
    print("Message:", message)
    print("Success:", result.get("success"))
    print("Mode:", result.get("mode"))
    print("Provider:", result.get("provider"))
    print("Model:", result.get("model_used"))
    print("Response:\n", result.get("response"))


def main():
    tests = [
        "Show me student 9486",
        "How many students are in the system?",
        "Analyze the Gonza stream",
        "Tell me about the Education Act on discipline",
    ]

    for t in tests:
        run_test(t)


if __name__ == '__main__':
    main()
