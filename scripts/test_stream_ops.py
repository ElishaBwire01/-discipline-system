"""
Regression tests for stream operation bugs fixed in this session:

Bug 1 — reassign_stream_students called with from_stream_id/to_stream_id
  - execute_action must normalise ID-based params to name-based before dispatch
  - Synthesizer prompt now includes exact param names

Bug 2 — stream list not filtered by school
  - LocalQueryRouter._streams() must only return streams for School.objects.first()
  - AdminDataReader.get_full_school_context() streams must be scoped to school

Bug 1C — _get_stream helper scopes by school
  - reassign/delete/rename must not cross-contaminate streams from other schools
"""
import sys
import os
import unittest

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "disciplinary_program.settings")
django.setup()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_primary_school():
    from core.models import School
    return School.objects.first()


def _make_test_stream(name, code, school=None):
    from core.models import Stream, School
    if school is None:
        school = _get_primary_school()
    s, _ = Stream.objects.get_or_create(name=name, school=school, defaults={"code": code, "is_active": True})
    return s


def _delete_stream(name, school=None):
    from core.models import Stream, School
    if school is None:
        school = _get_primary_school()
    Stream.objects.filter(name=name, school=school).delete()


# ─────────────────────────────────────────────────────────────────────────────
# Bug 1 — param normalisation
# ─────────────────────────────────────────────────────────────────────────────

class TestReassignParamNormalisation(unittest.TestCase):

    def setUp(self):
        # Create two test streams in the primary school
        self.src = _make_test_stream("RegrTestSrc", "RSR")
        self.dst = _make_test_stream("RegrTestDst", "RDT")

    def tearDown(self):
        _delete_stream("RegrTestSrc")
        _delete_stream("RegrTestDst")

    def test_execute_action_with_id_params_normalises_to_names(self):
        """
        execute_action('reassign_stream_students', {from_stream_id: X, to_stream_id: Y})
        must not raise TypeError — it must normalise IDs to names before dispatch.
        """
        from core.admin_agent import AdminAgent
        agent = AdminAgent()
        result = agent.execute_action(
            "reassign_stream_students",
            {
                "from_stream_id": self.src.id,
                "to_stream_id": self.dst.id,
            },
        )
        # Should succeed (or return a structured error, not raise TypeError)
        self.assertIsInstance(result, dict, "execute_action must return a dict")
        self.assertNotIn("unexpected keyword argument", result.get("message", ""),
                         "Must not propagate raw TypeError message")

    def test_execute_action_with_name_params_works(self):
        """
        execute_action with correct name params must succeed.
        """
        from core.admin_agent import AdminAgent
        agent = AdminAgent()
        result = agent.execute_action(
            "reassign_stream_students",
            {
                "from_stream_name": self.src.name,
                "to_stream_name": self.dst.name,
            },
        )
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("success"), f"Expected success: {result}")
        # src should now be inactive
        self.src.refresh_from_db()
        self.assertFalse(self.src.is_active, "Source stream must be deactivated after reassign")

    def test_synth_prompt_contains_exact_param_names(self):
        """
        Synthesizer SYNTH_PROMPT must document from_stream_name/to_stream_name
        so the LLM knows not to use IDs.
        """
        from core.agent_pipeline import Synthesizer
        prompt = Synthesizer.SYNTH_PROMPT
        self.assertIn("from_stream_name", prompt,
                      "SYNTH_PROMPT must specify from_stream_name parameter")
        self.assertIn("to_stream_name", prompt,
                      "SYNTH_PROMPT must specify to_stream_name parameter")
        self.assertIn("never ids", prompt.lower(),
                      "SYNTH_PROMPT must warn against using IDs")


# ─────────────────────────────────────────────────────────────────────────────
# Bug 1C — _get_stream school scoping
# ─────────────────────────────────────────────────────────────────────────────

class TestGetStreamSchoolScoping(unittest.TestCase):

    def test_get_stream_resolves_by_name_in_primary_school(self):
        """
        _get_stream('Humanities') must find the stream in the primary school,
        not a stream with the same name in another school.
        """
        from core.admin_agent import AdminActionExecutor
        from core.models import School
        ex = AdminActionExecutor()
        school = School.objects.first()

        # Get the primary school's Humanities stream (school_id = school.id)
        from core.models import Stream
        primary_stream = Stream.objects.filter(name__iexact="Humanities", school=school).first()
        if primary_stream is None:
            self.skipTest("No 'Humanities' stream in primary school to test with")

        result = ex._get_stream("Humanities", school)
        self.assertEqual(result.school_id, school.id,
                         "_get_stream must return the primary school's stream, not another school's")

    def test_get_stream_does_not_return_other_school_stream(self):
        """
        If a stream name exists in two schools, _get_stream must only find
        the one in the specified school.
        """
        from core.admin_agent import AdminActionExecutor
        from core.models import School, Stream
        ex = AdminActionExecutor()
        school = School.objects.first()

        # The DB has STEM in both school 1 and school 5 — verify only school 1 is returned
        other_school_stems = Stream.objects.filter(name__iexact="STEM").exclude(school=school)
        if not other_school_stems.exists():
            self.skipTest("No cross-school duplicate 'STEM' to test with")

        result = ex._get_stream("STEM", school)
        self.assertEqual(result.school_id, school.id,
                         "_get_stream must not match streams from other schools")


# ─────────────────────────────────────────────────────────────────────────────
# Bug 2 — stream list scoped to primary school
# ─────────────────────────────────────────────────────────────────────────────

class TestStreamListSchoolScoping(unittest.TestCase):

    def test_lqr_streams_only_shows_primary_school(self):
        """
        LocalQueryRouter._streams() must only list streams belonging to
        School.objects.first(), not all streams across every school.
        """
        from core.admin_agent_queries import LocalQueryRouter
        from core.models import School, Stream
        router = LocalQueryRouter()
        school = School.objects.first()

        other_school_streams = Stream.objects.exclude(school=school)
        if not other_school_streams.exists():
            self.skipTest("Only one school in DB — cross-school leak cannot occur")

        output = router._streams()
        for s in other_school_streams:
            self.assertNotIn(
                f"id {s.id}",
                output,
                f"Stream '{s.name}' (id {s.id}, school_id {s.school_id}) must NOT appear in primary school stream list",
            )

    def test_full_school_context_streams_scoped_to_school(self):
        """
        AdminDataReader.get_full_school_context() streams list must not include
        streams from other schools.
        """
        from core.admin_agent_queries import AdminDataReader
        from core.models import School, Stream
        reader = AdminDataReader()
        school = School.objects.first()
        ctx = reader.get_full_school_context()

        stream_ids_in_ctx = {s["id"] for s in ctx.get("streams", [])}
        other_ids = set(
            Stream.objects.exclude(school=school).values_list("id", flat=True)
        )

        overlap = stream_ids_in_ctx & other_ids
        self.assertEqual(
            overlap, set(),
            f"Context streams must not include IDs from other schools: {overlap}",
        )

    def test_lqr_answer_streams_scoped(self):
        """
        LocalQueryRouter.answer('get streams') must not mention stream IDs
        that belong to a different school.
        """
        from core.admin_agent_queries import LocalQueryRouter
        from core.models import School, Stream
        router = LocalQueryRouter()
        school = School.objects.first()

        other_school_streams = Stream.objects.exclude(school=school)
        if not other_school_streams.exists():
            self.skipTest("Only one school in DB")

        output = router.answer("get streams") or ""
        for s in other_school_streams:
            self.assertNotIn(
                f"id {s.id}",
                output,
                f"Stream '{s.name}' id {s.id} from school {s.school_id} must not appear",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestReassignParamNormalisation))
    suite.addTests(loader.loadTestsFromTestCase(TestGetStreamSchoolScoping))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamListSchoolScoping))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
