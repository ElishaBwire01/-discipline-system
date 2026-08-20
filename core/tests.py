import pandas as pd
from django.test import TestCase

from core.ai_chat import PollinationAIChat
from core.views import build_upload_summary, extract_from_excel
from core.models import Student, Stream


class AiTruthfulnessTests(TestCase):
    def test_missing_student_record_returns_data_unavailable(self):
        client = PollinationAIChat()
        result = client.chat("Show me student 999999")

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("mode"), "data_unavailable")
        response = (result.get("response") or "").lower()
        self.assertIn("data unavailable", response)
        self.assertNotIn("admission:", response)

    def test_missing_stats_request_returns_data_unavailable(self):
        client = PollinationAIChat()
        result = client.chat("How many students are in the system?")

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("mode"), "data_unavailable")
        response = (result.get("response") or "").lower()
        self.assertIn("data unavailable", response)
        self.assertNotIn("total students:", response)

    def test_extract_from_excel_infers_higher_forms_and_streams(self):
        df = pd.DataFrame(
            [
                ["Alice Akinyi", "1001", "Grade 8", "Science"],
                ["Brian Otieno", "1002", "Form 10", "Humanities"],
            ],
            columns=["Name", "Admission", "Grade", "Stream"],
        )

        rows = extract_from_excel(df, known_streams=["Science", "Humanities"], known_grades=["Form 8", "Form 10"])

        self.assertEqual(rows[0]["grade"], "Form 8")
        self.assertEqual(rows[0]["stream"], "Science")
        self.assertEqual(rows[1]["grade"], "Form 10")
        self.assertEqual(rows[1]["stream"], "Humanities")

    def test_extract_from_excel_infers_form_without_explicit_grade_keyword(self):
        df = pd.DataFrame(
            [["Cynthia Wanjiru", "1003", "8", "STEM"], ["Daniel Kibet", "1004", "Ten", "Art"]],
            columns=["Name", "Admission", "Class", "Section"],
        )

        rows = extract_from_excel(df, known_streams=["STEM", "Art"], known_grades=["Form 8", "Form 10"])

        self.assertEqual(rows[0]["grade"], "Form 8")
        self.assertEqual(rows[1]["grade"], "Form 10")
        self.assertEqual(rows[0]["stream"], "STEM")
        self.assertEqual(rows[1]["stream"], "Art")

    def test_build_upload_summary_reports_preview_and_duplicates(self):
        rows = [
            {"admission": "1001", "name": "Alice Akinyi", "grade": "Form 8", "stream": "STEM"},
            {"admission": "1001", "name": "Alice Akinyi Duplicate", "grade": "Form 8", "stream": "STEM"},
            {"admission": "1002", "name": "Brian Otieno", "grade": "Form 10", "stream": "Humanities"},
        ]

        summary = build_upload_summary(rows)

        self.assertEqual(summary["total_rows"], 3)
        self.assertEqual(summary["duplicate_admission_count"], 1)
        self.assertEqual(summary["unique_admissions"], 2)
        self.assertEqual(len(summary["preview_rows"]), 3)
        self.assertEqual(summary["preview_rows"][0]["admission"], "1001")

    def test_follow_up_names_returned_when_db_has_students(self):
        # Create streams and students in test DB
        s_stem = Stream.objects.create(name="STEM")
        s_hum = Stream.objects.create(name="Humanities")

        Student.objects.create(admission_number="TEST001", name="John Doe", stream=s_stem, form="Form 1")
        Student.objects.create(admission_number="TEST002", name="Jane Roe", stream=s_hum, form="Form 2")
        Student.objects.create(admission_number="1001", name="Alice Akinyi", stream=s_stem, form="Form 8")
        Student.objects.create(admission_number="1002", name="Brian Otieno", stream=s_hum, form="Form 10")

        client = PollinationAIChat()

        # Stub provider calls to avoid external network and force DB-derived fallback
        client._call_providers_in_order = lambda messages, provider_order=None: {"success": False, "error": "stubbed"}

        res1 = client.chat("How many students are in the system?")
        self.assertTrue(res1.get("success"))
        # should mention students count in fallback
        self.assertIn("students", (res1.get("response") or "").lower())

        conv = [
            {"role": "user", "content": "How many students are in the system?"},
            {"role": "assistant", "content": res1.get("response", "")},
        ]

        res2 = client.chat("What are their names?", conversation_history=conv)
        self.assertTrue(res2.get("success"))
        resp = (res2.get("response") or "").lower()
        self.assertIn("john doe", resp)
        self.assertIn("jane roe", resp)
        self.assertIn("alice akinyi", resp)
        self.assertIn("brian otieno", resp)
