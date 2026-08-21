"""
Live-database query layer for the Admin Engineering Agent.

LocalQueryRouter answers factual admin questions directly from the live Django ORM
without calling any external LLM.  Every query category is a named method so the
agent's tool layer can also call them individually.

New in this version:
  - Full schema introspection (tables, columns, FK map)
  - Rich relationship-aware student queries
  - Route/view/source inspection hooks
  - Backend health diagnostics with severity scoring
  - build_llm_context_blob() produces the full JSON context injected into the LLM
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models import Avg, Count, Q, Sum
from django.urls import get_resolver
from django.utils import timezone

from .models import (
    AcademicTerm,
    DisciplineCategory,
    DisciplineReport,
    GradeLevel,
    Notification,
    PasswordReset,
    School,
    Stream,
    Student,
    TeacherProfile,
    UserSession,
)


# ─────────────────────────────────────────────────────────────────────────────
# Tiny helpers
# ─────────────────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _lines(title: str, rows: list, empty: str = "None found.") -> str:
    parts = [title]
    parts.extend(rows if rows else [empty])
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# AdminDataReader — rich read-only snapshots of every operational table
# ─────────────────────────────────────────────────────────────────────────────

class AdminDataReader:
    """Read-only snapshots of every operational table."""

    def school(self):
        return School.objects.first()

    def get_full_school_context(self):
        try:
            school = self.school()
            school_info = {
                "name": school.name if school else "Unknown",
                "short_name": getattr(school, "short_name", "") if school else "",
                "motto": school.motto if school else "",
                "current_year": school.current_year if school else "",
                "phone": school.phone if school else "",
                "email": school.email if school else "",
                "address": school.address if school else "",
                "allow_teacher_registration": bool(
                    school.allow_teacher_registration if school else False
                ),
                "require_teacher_approval": bool(
                    school.require_teacher_approval if school else False
                ),
            }
            # Scope streams to the primary school to avoid cross-school leakage
            streams = list(
                Stream.objects.filter(school=school, is_active=True).values("id", "name", "code")
                if school else
                Stream.objects.filter(is_active=True).values("id", "name", "code")
            )
            total_students = Student.objects.filter(is_active=True).count()
            critical = Student.objects.filter(is_active=True, risk_level="CRITICAL").count()
            warning = Student.objects.filter(is_active=True, risk_level="WARNING").count()
            good = Student.objects.filter(is_active=True, risk_level="GOOD").count()
            total_reports = DisciplineReport.objects.count()
            total_teachers = (
                User.objects.filter(groups__name__in=["ClassTeacher", "Teacher"])
                .distinct()
                .count()
            )
            categories = list(
                DisciplineCategory.objects.filter(is_active=True).values("id", "key", "name")
            )
            return {
                "school": school_info,
                "streams": streams,
                "students": {
                    "total": total_students,
                    "critical": critical,
                    "warning": warning,
                    "good": good,
                },
                "total_reports": total_reports,
                "total_teachers": total_teachers,
                "categories": categories,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_students_for_context(self, limit: int = 80):
        try:
            return list(
                Student.objects.filter(is_active=True)
                .select_related("stream")
                .order_by("-risk_score")[:limit]
                .values(
                    "id", "name", "admission_number", "stream__name",
                    "form", "year", "risk_score", "risk_level", "optional_notes",
                )
            )
        except Exception:
            return []

    def get_teachers_for_context(self):
        try:
            teachers = []
            for p in TeacherProfile.objects.select_related("user", "assigned_stream").all():
                teachers.append({
                    "id": p.user.id,
                    "username": p.user.username,
                    "name": p.user.get_full_name() or p.user.username,
                    "email": p.user.email,
                    "stream": p.assigned_stream.name if p.assigned_stream else None,
                    "form": p.assigned_form,
                    "is_approved": p.is_approved,
                    "is_suspended": p.is_suspended,
                    "is_online": p.is_online,
                    "groups": list(p.user.groups.values_list("name", flat=True)),
                })
            return teachers
        except Exception:
            return []

    def table_inventory(self) -> dict:
        """Row counts for every operational table the agent can read."""
        return {
            "school": School.objects.count(),
            "streams": Stream.objects.count(),
            "active_streams": Stream.objects.filter(is_active=True).count(),
            "grade_levels": GradeLevel.objects.count(),
            "academic_terms": AcademicTerm.objects.count(),
            "students": Student.objects.count(),
            "active_students": Student.objects.filter(is_active=True).count(),
            "discipline_categories": DisciplineCategory.objects.count(),
            "discipline_reports": DisciplineReport.objects.count(),
            "users": User.objects.count(),
            "teacher_profiles": TeacherProfile.objects.count(),
            "groups": Group.objects.count(),
            "user_sessions": UserSession.objects.count(),
            "active_sessions": UserSession.objects.filter(is_active=True).count(),
            "notifications": Notification.objects.count(),
            "password_resets": PasswordReset.objects.count(),
        }

    def db_schema_summary(self) -> dict:
        """Live table schema via Django introspection."""
        try:
            from django.db import connection
            tables = connection.introspection.table_names()
            schema = {}
            with connection.cursor() as cursor:
                for table in tables:
                    try:
                        desc = connection.introspection.get_table_description(cursor, table)
                        schema[table] = [
                            {"name": c.name, "type": str(c.type_code), "null": c.null_ok}
                            for c in desc
                        ]
                    except Exception:
                        schema[table] = []
            return {"tables": tables, "schema": schema}
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# LocalQueryRouter — answers factual questions without an LLM call
# ─────────────────────────────────────────────────────────────────────────────

class LocalQueryRouter:
    """
    Answers factual admin questions from the live database without calling
    an external LLM.  Returns None when the message is a write command or
    needs model reasoning.
    """

    WRITE_RE = re.compile(
        r"\b(add|create|delete|remove|rename|update|change name|set the|approve|suspend|"
        r"unsuspend|reset password|import|recalculate|deactivate|assign|ban|fix|patch|"
        r"repair|modify|edit)\b",
        re.I,
    )

    def __init__(self):
        self.reader = AdminDataReader()

    # ── Public entry point ────────────────────────────────────────────────────

    def answer(self, message: str) -> str | None:
        n = _norm(message)
        if not n:
            return None

        # Greetings
        if n in {"hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"}:
            return self._greeting()

        # Write commands → pass to LLM
        if self.WRITE_RE.search(n) and not self._is_pure_read(n):
            return None

        # ── Route matching ────────────────────────────────────────────────────

        # System / health
        if self._match(n, ["health", "diagnos", "debug", "system status", "backend status", "backend health"]):
            return self._diagnostics()
        if self._match(n, ["error log", "recent error", "traceback", "show errors", "latest error"]):
            return self._error_logs()
        if self._match(n, ["route", "url", "endpoint", "urlpattern", "list route"]):
            return self._routes()
        if self._match(n, ["table", "schema", "database inventory", "all tables", "db schema"]):
            return self._tables()
        if self._match(n, ["app manifest", "application manifest", "source tree", "source files"]):
            return self._app_manifest_summary()

        # School identity
        if (
            self._match(n, ["school name", "name of the school", "name of this school",
                            "name of this system", "name of the system", "this system", "which school"])
            and not self._match(n, ["teacher", "student", "report", "stream"])
        ):
            return self._school_identity()

        # School stats / overview
        if self._match(n, ["school statistic", "dashboard stat", "overview", "summary", "school overview"]):
            return self._school_stats()

        # Teachers
        if (
            self._match(n, ["how many teacher", "number of teacher", "count teacher"])
            or n in {"teachers", "list teachers", "list all teachers", "show teachers",
                     "show all teachers", "all teachers"}
        ):
            return self._teachers(count_only=("how many" in n or "number of" in n or "count" in n))
        if self._match(n, ["list teacher", "show teacher", "all teacher"]):
            return self._teachers(count_only=False)
        if self._match(n, ["pending approval", "unapproved teacher", "awaiting approval"]):
            return self._pending_teachers()
        if self._match(n, ["suspended teacher"]):
            return self._suspended_teachers()
        if self._match(n, ["online teacher", "who is online"]):
            return self._sessions()

        # Streams
        if self._match(n, ["stream"]) and not self._match(n, ["student in stream"]):
            return self._streams()

        # Grade / term
        if self._match(n, ["grade", "form level"]):
            return self._grades()
        if self._match(n, ["term", "academic term"]):
            return self._terms()

        # Categories
        if self._match(n, ["categor"]):
            return self._categories()

        # Password resets
        if self._match(n, ["password reset", "reset request"]):
            return self._resets()

        # Notifications
        if self._match(n, ["notification"]):
            return self._notifications()

        # Sessions
        if self._match(n, ["session", "active session"]):
            return self._sessions()

        # Risk / critical students
        if self._match(n, ["critical student", "top risk", "highest risk", "at risk"]):
            return self._top_risk()
        if self._match(n, ["warning student"]):
            return self._warning_students()

        # Student counts
        if self._match(n, ["how many student", "number of student", "count student", "student count"]):
            return self._student_count()

        # Students by stream/form
        stream_form_match = re.search(
            r"student[s]?\s+(?:in\s+)?(?:stream\s+)?([a-z0-9 ]+?)(?:\s+form\s+(\d+))?$", n
        )
        if stream_form_match and self._match(n, ["student"]):
            stream_hint = stream_form_match.group(1).strip()
            form_hint = stream_form_match.group(2)
            return self._students_by_stream_form(stream_hint, form_hint)

        # General student list
        if self._match(n, ["list student", "show student", "all student"]):
            return self._students()

        # Reports
        if self._match(n, ["how many report", "number of report", "count report"]):
            return self._reports(count_only=True)
        if (
            self._match(n, ["list report", "show report", "all report", "discipline report",
                            "generate discipline", "recent report"])
            or n in {"reports", "list reports", "show reports"}
        ):
            return self._reports(count_only=False)

        # Cross-table relationship queries
        if self._match(n, ["discipline case", "disciplinary case", "disciplinary record"]):
            return self._students_with_discipline()
        if self._match(n, ["most reported", "most discipline", "most offence", "most offense"]):
            return self._most_reported_students()
        if self._match(n, ["no report", "no discipline", "clean record", "no offense"]):
            return self._students_no_reports()

        # Users
        if self._match(n, ["user account", "user list", "all user", "list user", "show user"]):
            return self._users()

        return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _is_pure_read(self, n: str) -> bool:
        return bool(
            re.match(
                r"^(list|show|how many|what|name of|count|display|get|dump|"
                r"analyse|analyze|debug|inspect|find|search|who)\b",
                n,
            )
        )

    def _match(self, n: str, needles: list) -> bool:
        return any(needle in n for needle in needles)

    # ── Response builders ─────────────────────────────────────────────────────

    def _greeting(self) -> str:
        school = self.reader.school()
        ctx = self.reader.get_full_school_context()
        name = school.name if school else "this school"
        students = ctx.get("students", {})
        inv = self.reader.table_inventory()
        return (
            f"Hello. I am the **Admin Engineering Agent** for **{name}**.\n"
            f"I have full read access to your source code, database, logs, and routes — "
            f"and controlled write access to the database and backend code.\n\n"
            f"**Live snapshot:**\n"
            f"- Students: {students.get('total', 0)} "
            f"(🔴 Critical {students.get('critical', 0)}, "
            f"⚠️ Warning {students.get('warning', 0)}, "
            f"✅ Good {students.get('good', 0)})\n"
            f"- Teachers: {ctx.get('total_teachers', 0)}\n"
            f"- Discipline reports: {ctx.get('total_reports', 0)}\n"
            f"- Streams: {len(ctx.get('streams') or [])}\n"
            f"- Tables in DB: {len(inv)}\n\n"
            f"**Try asking:**\n"
            f"- `list all teachers` — live teacher list from DB\n"
            f"- `show critical students` — top risk students\n"
            f"- `backend health` — full system diagnostics\n"
            f"- `debug teacher dashboard 500` — incident investigation\n"
            f"- `inspect route /admin-dashboard/` — view source\n"
            f"- `show recent errors` — latest tracebacks\n"
            f"- Or any write command: `add student`, `approve teacher`, `fix bug in…`"
        )

    def _school_identity(self) -> str:
        school = self.reader.school()
        if not school:
            return "No school record exists yet. Use `update school name = ...` to set it."
        bits = [
            f"**School name:** {school.name}",
            f"**Short name:** {school.short_name or '—'}",
            f"**Motto:** {school.motto or '—'}",
            f"**Year:** {school.current_year}",
            f"**Phone:** {school.phone or '—'}",
            f"**Email:** {school.email or '—'}",
            f"**Address:** {school.address or '—'}",
            f"**Teacher registration:** {'Open' if school.allow_teacher_registration else 'Closed'}",
            f"**Requires approval:** {'Yes' if school.require_teacher_approval else 'No'}",
        ]
        return "**This system is bound to:**\n" + "\n".join(bits)

    def _school_stats(self) -> str:
        ctx = self.reader.get_full_school_context()
        school = ctx.get("school") or {}
        students = ctx.get("students") or {}
        inv = self.reader.table_inventory()
        avg = Student.objects.filter(is_active=True).aggregate(avg=Avg("risk_score"))["avg"] or 0
        pending_approvals = TeacherProfile.objects.filter(is_approved=False, is_suspended=False).count()
        pending_resets    = PasswordReset.objects.filter(status="pending").count()
        return (
            f"**{school.get('name', 'School')} — Live Statistics**\n"
            f"- Active students: **{students.get('total', 0)}**\n"
            f"- Risk breakdown: 🔴 Critical {students.get('critical', 0)} / "
            f"⚠️ Warning {students.get('warning', 0)} / ✅ Good {students.get('good', 0)}\n"
            f"- Average risk score: **{round(avg, 1)}**\n"
            f"- Discipline reports: **{ctx.get('total_reports', 0)}**\n"
            f"- Teachers (DB): **{ctx.get('total_teachers', 0)}**\n"
            f"- Active streams: **{len(ctx.get('streams') or [])}**\n"
            f"- Categories: **{len(ctx.get('categories') or [])}**\n"
            f"- Pending teacher approvals: **{pending_approvals}**\n"
            f"- Pending password resets: **{pending_resets}**\n"
            f"- Active user sessions: **{inv.get('active_sessions', 0)}**\n"
            f"\n**Full table inventory:** {inv}"
        )

    def _teachers(self, count_only: bool = False) -> str:
        qs = (
            User.objects.filter(groups__name__in=["ClassTeacher", "Teacher"])
            .distinct()
            .select_related("teacher_profile")
            .prefetch_related("groups")
            .order_by("first_name", "username")
        )
        staff     = list(qs)
        superusers = list(User.objects.filter(is_superuser=True).order_by("username"))
        if count_only:
            return (
                f"**Teachers in DB (ClassTeacher/Teacher groups):** {len(staff)}\n"
                f"**Admin/Superuser accounts:** {len(superusers)}"
            )
        rows = []
        for u in staff:
            groups = ", ".join(u.groups.values_list("name", flat=True)) or "—"
            try:
                p = u.teacher_profile
                stream = p.assigned_stream.name if p.assigned_stream else "—"
                form   = p.assigned_form or "—"
                status = []
                if not p.is_approved:
                    status.append("⏳ pending")
                if p.is_suspended:
                    status.append("🚫 suspended")
                if p.is_online:
                    status.append("🟢 online")
                status_s = ", ".join(status) or "✅ active"
            except TeacherProfile.DoesNotExist:
                stream = form = "—"
                status_s = "⚠️ no profile"
            rows.append(
                f"- **{u.get_full_name() or u.username}** (@{u.username}) | "
                f"{groups} | {stream} {form} | {status_s}"
            )
        admin_rows = [
            f"- {u.get_full_name() or u.username} (@{u.username}) [superuser]"
            for u in superusers
        ]
        return (
            _lines(f"**Teachers ({len(staff)}) — live from DB:**", rows)
            + "\n\n"
            + _lines(f"**Admins ({len(superusers)}):**", admin_rows)
        )

    def _pending_teachers(self) -> str:
        pending = TeacherProfile.objects.filter(
            is_approved=False, is_suspended=False
        ).select_related("user")
        rows = [
            f"- {p.user.get_full_name() or p.user.username} (@{p.user.username}) "
            f"— registered {p.user.date_joined.strftime('%Y-%m-%d')}"
            for p in pending
        ]
        return _lines(f"**Pending teacher approvals ({pending.count()}):**", rows)

    def _suspended_teachers(self) -> str:
        susp = TeacherProfile.objects.filter(is_suspended=True).select_related("user")
        rows = [
            f"- {p.user.username} | Reason: {p.suspension_reason or 'none'} | "
            f"Suspended: {p.suspended_at.strftime('%Y-%m-%d') if p.suspended_at else '—'}"
            for p in susp
        ]
        return _lines(f"**Suspended teachers ({susp.count()}):**", rows)

    def _streams(self) -> str:
        school = self.reader.school()
        qs = Stream.objects.filter(school=school) if school else Stream.objects.all()
        rows = []
        for s in qs.order_by("name"):
            count = s.students.filter(is_active=True).count()
            flag  = "✅ active" if s.is_active else "❌ inactive"
            rows.append(
                f"- **{s.name}** (code: {s.code or '—'}, id {s.id}, {flag}) — "
                f"{count} active student(s)"
            )
        return _lines(f"**Streams in DB ({qs.count()}):**", rows)

    def _grades(self) -> str:
        rows = [
            f"- {g.name} (code {g.code}, order {g.order}, "
            f"{'active' if g.is_active else 'inactive'})"
            for g in GradeLevel.objects.all().order_by("order", "name")
        ]
        return _lines("**Grade levels:**", rows)

    def _terms(self) -> str:
        rows = []
        for t in AcademicTerm.objects.all().order_by("-year", "-term_number"):
            cur = " ⭐ current" if t.is_current else ""
            rows.append(
                f"- {t.name} {t.year} (term {t.term_number}) "
                f"{t.start_date} → {t.end_date}{cur}"
            )
        return _lines("**Academic terms:**", rows)

    def _categories(self) -> str:
        rows = [
            f"- **{c.name}** [{c.key}] rating={c.default_rating} "
            f"weight={c.risk_weight} severity={c.severity_level}"
            for c in DisciplineCategory.objects.filter(is_active=True).order_by("order", "name")
        ]
        return _lines("**Active discipline categories:**", rows)

    def _student_count(self) -> str:
        total    = Student.objects.filter(is_active=True).count()
        inactive = Student.objects.filter(is_active=False).count()
        by_stream = (
            Student.objects.filter(is_active=True)
            .values("stream__name")
            .annotate(n=Count("id"))
            .order_by("stream__name")
        )
        lines = [
            f"**Active students:** {total}",
            f"**Inactive/deactivated:** {inactive}",
            "**By stream:**",
        ]
        for row in by_stream:
            lines.append(f"  - {row['stream__name'] or '—'}: {row['n']}")
        by_form = (
            Student.objects.filter(is_active=True)
            .values("form")
            .annotate(n=Count("id"))
            .order_by("form")
        )
        lines.append("**By form:**")
        for row in by_form:
            lines.append(f"  - {row['form'] or '—'}: {row['n']}")
        return "\n".join(lines)

    def _students(self, limit: int = 80) -> str:
        qs = (
            Student.objects.filter(is_active=True)
            .select_related("stream")
            .order_by("name")[:limit]
        )
        rows = [
            f"- **{s.name}** #{s.admission_number} | "
            f"{s.stream.name if s.stream else '—'} {s.form} | "
            f"risk {s.risk_score} {s.risk_level}"
            for s in qs
        ]
        extra = Student.objects.filter(is_active=True).count() - len(rows)
        text  = _lines(f"**Students (showing up to {len(rows)}):**", rows)
        if extra > 0:
            text += f"\n…and {extra} more. Try `students in <stream> form <N>` to filter."
        return text

    def _students_by_stream_form(self, stream_hint: str, form_hint: str | None) -> str:
        """Filter students by stream name hint and optional form number."""
        try:
            qs = Student.objects.filter(is_active=True).select_related("stream")
            # Stream filter — fuzzy name match
            if stream_hint:
                qs = qs.filter(stream__name__icontains=stream_hint)
            # Form filter
            if form_hint:
                form_str = f"Form {form_hint}"
                qs = qs.filter(form=form_str)
            qs = qs.order_by("name")[:100]
            rows = [
                f"- **{s.name}** #{s.admission_number} | "
                f"{s.stream.name if s.stream else '—'} {s.form} | "
                f"risk {s.risk_score} {s.risk_level}"
                for s in qs
            ]
            filter_desc = (
                (f"stream ~'{stream_hint}'" if stream_hint else "")
                + (" " if stream_hint and form_hint else "")
                + (f"Form {form_hint}" if form_hint else "")
            ) or "all"
            return _lines(
                f"**Students matching [{filter_desc}] ({len(rows)} found):**", rows
            )
        except Exception as e:
            return f"Query error: {e}"

    def _top_risk(self, limit: int = 25) -> str:
        qs = (
            Student.objects.filter(is_active=True)
            .exclude(risk_level="GOOD")
            .select_related("stream")
            .order_by("-risk_score")[:limit]
        )
        rows = [
            f"- **{s.name}** #{s.admission_number} | "
            f"{s.stream.name if s.stream else '—'} {s.form} | "
            f"score={s.risk_score} {s.risk_level} | "
            f"reports={s.reports.count()}"
            for s in qs
        ]
        return _lines("**Highest-risk students (live risk_score, non-GOOD):**", rows, "No warning/critical students.")

    def _warning_students(self) -> str:
        qs = (
            Student.objects.filter(is_active=True, risk_level="WARNING")
            .select_related("stream")
            .order_by("-risk_score")[:50]
        )
        rows = [
            f"- **{s.name}** #{s.admission_number} | {s.stream.name if s.stream else '—'} {s.form} | score={s.risk_score}"
            for s in qs
        ]
        return _lines(f"**Warning-level students ({qs.count()}):**", rows)

    def _students_with_discipline(self) -> str:
        """Students who have at least one discipline report."""
        qs = (
            Student.objects.filter(is_active=True)
            .annotate(report_count=Count("reports"))
            .filter(report_count__gt=0)
            .select_related("stream")
            .order_by("-report_count")[:60]
        )
        rows = [
            f"- **{s.name}** #{s.admission_number} | {s.stream.name if s.stream else '—'} "
            f"{s.form} | {s.report_count} report(s) | risk {s.risk_level}"
            for s in qs
        ]
        total = Student.objects.filter(is_active=True).annotate(rc=Count("reports")).filter(rc__gt=0).count()
        return _lines(f"**Students with discipline records ({total} total, showing {len(rows)}):**", rows)

    def _most_reported_students(self, limit: int = 20) -> str:
        qs = (
            Student.objects.filter(is_active=True)
            .annotate(n=Count("reports"), pts=Sum("reports__points"))
            .filter(n__gt=0)
            .select_related("stream")
            .order_by("-n")[:limit]
        )
        rows = [
            f"- **{s.name}** #{s.admission_number} | {s.n} report(s), {s.pts or 0} pts | "
            f"{s.stream.name if s.stream else '—'} {s.form}"
            for s in qs
        ]
        return _lines(f"**Most-reported students (top {limit}):**", rows)

    def _students_no_reports(self) -> str:
        qs = (
            Student.objects.filter(is_active=True)
            .annotate(n=Count("reports"))
            .filter(n=0)
            .select_related("stream")
            .order_by("name")[:80]
        )
        rows = [
            f"- {s.name} #{s.admission_number} | {s.stream.name if s.stream else '—'} {s.form}"
            for s in qs
        ]
        return _lines(f"**Students with no discipline records ({len(rows)}):**", rows)

    def _reports(self, count_only: bool = False, limit: int = 40) -> str:
        total = DisciplineReport.objects.count()
        if count_only:
            today = DisciplineReport.objects.filter(
                reported_at__date=timezone.now().date()
            ).count()
            return (
                f"**Discipline reports in DB:** {total}\n"
                f"**Filed today:** {today}"
            )
        qs = (
            DisciplineReport.objects.select_related("student", "category", "reported_by")
            .order_by("-reported_at")[:limit]
        )
        rows = [
            f"- #{r.id} {r.reported_at.strftime('%Y-%m-%d %H:%M')} | "
            f"**{r.student.name}** #{r.student.admission_number} | "
            f"{r.category_name} | {r.get_rating_display()} +{r.points} pts | "
            f"by {r.reported_by.get_full_name() or r.reported_by.username}"
            for r in qs
        ]
        by_cat = (
            DisciplineReport.objects.values("category_name")
            .annotate(n=Count("id"), pts=Sum("points"))
            .order_by("-n")[:12]
        )
        cat_lines = [
            f"- {row['category_name']}: {row['n']} reports, {row['pts'] or 0} pts"
            for row in by_cat
        ]
        extra = total - len(rows)
        text  = _lines(f"**Latest discipline reports ({min(limit, total)} of {total}):**", rows)
        text += "\n\n" + _lines("**By category:**", cat_lines)
        if extra > 0:
            text += f"\n\n…{extra} older report(s) not listed."
        return text

    def _resets(self) -> str:
        pending = PasswordReset.objects.filter(status="pending").select_related("user")
        rows = [
            f"- {r.user.username} requested {r.requested_at.strftime('%Y-%m-%d %H:%M')} [{r.status}]"
            for r in pending
        ]
        return _lines(f"**Pending password resets ({pending.count()}):**", rows)

    def _notifications(self, limit: int = 20) -> str:
        qs = Notification.objects.order_by("-created_at")[:limit]
        rows = [
            f"- {n.created_at.strftime('%Y-%m-%d %H:%M')} [{n.notification_type}] "
            f"**{n.title}** (read={n.is_read})"
            for n in qs
        ]
        return _lines(f"**Recent notifications ({Notification.objects.count()} total):**", rows)

    def _sessions(self) -> str:
        online = TeacherProfile.objects.filter(is_online=True).select_related("user")
        rows = [
            f"- {p.user.get_full_name() or p.user.username} (@{p.user.username}) "
            f"last activity {p.last_activity}"
            for p in online
        ]
        active = UserSession.objects.filter(is_active=True).count()
        text = _lines(f"**Teachers flagged online ({online.count()}):**", rows, "Nobody currently marked online.")
        return text + f"\n**Active UserSession rows:** {active}"

    def _users(self) -> str:
        rows = []
        for u in User.objects.all().order_by("username")[:80]:
            groups = ", ".join(u.groups.values_list("name", flat=True)) or "—"
            flags  = []
            if u.is_superuser:
                flags.append("admin")
            if not u.is_active:
                flags.append("banned")
            rows.append(
                f"- **{u.username}** ({u.get_full_name() or 'no name'}) | "
                f"{groups} | {', '.join(flags) or 'user'}"
            )
        extra = User.objects.count() - len(rows)
        text  = _lines(f"**User accounts ({User.objects.count()}):**", rows)
        if extra > 0:
            text += f"\n…and {extra} more."
        return text

    def _tables(self) -> str:
        inv  = self.reader.table_inventory()
        rows = [f"- **{name}**: {count} row(s)" for name, count in inv.items()]
        try:
            schema = self.reader.db_schema_summary()
            all_tables = schema.get("tables", [])
            rows.append(f"\n**Raw DB tables ({len(all_tables)}):** " + ", ".join(all_tables[:30]))
        except Exception:
            pass
        return _lines("**Live table inventory (Django models):**", rows)

    def _routes(self) -> str:
        rows = []
        try:
            resolver = get_resolver()
            def _collect(pattern, prefix=""):
                try:
                    pfx = prefix + str(pattern.pattern)
                except Exception:
                    pfx = prefix
                if hasattr(pattern, "url_patterns"):
                    for child in pattern.url_patterns:
                        _collect(child, pfx)
                    return
                name = getattr(pattern, "name", None) or ""
                cb   = getattr(pattern.callback, "__name__", "") if hasattr(pattern, "callback") else ""
                rows.append(f"- `/{pfx.lstrip('/')}`  [{name}]  → {cb}")
            for pat in resolver.url_patterns:
                _collect(pat)
        except Exception as e:
            return f"Could not inspect URL routes: {e}"
        return _lines(f"**Application URL routes ({len(rows)}):**", rows[:120])

    def _error_logs(self, max_chars: int = 6000) -> str:
        log_file = Path(settings.BASE_DIR) / "error_logs.txt"
        if not log_file.exists():
            return "No `error_logs.txt` file yet — Django has not recorded an application error."
        try:
            text = log_file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return f"Could not read error logs: {e}"
        if not text.strip():
            return "Error log is empty — no errors recorded."
        snippet = text[-max_chars:]
        return "**Latest application errors from `error_logs.txt`:**\n```\n" + snippet + "\n```"

    def _diagnostics(self) -> str:
        inv    = self.reader.table_inventory()
        issues = []

        dup_adm = (
            Student.objects.values("admission_number")
            .annotate(n=Count("id"))
            .filter(n__gt=1)
        )
        if dup_adm.exists():
            dupes = ", ".join(d["admission_number"] for d in dup_adm[:10])
            issues.append(f"🔴 **DUPLICATE admission numbers:** {dupes}")

        school = self.reader.school()
        active_streams_qs = (
            Stream.objects.filter(school=school, is_active=True)
            if school else Stream.objects.filter(is_active=True)
        )
        empty_streams = [
            s.name for s in active_streams_qs
            if not s.students.filter(is_active=True).exists()
        ]
        if empty_streams:
            issues.append(f"⚠️ **Active streams with no students:** {', '.join(empty_streams)}")

        unapproved = TeacherProfile.objects.filter(is_approved=False, is_suspended=False).count()
        if unapproved:
            issues.append(f"⚠️ **{unapproved} teacher profile(s) pending approval**")

        pending_resets = PasswordReset.objects.filter(status="pending").count()
        if pending_resets:
            issues.append(f"ℹ️ **{pending_resets} pending password reset(s)**")

        stale_online = TeacherProfile.objects.filter(is_online=True).count()
        if stale_online:
            issues.append(
                f"ℹ️ **{stale_online} profile(s) flagged online** (may be stale after crash/logout)"
            )

        stale_critical = Student.objects.filter(
            is_active=True, risk_level="CRITICAL", last_incident_date__isnull=True
        ).count()
        if stale_critical:
            issues.append(
                f"⚠️ **{stale_critical} student(s) CRITICAL risk but no last_incident_date** — run recalculate_risk"
            )

        form_counts = Counter(
            Student.objects.filter(is_active=True).values_list("form", flat=True)
        )
        issue_text = "\n".join(issues) if issues else "✅ No data-integrity issues detected."

        return (
            f"**Backend Diagnostics — {timezone.now().strftime('%Y-%m-%d %H:%M')}**\n\n"
            f"**Checks:**\n{issue_text}\n\n"
            f"**Students by form:** {dict(sorted(form_counts.items()))}\n\n"
            f"**Table row counts:**\n"
            + "\n".join(f"- {k}: {v}" for k, v in inv.items())
            + "\n\nFor tracebacks run `show recent errors`. For URL routes run `list routes`."
        )

    def _app_manifest_summary(self) -> str:
        """Quick summary of the application structure."""
        try:
            from django.apps import apps as django_apps
            models_count = sum(1 for app in django_apps.get_app_configs() for _ in app.get_models())
            routes_count = 0
            def _count(pat):
                nonlocal routes_count
                if hasattr(pat, "url_patterns"):
                    for c in pat.url_patterns:
                        _count(c)
                else:
                    routes_count += 1
            for pat in get_resolver().url_patterns:
                _count(pat)

            base = Path(settings.BASE_DIR)
            py_files = [
                p for p in base.rglob("*.py")
                if not any(s in str(p) for s in [".git", "__pycache__", ".venv", "venv", "migrations"])
            ]
            html_files = [
                p for p in base.rglob("*.html")
                if not any(s in str(p) for s in [".git", "__pycache__", ".venv", "venv"])
            ]
            return (
                f"**Application Manifest**\n"
                f"- Backend: Django\n"
                f"- Models: {models_count}\n"
                f"- URL routes: {routes_count}\n"
                f"- Python source files: {len(py_files)}\n"
                f"- HTML templates: {len(html_files)}\n"
                f"- Core app: `core/` — views, models, urls, middleware\n"
                f"- Settings: `disciplinary_program/settings.py`\n\n"
                f"Ask `inspect route /url/`, `show recent errors`, or `read file core/views.py` for details."
            )
        except Exception as e:
            return f"Manifest error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# build_llm_context_blob — full JSON injected into the LLM system prompt
# ─────────────────────────────────────────────────────────────────────────────

def build_llm_context_blob(limit_students: int = 80) -> dict:
    reader = AdminDataReader()
    ctx    = reader.get_full_school_context()
    return {
        "school_context": ctx,
        "table_counts": reader.table_inventory(),
        "students_sample": reader.get_students_for_context(limit=limit_students),
        "teachers": reader.get_teachers_for_context(),
        "recent_reports": list(
            DisciplineReport.objects.select_related("student", "reported_by")
            .order_by("-reported_at")[:25]
            .values(
                "id", "category_name", "rating", "points", "reported_at",
                "student__name", "student__admission_number",
                "reported_by__username",
            )
        ),
        "pending_approvals": list(
            TeacherProfile.objects.filter(is_approved=False).values(
                "user__username", "user__first_name", "user__last_name"
            )[:30]
        ),
        "pending_resets": list(
            PasswordReset.objects.filter(status="pending").values(
                "id", "user__username", "requested_at"
            )[:20]
        ),
        "streams_all": list(Stream.objects.values("id", "name", "code", "is_active")),
        "grades": list(GradeLevel.objects.values("id", "name", "code", "is_active")),
        "instruction": (
            "You MUST answer using this live database snapshot. "
            "This school is whatever school.name says. "
            "Never ask which school or city. Never invent teachers or reports. "
            "If a list is in this JSON, use it. "
            "If a field is missing, say it is not in the database."
        ),
    }
