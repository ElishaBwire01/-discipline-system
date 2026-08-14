"""Small integration test to exercise AI provider failover.

Run with: `python -m scripts.ai_integration_test` from project root.
It uses env vars for keys; if none are set the test will validate the data_fallback path.
"""
import os
import django
import sys

# Ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Minimal Django setup guard: if manage.py exists set the project's settings module
if os.path.exists(os.path.join(ROOT, "manage.py")):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")

try:
    django.setup()
except Exception:
    # Some environments won't have Django configured; continue with limited test
    pass

from core.ai_chat import PollinationAIChat


def run_test():
    client = PollinationAIChat()
    msg = "Hello — please introduce yourself briefly about the school assistant."
    print("Sending message to AI client (no real keys required)...")
    res = client.chat(msg)
    print("Result mode:", res.get("mode"))
    print("Provider/model:", res.get("provider"), res.get("model_used"))
    print("Response:\n", res.get("response"))


if __name__ == "__main__":
    run_test()
