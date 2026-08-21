"""Run a simple AI chat follow-up test:
1. Ask "How many students are in the system?"
2. Then ask "What are their names?" using the assistant reply in conversation history.

Prints both responses and context for inspection.
"""
import os
import sys
import json

# Ensure Django settings are loaded
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinev12.settings")
try:
    import django
    django.setup()
except Exception as e:
    print("Failed to setup Django:", e)
    sys.exit(1)

from core.ai_chat import PollinationAIChat

def run_test():
    ai = PollinationAIChat()

    first = "How many students are in the system?"
    print("\n=== USER: ", first)
    res1 = ai.chat(user_message=first, conversation_history=None)
    print("--- RESULT 1 ---")
    print(json.dumps(res1, indent=2, ensure_ascii=False))

    # Prepare conversation history to simulate follow-up
    conv = [
        {"role": "user", "content": first},
        {"role": "assistant", "content": res1.get("response", "")}
    ]

    second = "What are their names?"
    print("\n=== USER (follow-up): ", second)
    res2 = ai.chat(user_message=second, conversation_history=conv)
    print("--- RESULT 2 ---")
    print(json.dumps(res2, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    try:
        run_test()
    except Exception as e:
        print("Test run failed:", e)
        raise
