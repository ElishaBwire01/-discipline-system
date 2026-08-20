"""
Trace the exact pipeline for:
  "add the stream called Mukasa, Muwanga use the code MUK, MUW"
"""
import sys, os, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")
django.setup()

from core.admin_agent import AdminAgent, AdminActionExecutor
from core.agent_pipeline import IntentClassifier, Intent

msg = "add the stream called Mukasa, Muwanga use the code MUK, MUW"

# ── Step 1: IntentClassifier ──────────────────────────────────────────────────
clf = IntentClassifier()
intent = clf.classify(msg)
print(f"[1] IntentClassifier => {intent.value}")

# ── Step 2: Is LQR called or does it go straight to pipeline? ────────────────
from core.admin_agent_queries import LocalQueryRouter
router = LocalQueryRouter()
local_answer = router.answer(msg)
print(f"[2] LocalQueryRouter => {local_answer!r}")

# ── Step 3: Full chat() call ──────────────────────────────────────────────────
print()
print("[3] agent.chat() full pipeline trace:")
agent = AdminAgent()
result = agent.chat(msg, conversation_history=[], mode="INSPECT")

print(f"    success:       {result.get('success')}")
print(f"    intent:        {result.get('intent')}")
print(f"    source:        {result.get('source', 'pipeline')}")
print(f"    provider:      {result.get('provider')}")
print(f"    replan_count:  {result.get('replan_count')}")
print(f"    think_steps:   {len(result.get('think_steps', []))}")
print()

print("[4] Think steps:")
for step in result.get("think_steps", []):
    phase  = step.get("phase", "")
    label  = step.get("label", "").encode("ascii", "replace").decode()
    detail = step.get("detail", "")[:150].encode("ascii", "replace").decode()
    status = step.get("status", "")
    print(f"    [{phase:10}] {label}  ({status})")
    if detail:
        print(f"                 {detail}")

print()
print("[5] Pending action (approval gate):")
action = result.get("action")
print(f"    {action}")

print()
print("[6] Response snippet (first 600 chars):")
resp = str(result.get("response", "")).encode("ascii", "replace").decode()
print(resp[:600])

# ── Step 4: Simulate admin approving the action ───────────────────────────────
print()
print("=" * 60)
print("[7] Simulating admin approval of pending action...")

if action and isinstance(action, dict):
    action_type = action.get("type", "")
    params = action.get("params", {})
    print(f"    action_type: {action_type!r}")
    print(f"    params:      {params}")
    print()

    # Direct call to execute_action
    exec_result = agent.execute_action(action_type, params)
    print(f"    execute_action result:")
    print(f"      success: {exec_result.get('success')}")
    msg_out = str(exec_result.get('message', '')).encode('ascii','replace').decode()
    print(f"      message: {msg_out}")
    data = exec_result.get('data')
    print(f"      data:    {data}")

    # ── Step 5: Also test create_stream directly ──────────────────────────────
    print()
    print("[8] Direct create_stream tests:")
    ex = AdminActionExecutor()

    for name, code in [("Mukasa", "MUK"), ("Muwanga", "MUW")]:
        r = ex.create_stream(name=name, code=code)
        print(f"    create_stream({name!r}, {code!r}) => success={r['success']} msg={r['message']!r}")
else:
    print("    No pending action in result — pipeline may have gone to read-only path")
    print()

    # Still test create_stream directly
    print("[8] Direct create_stream tests (action not returned from pipeline):")
    ex = AdminActionExecutor()
    for name, code in [("Mukasa", "MUK"), ("Muwanga", "MUW")]:
        r = ex.create_stream(name=name, code=code)
        print(f"    create_stream({name!r}, {code!r}) => success={r['success']} msg={r['message']!r}")

# ── Step 6: bulk_create_streams with the expected params ─────────────────────
print()
print("[9] bulk_create_streams test:")
ex = AdminActionExecutor()
streams_list = [
    {"name": "Mukasa", "code": "MUK"},
    {"name": "Muwanga", "code": "MUW"},
]
r = ex.bulk_create_streams(streams_list)
print(f"    success: {r['success']}")
msg_out = str(r.get('message', '')).encode('ascii','replace').decode()
print(f"    message: {msg_out}")
print(f"    data:    {r.get('data')}")

# ── Step 7: Check Stream model unique_together constraint ─────────────────────
print()
print("[10] Stream model unique_together check:")
from core.models import Stream, School
school = School.objects.first()
print(f"    School: {school}")
print(f"    unique_together: ('school', 'name')")
print(f"    Existing streams:")
for s in Stream.objects.all():
    print(f"      id={s.id} name={s.name!r} code={s.code!r} school_id={s.school_id} active={s.is_active}")
