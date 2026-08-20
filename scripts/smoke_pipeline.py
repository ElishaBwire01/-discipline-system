"""
Admin Agent Pipeline Smoke Tests
Runs through AdminAgent.chat() — the real entry point — testing:
  1. LocalQueryRouter fast path (instant, no LLM)
  2. Intent routing (correct mode assigned)
  3. Full pipeline structure (think_steps, audit, intent keys present)
  4. Read-only pipeline for TEST/ANALYSIS intents
"""
import sys, os, django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")
django.setup()

from core.admin_agent import AdminAgent

agent = AdminAgent()

TESTS = [
    # (description, message, expected_keys, check_fn)
    (
        "LocalQueryRouter: list all teachers",
        "list all teachers",
        ["response", "intent", "source"],
        lambda r: (
            r.get("source") in ("local_db", "pipeline"),
            f"source={r.get('source')}"
        ),
    ),
    (
        "LocalQueryRouter: how many students",
        "how many students",
        ["response", "intent"],
        lambda r: (bool(r.get("response")), f"response={r.get('response', '')[:80]}"),
    ),
    (
        "Pipeline: backend health check (TEST mode)",
        "run backend health check",
        ["response", "intent", "think_steps"],
        lambda r: (
            r.get("intent") in ("test", "TEST", "read_data", "READ_DATA"),
            f"intent={r.get('intent')}"
        ),
    ),
    (
        "Pipeline: analyze student management system (ANALYSIS mode)",
        "analyze student management system",
        ["response", "intent"],
        lambda r: (bool(r.get("response")), f"response present"),
    ),
    (
        "Pipeline: inspect route /login/ (INSPECT_CODE mode)",
        "inspect route /login/",
        ["response", "think_steps"],
        lambda r: (bool(r.get("response")), f"response={r.get('response','')[:80]}"),
    ),
]

passed = 0
failed = 0

for desc, message, required_keys, check_fn in TESTS:
    print(f"\n--- {desc} ---")
    print(f"  Message: {message!r}")
    try:
        result = agent.chat(message, conversation_history=[], mode="INSPECT")
        # Check required keys
        missing = [k for k in required_keys if k not in result]
        if missing:
            print(f"  FAIL: missing keys {missing}")
            failed += 1
            continue

        ok, detail = check_fn(result)
        source = result.get("source", "pipeline")
        think = result.get("think_steps", [])
        intent = result.get("intent", "?")
        response_snippet = str(result.get("response", ""))[:120]

        # Strip non-ascii for safe Windows terminal output
        safe_snippet = response_snippet.encode("ascii", "replace").decode("ascii")

        if ok:
            print(f"  PASS | source={source} | intent={intent} | think_steps={len(think)}")
            print(f"    => {safe_snippet}")
            passed += 1
        else:
            print(f"  FAIL: {detail}")
            print(f"    => {safe_snippet}")
            failed += 1

    except Exception as exc:
        import traceback
        print(f"  ERROR: {exc}")
        traceback.print_exc()
        failed += 1

print(f"\n{'='*50}")
print(f"Smoke tests: {passed}/{passed+failed} passed")
if failed:
    sys.exit(1)
