"""
Inspect Verifier threshold behavior across different done/failed step ratios.
Investigation only — no fixes applied here.
"""
import sys, os, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")
django.setup()

from core.agent_pipeline import Verifier, AgentRun, PlanStep, RiskLevel, Intent


def make_run_with_plan(done_count, failed_count, intent=Intent.DB_WRITE):
    run = AgentRun(message="test", mode="INSPECT")
    run.intent = intent
    for i in range(done_count):
        s = PlanStep(step_id=i+1, description="ok step", tool="db_query", params={})
        s.status = "done"
        run.plan.append(s)
    for i in range(failed_count):
        s = PlanStep(step_id=done_count+i+1, description="bad step", tool="inspect_model", params={})
        s.status = "failed"
        run.plan.append(s)
    return run


v = Verifier()

scenarios = [
    (0, 1, "zero done, one failed"),
    (1, 0, "one done, zero failed"),
    (1, 1, "one done, one failed   (stream-write case -- 50/50)"),
    (1, 2, "one done, two failed   (majority failed)"),
    (2, 1, "two done, one failed"),
    (0, 2, "zero done, two failed"),
    (2, 3, "two done, three failed (majority failed)"),
    (0, 0, "no steps at all"),
]

print("Verifier threshold analysis (done > failed is the pass rule):")
print()
print(f"  {'Scenario':<48} {'pass?':<8} reason")
print("  " + "-" * 75)
for done, failed, label in scenarios:
    run = make_run_with_plan(done, failed)
    passed, reason = v.verify(run)
    print(f"  {label:<48} {str(passed):<8} {reason}")

print()
print("The threshold check (line 705):")
print("  if len(failed) > len(done):  → fail")
print("  otherwise                    → pass")
print()
print("Implication: equal failed and done (50/50) passes.")
print("Implication: zero done and zero failed also passes (no steps).")
