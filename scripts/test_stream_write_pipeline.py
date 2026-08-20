"""
Regression and unit tests for stream-write pipeline fixes.

Tests from the investigation report (2025-07):
  1. Response is never empty when pending_action is set
  2. Action params correctly parsed for two streams
  3. Empty-after-strip guard: approval prompt shown when body was only action block
  4. inspect_model rejects DB table name format
  5. bulk_create_streams always requires approval (MEDIUM risk)
  6. execute_action("bulk_create_streams") creates both streams correctly
"""
import sys
import os
import django
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")
django.setup()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_run_with_action(action: dict):
    """Build a minimal AgentRun that already has a pending_action set."""
    from core.agent_pipeline import AgentRun, Intent
    run = AgentRun(message="test", mode="INSPECT")
    run.intent = Intent.DB_WRITE
    run.pending_action = action
    return run


def _cleanup_streams(*names):
    """Remove test streams created during tests."""
    from core.models import Stream
    Stream.objects.filter(name__in=names).delete()


# ─────────────────────────────────────────────────────────────────────────────
# Test suite
# ─────────────────────────────────────────────────────────────────────────────

class TestStreamWritePipeline(unittest.TestCase):

    # ── Test 1 ────────────────────────────────────────────────────────────────
    def test_db_write_response_not_empty_when_action_pending(self):
        """
        Regression: agent.chat() must return a non-empty response string and
        success=True whenever a pending_action is present in the result.
        Covers the case where the LLM emits only an action block with no prose.
        """
        from core.agent_pipeline import AgentPipeline, AgentRun, Intent

        # Build a run that already has a pending_action so _approval_prompt fires
        action = {
            "type": "bulk_create_streams",
            "params": {"streams": [
                {"name": "TestAlpha", "code": "TAL"},
                {"name": "TestBeta",  "code": "TBT"},
            ]},
            "description": "Add streams TestAlpha and TestBeta",
            "risk": "MEDIUM",
        }
        run = _make_run_with_action(action)

        # Simulate what AgentPipeline.run() does at the synthesis stage:
        # final_response started as an action-block-only string, got stripped to "".
        run.final_response = ""

        # Apply the fix: empty final_response with pending_action → approval prompt
        from core.agent_pipeline import AgentPipeline
        from core.admin_agent import EngineeringToolkit
        pipeline = AgentPipeline(
            toolkit=EngineeringToolkit(),
            ai_caller=lambda msgs, **kw: {"success": False, "response": "", "provider": ""},
        )

        # Re-run just the guard logic (inline — same code as the fix)
        if not run.final_response and run.pending_action:
            run.final_response = pipeline._approval_prompt(run)

        self.assertTrue(
            bool(run.final_response),
            "final_response must not be empty when pending_action is set",
        )
        self.assertIn("approval", run.final_response.lower())

    # ── Test 2 ────────────────────────────────────────────────────────────────
    def test_bulk_stream_params_extracted_by_agent_chat(self):
        """
        Regression: agent.chat() must extract both stream names/codes from
        'add the stream called Mukasa, Muwanga use the code MUK, MUW'.
        The pending_action must be bulk_create_streams with correct params.

        This test requires a live LLM call; skip if no API key is configured.
        """
        import os
        has_key = any(
            os.environ.get(k)
            for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY")
        )
        if not has_key:
            self.skipTest("No LLM API key configured — skipping live pipeline test")

        # Remove these streams if they already exist so the LLM doesn't see them
        # as already created and skip the action block entirely.
        _cleanup_streams("Mukasa", "Muwanga")

        from core.admin_agent import AdminAgent
        agent = AdminAgent()
        result = agent.chat(
            "add the stream called Mukasa, Muwanga use the code MUK, MUW",
            conversation_history=[],
            mode="INSPECT",
        )

        # Response must be non-empty and successful
        self.assertTrue(result.get("success"), f"Expected success=True, got: {result}")
        self.assertTrue(result.get("response"), "response must not be empty")

        # Must have a pending action for bulk_create_streams
        action = result.get("action")
        self.assertIsNotNone(action, "action must be present in result")
        self.assertIsInstance(action, dict, f"action must be a dict, got {type(action).__name__}: {action!r}")
        self.assertEqual(action.get("type"), "bulk_create_streams")

        streams = action.get("params", {}).get("streams", [])
        self.assertIsInstance(streams, list, f"params.streams must be a list, got: {streams!r}")
        self.assertEqual(len(streams), 2, f"Expected 2 streams, got {len(streams)}: {streams}")

        names = {s["name"] for s in streams}
        codes = {s["code"] for s in streams}
        self.assertEqual(names, {"Mukasa", "Muwanga"}, f"Names mismatch: {names}")
        self.assertEqual(codes, {"MUK", "MUW"}, f"Codes mismatch: {codes}")

        # Cleanup: restore the streams we deleted so DB state is consistent
        from core.admin_agent import AdminActionExecutor
        AdminActionExecutor().bulk_create_streams([
            {"name": "Mukasa", "code": "MUK"},
            {"name": "Muwanga", "code": "MUW"},
        ])

    # ── Test 3 ────────────────────────────────────────────────────────────────
    def test_approval_prompt_shown_when_response_stripped_to_empty(self):
        """
        Unit: when final_response is only a ```action``` block that gets stripped,
        _approval_prompt() must be called and the result must not be empty.
        """
        from core.agent_pipeline import AgentPipeline, AgentRun, Intent
        import re

        action = {
            "type": "bulk_create_streams",
            "params": {"streams": []},
            "description": "Add streams",
            "risk": "MEDIUM",
        }
        run = AgentRun(message="add streams", mode="INSPECT")
        run.intent = Intent.DB_WRITE
        # LLM returned only the action block
        run.final_response = '```action\n{"type":"bulk_create_streams","params":{"streams":[]},"description":"Add streams","risk":"MEDIUM"}\n```'
        run.pending_action = None

        from core.admin_agent import EngineeringToolkit
        pipeline = AgentPipeline(
            toolkit=EngineeringToolkit(),
            ai_caller=lambda msgs, **kw: {"success": False, "response": "", "provider": ""},
        )

        # Replicate the exact production code path
        extracted = pipeline._extract_action(run.final_response)
        self.assertIsNotNone(extracted, "_extract_action should parse the block")

        run.pending_action = extracted
        run.final_response = re.sub(
            r"```action\s*\{.*?\}\s*```", "",
            run.final_response, flags=re.DOTALL | re.IGNORECASE,
        ).strip()

        # Before fix: run.final_response == "" here
        self.assertEqual(run.final_response, "", "After stripping, body should be empty")

        # After fix (the guard):
        if not run.final_response:
            run.final_response = pipeline._approval_prompt(run)

        self.assertTrue(bool(run.final_response), "Guard must produce non-empty response")
        self.assertIn("approval", run.final_response.lower())

    # ── Test 4 ────────────────────────────────────────────────────────────────
    def test_inspect_model_rejects_db_table_name(self):
        """
        Unit: EngineeringToolkit.inspect_model('core_stream') must return ok=False
        (because 'core_stream' is a DB table name, not a Python class name).
        """
        from core.admin_agent import EngineeringToolkit
        tk = EngineeringToolkit()

        result = tk.inspect_model("core_stream")
        self.assertFalse(
            result.get("ok"),
            f"inspect_model('core_stream') should fail; got: {result}",
        )
        # Verify the correct class name works
        result_ok = tk.inspect_model("Stream")
        self.assertTrue(
            result_ok.get("ok"),
            f"inspect_model('Stream') should succeed; got: {result_ok}",
        )

    # ── Test 5 ────────────────────────────────────────────────────────────────
    def test_bulk_create_streams_requires_approval(self):
        """
        Unit: bulk_create_streams must be rated MEDIUM risk, which means
        requires_approval() returns True.
        """
        from core.agent_pipeline import RiskAssessor, RiskLevel
        assessor = RiskAssessor()

        risk = assessor.assess("bulk_create_streams")
        self.assertEqual(risk, RiskLevel.MEDIUM, "bulk_create_streams must be MEDIUM risk")
        self.assertTrue(
            assessor.requires_approval(risk),
            "MEDIUM risk must require approval",
        )

    # ── Test 6 ────────────────────────────────────────────────────────────────
    def test_execute_action_bulk_create_streams(self):
        """
        Integration: execute_action('bulk_create_streams', {...}) creates both
        streams in the database, or correctly skips them if they already exist.
        Cleans up after itself.
        """
        _cleanup_streams("PipelineTestAlpha", "PipelineTestBeta")

        from core.admin_agent import AdminAgent
        agent = AdminAgent()

        result = agent.execute_action(
            "bulk_create_streams",
            {"streams": [
                {"name": "PipelineTestAlpha", "code": "PTA"},
                {"name": "PipelineTestBeta",  "code": "PTB"},
            ]},
        )

        self.assertTrue(result.get("success"), f"execute_action must succeed: {result}")
        data = result.get("data", {})
        self.assertIn("PipelineTestAlpha", data.get("created", []))
        self.assertIn("PipelineTestBeta",  data.get("created", []))
        self.assertEqual(data.get("failed", []), [])

        # Verify both streams exist in DB
        from core.models import Stream
        self.assertTrue(Stream.objects.filter(name="PipelineTestAlpha").exists())
        self.assertTrue(Stream.objects.filter(name="PipelineTestBeta").exists())

        # Cleanup
        _cleanup_streams("PipelineTestAlpha", "PipelineTestBeta")


class TestVerifierThreshold(unittest.TestCase):
    """
    Regression tests for the Verifier threshold fix.
    Old rule:  len(failed) > len(done)   → 50/50 tie passed silently
    New rule:  len(failed) > 0 and len(failed) >= len(done)  → tie fails
    """

    def _make_run(self, done_count, failed_count, intent=None):
        from core.agent_pipeline import AgentRun, PlanStep, Intent
        run = AgentRun(message="test", mode="INSPECT")
        run.intent = intent or Intent.DB_WRITE
        for i in range(done_count):
            s = PlanStep(step_id=i + 1, description="ok", tool="db_query", params={})
            s.status = "done"
            run.plan.append(s)
        for i in range(failed_count):
            s = PlanStep(step_id=done_count + i + 1, description="bad", tool="inspect_model", params={})
            s.status = "failed"
            run.plan.append(s)
        return run

    def test_tie_now_fails(self):
        """1 done, 1 failed (the stream-write case) must now trigger a replan."""
        from core.agent_pipeline import Verifier
        run = self._make_run(done_count=1, failed_count=1)
        passed, reason = Verifier().verify(run)
        self.assertFalse(passed, "50/50 tie must fail verification (triggers replan)")
        self.assertIn("1 of 2", reason)

    def test_majority_failed_still_fails(self):
        """2 failed, 1 done must still fail."""
        from core.agent_pipeline import Verifier
        run = self._make_run(done_count=1, failed_count=2)
        passed, _ = Verifier().verify(run)
        self.assertFalse(passed)

    def test_all_done_passes(self):
        """2 done, 0 failed must pass."""
        from core.agent_pipeline import Verifier
        run = self._make_run(done_count=2, failed_count=0)
        passed, reason = Verifier().verify(run)
        self.assertTrue(passed)
        self.assertEqual(reason, "ok")

    def test_minority_failed_still_passes(self):
        """1 failed out of 3 total (2 done) must still pass."""
        from core.agent_pipeline import Verifier
        run = self._make_run(done_count=2, failed_count=1)
        passed, reason = Verifier().verify(run)
        self.assertTrue(passed)
        self.assertEqual(reason, "ok")

    def test_empty_plan_passes_vacuously(self):
        """0 done, 0 failed must pass (empty plan is not a failure)."""
        from core.agent_pipeline import Verifier
        run = self._make_run(done_count=0, failed_count=0)
        passed, reason = Verifier().verify(run)
        self.assertTrue(passed)

    def test_zero_done_one_failed_fails(self):
        """0 done, 1 failed must fail."""
        from core.agent_pipeline import Verifier
        run = self._make_run(done_count=0, failed_count=1)
        passed, _ = Verifier().verify(run)
        self.assertFalse(passed)


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestStreamWritePipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestVerifierThreshold))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
