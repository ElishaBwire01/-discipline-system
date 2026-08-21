# core/admin_agent.py
"""
Admin Engineering Agent — a full-stack AI-controlled engineering layer over the
entire application: database → backend source → APIs/routes → services → logs.

Architecture:
  AdminAgent (orchestrator)
    ├── EngineeringToolkit   (tool bus — every capability is an explicit tool)
    ├── AdminActionExecutor  (confirmed write operations on the DB)
    ├── AdminDataReader      (read-only DB snapshots)
    └── LocalQueryRouter     (offline answers for factual questions, no LLM needed)

Operating Modes
  INSPECT  — read everything, modify nothing
  ANALYSIS — investigate relationships, root-cause problems
  REPAIR   — propose and execute code/data fixes (with confirmation)
  TEST     — run management commands, checks, diagnostics
  INCIDENT — analyze errors, 4xx/5xx, slow queries, data anomalies

Permission gates (all write tools require confirmation from the admin):
  DB reads          ✅ always allowed
  DB writes         ⚠️ confirmation gate
  Source reads      ✅ always allowed
  apply_patch       ⚠️ confirmation gate
  create/delete file⚠️ confirmation gate
"""

from __future__ import annotations

import ast
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from textwrap import dedent

logger = logging.getLogger("core.admin_agent")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _now():
    try:
        from django.utils import timezone
        return timezone.now()
    except Exception:
        from datetime import timezone as dt_tz
        return datetime.now(dt_tz.utc)


def _safe_str(val, max_len: int = 200) -> str:
    if val is None:
        return ""
    return str(val)[:max_len].strip()


def _base_dir() -> Path:
    try:
        from django.conf import settings
        return Path(settings.BASE_DIR)
    except Exception:
        return Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# EngineeringToolkit — every capability exposed to the AI as a named tool
# ─────────────────────────────────────────────────────────────────────────────

class EngineeringToolkit:
    """
    All tools the agent may call.  Each method returns a dict:
      {"ok": bool, "output": str, "data": any}

    READ tools are always executed automatically.
    WRITE tools (prefixed _exec_) are gated — the frontend must confirm them.
    """

    MAX_FILE_BYTES = 80_000   # ~80 KB cap when reading source files
    MAX_LOG_CHARS  = 8_000

    # ── APPLICATION MANIFEST ─────────────────────────────────────────────────

    def app_manifest(self) -> dict:
        """Generate a live map of the entire application structure."""
        try:
            from django.urls import get_resolver
            from django.apps import apps as django_apps
            base = _base_dir()

            # Models
            models_info = []
            for app_config in django_apps.get_app_configs():
                for model in app_config.get_models():
                    fields = [
                        {
                            "name": f.name,
                            "type": f.get_internal_type(),
                            "null": getattr(f, "null", False),
                            "unique": getattr(f, "unique", False),
                        }
                        for f in model._meta.get_fields()
                        if hasattr(f, "get_internal_type")
                    ]
                    related = [
                        {"field": f.name, "to": str(f.related_model.__name__), "type": f.get_internal_type()}
                        for f in model._meta.get_fields()
                        if hasattr(f, "related_model") and f.related_model and hasattr(f, "get_internal_type")
                    ]
                    models_info.append({
                        "app": app_config.name,
                        "model": model.__name__,
                        "table": model._meta.db_table,
                        "fields": fields,
                        "relations": related,
                    })

            # Routes
            routes = []
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
                cb = getattr(pattern.callback, "__name__", "") if hasattr(pattern, "callback") else ""
                routes.append({"url": "/" + pfx.lstrip("/"), "name": name, "view": cb})

            for pat in get_resolver().url_patterns:
                _collect(pat)

            # Source tree summary — skip symlinks and unreadable paths (e.g. venv/lib64 on Windows)
            source_files = []
            for ext in ["*.py", "*.html"]:
                for p in base.rglob(ext):
                    try:
                        if p.is_symlink():
                            continue
                        if any(skip in str(p) for skip in [".git", "__pycache__", ".venv", "venv", "migrations", "staticfiles"]):
                            continue
                        source_files.append(str(p.relative_to(base)))
                    except (OSError, PermissionError):
                        continue

            # Settings snapshot (safe subset)
            settings_info = {}
            try:
                from django.conf import settings as dj_settings
                settings_info = {
                    "DEBUG": dj_settings.DEBUG,
                    "DATABASES": {k: {"ENGINE": v.get("ENGINE")} for k, v in dj_settings.DATABASES.items()},
                    "INSTALLED_APPS": list(dj_settings.INSTALLED_APPS),
                    "MIDDLEWARE": list(dj_settings.MIDDLEWARE),
                }
            except Exception:
                pass

            return {
                "ok": True,
                "output": f"Manifest generated: {len(models_info)} models, {len(routes)} routes, {len(source_files)} source files",
                "data": {
                    "backend": "Django",
                    "models": models_info,
                    "routes": routes,
                    "source_files": source_files,
                    "settings": settings_info,
                },
            }
        except Exception as e:
            logger.exception("app_manifest failed")
            return {"ok": False, "output": str(e), "data": {}}

    # ── DATABASE INTELLIGENCE ─────────────────────────────────────────────────

    def db_schema(self) -> dict:
        """Full schema: tables, columns, constraints, indexes, FK map."""
        try:
            from django.db import connection
            tables = connection.introspection.table_names()
            schema = {}
            with connection.cursor() as cursor:
                for table in tables:
                    try:
                        desc = connection.introspection.get_table_description(cursor, table)
                        cols = [
                            {
                                "name": col.name,
                                "type": col.type_code,
                                "null": col.null_ok,
                                "default": col.default,
                            }
                            for col in desc
                        ]
                        schema[table] = {"columns": cols}
                    except Exception:
                        schema[table] = {"columns": []}
            return {
                "ok": True,
                "output": f"Schema dumped: {len(tables)} tables",
                "data": {"tables": tables, "schema": schema},
            }
        except Exception as e:
            return {"ok": False, "output": str(e), "data": {}}

    def db_row_counts(self) -> dict:
        """Row counts for every Django model table."""
        try:
            from django.apps import apps as django_apps
            counts = {}
            for app in django_apps.get_app_configs():
                for model in app.get_models():
                    try:
                        counts[model._meta.db_table] = model.objects.count()
                    except Exception:
                        counts[model._meta.db_table] = "error"
            return {
                "ok": True,
                "output": f"Row counts for {len(counts)} tables",
                "data": counts,
            }
        except Exception as e:
            return {"ok": False, "output": str(e), "data": {}}

    def db_query(self, query: str) -> dict:
        """
        Execute a raw READ-ONLY SQL query (SELECT only).
        Blocked: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
        """
        blocked = re.compile(
            r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|MERGE|EXEC|EXECUTE)\b",
            re.I,
        )
        if blocked.search(query):
            return {"ok": False, "output": "Blocked: only SELECT queries are allowed via db_query.", "data": []}
        try:
            from django.db import connection
            with connection.cursor() as cur:
                cur.execute(query)
                columns = [d[0] for d in cur.description] if cur.description else []
                rows = [dict(zip(columns, row)) for row in cur.fetchall()[:200]]
            return {"ok": True, "output": f"{len(rows)} row(s) returned.", "data": rows}
        except Exception as e:
            return {"ok": False, "output": str(e), "data": []}

    def db_analyze(self, question: str) -> dict:
        """
        Answer a natural-language question about the database by introspecting
        Django models and generating the appropriate ORM answer inline.
        Returns formatted text.
        """
        from core.admin_agent_queries import LocalQueryRouter
        router = LocalQueryRouter()
        answer = router.answer(question)
        if answer:
            return {"ok": True, "output": answer, "data": {}}
        return {"ok": False, "output": "No local answer available — pass to LLM.", "data": {}}

    # ── SOURCE CODE INTELLIGENCE ──────────────────────────────────────────────

    def read_file(self, path: str) -> dict:
        """Read a source file relative to BASE_DIR. Capped at 80 KB."""
        try:
            base = _base_dir()
            full = (base / path).resolve()
            # Security: must stay inside project
            if not str(full).startswith(str(base)):
                return {"ok": False, "output": "Path traversal rejected.", "data": ""}
            if not full.exists():
                return {"ok": False, "output": f"File not found: {path}", "data": ""}
            content = full.read_text(encoding="utf-8", errors="replace")[:self.MAX_FILE_BYTES]
            lines = content.splitlines()
            numbered = "\n".join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
            return {"ok": True, "output": f"Read {len(lines)} lines from {path}", "data": numbered}
        except Exception as e:
            return {"ok": False, "output": str(e), "data": ""}

    def search_code(self, pattern: str, path: str = "", file_ext: str = ".py") -> dict:
        """
        Regex search across source files.  Returns matching lines with file:line context.
        Results are capped at 120 matching LINES.
        If pattern is '.*' or empty (a file-list request), returns a deduplicated file list instead.
        """
        try:
            base = _base_dir()
            root = (base / path).resolve() if path else base
            results = []
            is_file_list = not pattern or pattern.strip() in (".*", "*", "")
            rx = re.compile(pattern if pattern else ".", re.IGNORECASE)
            files_seen = set()
            for fp in root.rglob(f"*{file_ext}"):
                try:
                    if fp.is_symlink():
                        continue
                    if any(skip in str(fp) for skip in [".git", "__pycache__", ".venv", "venv", "migrations"]):
                        continue
                except (OSError, PermissionError):
                    continue
                # File-list mode: just collect file paths, one per file
                if is_file_list:
                    rel = str(fp.relative_to(base))
                    if rel not in files_seen:
                        files_seen.add(rel)
                        results.append(rel)
                        if len(results) >= 200:
                            break
                    continue
                try:
                    for i, line in enumerate(fp.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                        if rx.search(line):
                            results.append(f"{fp.relative_to(base)}:{i}  {line.rstrip()}")
                            if len(results) >= 120:
                                break
                except (OSError, PermissionError, Exception):
                    pass
                if len(results) >= 120:
                    break
            if is_file_list:
                summary = f"Found {len(results)} {file_ext} file(s)"
                return {"ok": True, "output": summary, "data": "\n".join(results) or "(none found)"}
            return {
                "ok": True,
                "output": f"Found {len(results)} match(es) for /{pattern}/",
                "data": "\n".join(results) or "(no matches)",
            }
        except Exception as e:
            return {"ok": False, "output": str(e), "data": ""}

    def inspect_route(self, url_or_name: str) -> dict:
        """Locate a URL route, find its view function, and read the view source."""
        try:
            from django.urls import get_resolver, resolve, Resolver404
            resolver = get_resolver()

            found_view = None
            found_url  = None

            # Try resolving as URL path
            for prefix in ["", "/"]:
                try:
                    match = resolve(prefix + url_or_name.lstrip("/"))
                    found_view = match.func
                    found_url  = url_or_name
                    break
                except (Resolver404, Exception):
                    pass

            # Fallback: scan patterns by name
            if not found_view:
                def _scan(pat, pfx=""):
                    try:
                        p = pfx + str(pat.pattern)
                    except Exception:
                        p = pfx
                    if hasattr(pat, "url_patterns"):
                        for c in pat.url_patterns:
                            r = _scan(c, p)
                            if r:
                                return r
                        return None
                    nm = getattr(pat, "name", None) or ""
                    if url_or_name.lower() in nm.lower() or url_or_name.lower() in p.lower():
                        return pat.callback, p
                    return None
                result = _scan(resolver)
                if result:
                    found_view, found_url = result

            if not found_view:
                return {"ok": False, "output": f"No route matching '{url_or_name}' found.", "data": ""}

            view_name = getattr(found_view, "__name__", str(found_view))
            module    = getattr(found_view, "__module__", "")
            source    = ""
            try:
                import inspect
                source = inspect.getsource(found_view)[:3000]
            except Exception:
                pass

            return {
                "ok": True,
                "output": f"Route: {found_url or url_or_name}  →  {view_name} ({module})",
                "data": {"view": view_name, "module": module, "source": source},
            }
        except Exception as e:
            return {"ok": False, "output": str(e), "data": ""}

    def inspect_model(self, model_name: str) -> dict:
        """Inspect a Django model: fields, relations, constraints, indexes."""
        try:
            from django.apps import apps as django_apps
            model = None
            for app in django_apps.get_app_configs():
                for m in app.get_models():
                    if m.__name__.lower() == model_name.lower():
                        model = m
                        break
                if model:
                    break
            if not model:
                return {"ok": False, "output": f"Model '{model_name}' not found.", "data": {}}

            import inspect
            fields = []
            for f in model._meta.get_fields():
                info = {"name": f.name, "type": type(f).__name__}
                if hasattr(f, "null"):
                    info["null"] = f.null
                if hasattr(f, "unique"):
                    info["unique"] = f.unique
                if hasattr(f, "related_model") and f.related_model:
                    info["related_to"] = f.related_model.__name__
                fields.append(info)

            source = ""
            try:
                source = inspect.getsource(model)[:4000]
            except Exception:
                pass

            return {
                "ok": True,
                "output": f"Model {model.__name__} — {len(fields)} fields",
                "data": {
                    "model": model.__name__,
                    "table": model._meta.db_table,
                    "fields": fields,
                    "source_snippet": source,
                },
            }
        except Exception as e:
            return {"ok": False, "output": str(e), "data": {}}

    def list_routes(self) -> dict:
        """List all URL routes with their view functions."""
        try:
            from django.urls import get_resolver
            routes = []
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
                cb = ""
                if hasattr(pattern, "callback"):
                    cb = getattr(pattern.callback, "__name__", str(pattern.callback))
                routes.append(f"/{pfx.lstrip('/')}  [{name}]  → {cb}")

            for pat in get_resolver().url_patterns:
                _collect(pat)
            return {
                "ok": True,
                "output": f"{len(routes)} routes found",
                "data": "\n".join(routes),
            }
        except Exception as e:
            return {"ok": False, "output": str(e), "data": ""}

    # ── LOGS & DIAGNOSTICS ────────────────────────────────────────────────────

    def read_logs(self, tail_chars: int = 8000) -> dict:
        """Read the application error log."""
        try:
            base = _base_dir()
            log_file = base / "error_logs.txt"
            if not log_file.exists():
                return {"ok": True, "output": "No error_logs.txt found — no errors recorded.", "data": ""}
            content = log_file.read_text(encoding="utf-8", errors="replace")
            snippet = content[-tail_chars:]
            return {"ok": True, "output": f"Last {min(tail_chars, len(content))} chars of error log", "data": snippet}
        except Exception as e:
            return {"ok": False, "output": str(e), "data": ""}

    def parse_tracebacks(self) -> dict:
        """Extract and structure the most recent tracebacks from the error log."""
        log_result = self.read_logs(tail_chars=20000)
        text = log_result.get("data", "")
        blocks = re.split(r"(?=Traceback \(most recent call last\))", text)
        parsed = []
        for block in blocks[-10:]:
            if "Traceback" not in block:
                continue
            lines = block.strip().splitlines()
            exc_line = next((l for l in reversed(lines) if re.match(r"\w+Error|Exception", l.strip())), lines[-1] if lines else "")
            file_lines = [l.strip() for l in lines if "File " in l and ".py" in l]
            parsed.append({
                "exception": exc_line.strip(),
                "files": file_lines[-5:],
                "snippet": block[:800],
            })
        return {
            "ok": True,
            "output": f"Found {len(parsed)} traceback(s)",
            "data": parsed,
        }

    def diagnostics(self) -> dict:
        """Full data-integrity + backend health check."""
        try:
            from django.db.models import Count
            from .models import (
                Student, TeacherProfile, Stream,
                PasswordReset, DisciplineReport, UserSession
            )
            from django.utils import timezone

            issues = []

            # Duplicate admission numbers
            dup = (
                Student.objects.values("admission_number")
                .annotate(n=Count("id"))
                .filter(n__gt=1)
            )
            if dup.exists():
                issues.append({
                    "type": "DUPLICATE_ADMISSION",
                    "detail": [d["admission_number"] for d in dup[:10]],
                    "severity": "HIGH",
                })

            # Active streams with no students
            empty = [
                s.name for s in Stream.objects.filter(is_active=True)
                if not s.students.filter(is_active=True).exists()
            ]
            if empty:
                issues.append({"type": "EMPTY_STREAMS", "detail": empty, "severity": "LOW"})

            # Unapproved teachers
            ua = TeacherProfile.objects.filter(is_approved=False, is_suspended=False).count()
            if ua:
                issues.append({"type": "UNAPPROVED_TEACHERS", "detail": ua, "severity": "MEDIUM"})

            # Pending resets
            pr = PasswordReset.objects.filter(status="pending").count()
            if pr:
                issues.append({"type": "PENDING_RESETS", "detail": pr, "severity": "LOW"})

            # Students with CRITICAL risk but no recent reports (stale risk)
            stale = Student.objects.filter(
                is_active=True, risk_level="CRITICAL", last_incident_date__isnull=True
            ).count()
            if stale:
                issues.append({"type": "STALE_CRITICAL_RISK", "detail": stale, "severity": "MEDIUM"})

            summary = f"{len(issues)} issue(s) detected" if issues else "No data issues detected."
            return {"ok": True, "output": summary, "data": {"issues": issues}}
        except Exception as e:
            return {"ok": False, "output": str(e), "data": {}}

    def run_management_command(self, command: str, args: list | None = None) -> dict:
        """
        Run a safe Django management command (whitelist only).
        Allowed: check, diffsettings, showmigrations, migrate, collectstatic --noinput
        """
        ALLOWED = {
            "check", "diffsettings", "showmigrations",
            "migrate", "collectstatic",
        }
        cmd_name = command.strip().lower().split()[0]
        if cmd_name not in ALLOWED:
            return {
                "ok": False,
                "output": f"Command '{cmd_name}' is not whitelisted. Allowed: {', '.join(sorted(ALLOWED))}",
                "data": "",
            }
        try:
            from django.core.management import call_command
            import io
            out = io.StringIO()
            safe_args = [str(a) for a in (args or [])]
            # Extra safety for collectstatic
            if cmd_name == "collectstatic" and "--noinput" not in safe_args:
                safe_args.append("--noinput")
            call_command(command, *safe_args, stdout=out, stderr=out)
            output = out.getvalue()[:5000]
            return {"ok": True, "output": output or "Command completed.", "data": output}
        except Exception as e:
            return {"ok": False, "output": str(e), "data": ""}

    # ── WRITE TOOLS (require confirmation) ────────────────────────────────────

    def apply_patch(self, path: str, search: str, replace: str, description: str = "") -> dict:
        """
        WRITE — Apply a targeted search-and-replace patch to a source file.
        Returns the pending patch dict for frontend confirmation.
        This method does NOT execute the patch — the executor does.
        """
        return {
            "ok": True,
            "output": f"Patch ready for confirmation: {description or path}",
            "data": {
                "__write_action": True,
                "type": "apply_patch",
                "params": {"path": path, "search": search, "replace": replace},
                "description": description or f"Patch {path}",
            },
        }

    def create_file(self, path: str, content: str, description: str = "") -> dict:
        """WRITE — Create a new file (requires confirmation)."""
        return {
            "ok": True,
            "output": f"Create file ready for confirmation: {path}",
            "data": {
                "__write_action": True,
                "type": "create_file",
                "params": {"path": path, "content": content},
                "description": description or f"Create {path}",
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# AdminActionExecutor — every confirmed DB write + code write goes here
# ─────────────────────────────────────────────────────────────────────────────

class AdminActionExecutor:
    """
    Executes confirmed write actions against the database OR source code.
    Each method returns {"success": bool, "message": str, "data": dict}.
    """

    # ── DB WRITE OPERATIONS ───────────────────────────────────────────────────

    def create_stream(self, name, description="", code=""):
        from .models import Stream, School
        from django.core.cache import cache
        try:
            school = School.objects.first()
            name = _safe_str(name, 50)
            if not name:
                return {"success": False, "message": "Stream name is required."}
            if Stream.objects.filter(name__iexact=name, school=school).exists():
                return {"success": False, "message": f"Stream '{name}' already exists."}
            stream = Stream.objects.create(
                name=name, code=_safe_str(code, 10),
                description=_safe_str(description), school=school, is_active=True,
            )
            cache.delete("active_streams")
            return {"success": True, "message": f"Stream '{stream.name}' created (ID {stream.id}).", "data": {"id": stream.id}}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def bulk_create_streams(self, streams_list):
        results = {"created": [], "skipped": [], "failed": []}
        for s in streams_list:
            r = self.create_stream(name=s.get("name", ""), code=s.get("code", ""), description=s.get("description", ""))
            if r["success"]:
                results["created"].append(s.get("name", "?"))
            elif "already exists" in r.get("message", "").lower():
                results["skipped"].append(s.get("name", "?"))
            else:
                results["failed"].append({"name": s.get("name", "?"), "reason": r["message"]})
        ok, sk = len(results["created"]), len(results["skipped"])
        return {"success": ok > 0 or sk > 0, "message": f"Bulk: {ok} created, {sk} skipped, {len(results['failed'])} failed.", "data": results}

    def _get_stream(self, stream_id_or_name, school=None):
        """Resolve a stream by id or name, scoped to the current school."""
        from .models import Stream, School
        if school is None:
            school = School.objects.first()
        key = str(stream_id_or_name)
        qs = Stream.objects.filter(school=school) if school else Stream.objects
        if key.isdigit():
            return qs.get(id=int(key))
        return qs.get(name__iexact=key)

    def delete_stream(self, stream_id_or_name):
        from .models import Stream, School
        from django.core.cache import cache
        try:
            school = School.objects.first()
            s = self._get_stream(stream_id_or_name, school)
            name = s.name
            all_students = s.students.count()
            if all_students > 0:
                active = s.students.filter(is_active=True).count()
                s.is_active = False
                s.save(update_fields=["is_active"])
                cache.delete("active_streams")
                return {"success": True, "message": f"Stream '{name}' deactivated ({all_students} students, {active} active). Use reassign_stream_students to fully remove."}
            s.delete()
            cache.delete("active_streams")
            return {"success": True, "message": f"Stream '{name}' deleted (no students)."}
        except Stream.DoesNotExist:
            return {"success": False, "message": "Stream not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def reassign_stream_students(self, from_stream_name, to_stream_name):
        from .models import Stream, Student, School
        from django.core.cache import cache
        try:
            school = School.objects.first()
            try:
                src = self._get_stream(from_stream_name, school)
            except Stream.DoesNotExist:
                return {"success": False, "message": f"Source stream '{from_stream_name}' not found."}
            try:
                dst = self._get_stream(to_stream_name, school)
                if not dst.is_active:
                    raise Stream.DoesNotExist
            except Stream.DoesNotExist:
                return {"success": False, "message": f"Destination stream '{to_stream_name}' not found or inactive."}
            count = Student.objects.filter(stream=src).update(stream=dst)
            src.is_active = False
            src.save(update_fields=["is_active"])
            cache.delete("active_streams")
            return {"success": True, "message": f"Moved {count} student(s) from '{src.name}' to '{dst.name}'. Source deactivated."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def rename_stream(self, stream_id_or_name, new_name):
        from .models import Stream, School
        from django.core.cache import cache
        try:
            school = School.objects.first()
            s = self._get_stream(stream_id_or_name, school)
            old = s.name
            s.name = _safe_str(new_name, 50)
            s.save(update_fields=["name"])
            cache.delete("active_streams")
            return {"success": True, "message": f"Stream renamed '{old}' to '{s.name}'."}
        except Stream.DoesNotExist:
            return {"success": False, "message": "Stream not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def add_student(self, name, admission_number, stream_name, form, year=None, notes=""):
        from .models import Student, Stream
        from django.utils import timezone as tz
        try:
            name = _safe_str(name, 200)
            admission_number = _safe_str(admission_number, 20)
            if not name or not admission_number:
                return {"success": False, "message": "Name and admission number are required."}
            if Student.objects.filter(admission_number=admission_number).exists():
                return {"success": False, "message": f"Admission number '{admission_number}' already exists."}
            try:
                stream = Stream.objects.get(name__iexact=str(stream_name), is_active=True)
            except Stream.DoesNotExist:
                return {"success": False, "message": f"Stream '{stream_name}' not found."}
            valid_forms = [f[0] for f in Student.FORM_CHOICES]
            if form not in valid_forms:
                normalized = f"Form {form}" if not str(form).startswith("Form") else form
                form = normalized if normalized in valid_forms else form
                if form not in valid_forms:
                    return {"success": False, "message": f"Invalid form '{form}'. Valid: {', '.join(valid_forms)}"}
            student = Student.objects.create(
                name=name, admission_number=admission_number, stream=stream,
                form=form, year=int(year) if year else tz.now().year,
                optional_notes=_safe_str(notes), is_active=True,
            )
            return {"success": True, "message": f"Student '{student.name}' (#{admission_number}) added to {stream.name} {form}.", "data": {"id": student.id}}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def bulk_add_students(self, students_list):
        results = {"added": [], "failed": []}
        for s in students_list:
            r = self.add_student(
                name=s.get("name", ""), admission_number=str(s.get("admission_number", "")),
                stream_name=s.get("stream_name", ""), form=s.get("form", ""),
                year=s.get("year"), notes=s.get("notes", ""),
            )
            if r["success"]:
                results["added"].append(s.get("name", "?"))
            else:
                results["failed"].append({"name": s.get("name", "?"), "reason": r["message"]})
        ok = len(results["added"])
        return {"success": ok > 0, "message": f"Bulk import: {ok}/{len(students_list)} added.", "data": results}

    def edit_student(self, admission_or_id, **fields):
        from .models import Student, Stream
        try:
            s = Student.objects.get(id=int(admission_or_id)) if (str(admission_or_id).isdigit() and len(str(admission_or_id)) < 6) else Student.objects.get(admission_number=str(admission_or_id))
            updated = []
            for key, val in fields.items():
                if key == "stream_name":
                    stream = Stream.objects.get(name__iexact=str(val), is_active=True)
                    s.stream = stream
                    updated.append(f"stream={stream.name}")
                elif key in {"name", "form", "year", "optional_notes", "is_active"}:
                    setattr(s, key, val)
                    updated.append(f"{key}={val}")
            s.save()
            return {"success": True, "message": f"Student '{s.name}' updated: {', '.join(updated) or 'no changes'}."}
        except Student.DoesNotExist:
            return {"success": False, "message": "Student not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_student(self, admission_or_id):
        from .models import Student
        try:
            s = Student.objects.get(id=int(admission_or_id)) if (str(admission_or_id).isdigit() and len(str(admission_or_id)) < 6) else Student.objects.get(admission_number=str(admission_or_id))
            name = s.name
            s.is_active = False
            s.save(update_fields=["is_active"])
            return {"success": True, "message": f"Student '{name}' deactivated."}
        except Student.DoesNotExist:
            return {"success": False, "message": "Student not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_school_settings(self, **fields):
        from .models import School
        try:
            school, _ = School.objects.get_or_create(id=1)
            allowed = {"name", "short_name", "motto", "address", "phone", "email", "website", "current_year", "terms_per_year"}
            updated = [f"{k}={v}" for k, v in fields.items() if k in allowed and not setattr(school, k, v)]
            school.save()
            from django.core.cache import cache
            cache.delete("school_settings")
            return {"success": True, "message": f"School settings updated: {', '.join(updated) or 'no changes'}."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def create_category(self, name, key=None, description="", default_rating="MODERATE", risk_weight=10, severity_level=2):
        from .models import DisciplineCategory
        from django.core.cache import cache
        try:
            name = _safe_str(name, 120)
            if not key:
                key = re.sub(r"[^A-Z0-9_]", "_", name.upper())[:30]
            if DisciplineCategory.objects.filter(key=key).exists():
                return {"success": False, "message": f"Category key '{key}' already exists."}
            cat = DisciplineCategory.objects.create(
                key=key, name=name, description=_safe_str(description),
                default_rating=default_rating, risk_weight=risk_weight,
                severity_level=severity_level, is_active=True,
            )
            cache.delete("active_categories")
            return {"success": True, "message": f"Category '{cat.name}' created.", "data": {"id": cat.id}}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_category(self, name_or_key):
        from .models import DisciplineCategory
        from django.core.cache import cache
        try:
            try:
                cat = DisciplineCategory.objects.get(key__iexact=str(name_or_key))
            except DisciplineCategory.DoesNotExist:
                cat = DisciplineCategory.objects.get(name__iexact=str(name_or_key))
            cat.is_active = False
            cat.save(update_fields=["is_active"])
            cache.delete("active_categories")
            return {"success": True, "message": f"Category '{cat.name}' deactivated."}
        except DisciplineCategory.DoesNotExist:
            return {"success": False, "message": "Category not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def approve_teacher(self, username_or_id):
        from django.contrib.auth.models import User
        from .models import TeacherProfile
        try:
            user = User.objects.get(id=int(username_or_id)) if str(username_or_id).isdigit() else User.objects.get(username__iexact=str(username_or_id))
            p, _ = TeacherProfile.objects.get_or_create(user=user)
            p.is_approved = True
            p.is_suspended = False
            p.save(update_fields=["is_approved", "is_suspended"])
            return {"success": True, "message": f"Teacher '{user.get_full_name() or user.username}' approved."}
        except User.DoesNotExist:
            return {"success": False, "message": "User not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def suspend_teacher(self, username_or_id, reason="Suspended by admin agent"):
        from django.contrib.auth.models import User
        from .models import TeacherProfile
        try:
            user = User.objects.get(id=int(username_or_id)) if str(username_or_id).isdigit() else User.objects.get(username__iexact=str(username_or_id))
            p, _ = TeacherProfile.objects.get_or_create(user=user)
            p.is_suspended = True
            p.suspension_reason = _safe_str(reason)
            p.suspended_at = _now()
            p.save(update_fields=["is_suspended", "suspension_reason", "suspended_at"])
            return {"success": True, "message": f"Teacher '{user.username}' suspended: {reason}"}
        except User.DoesNotExist:
            return {"success": False, "message": "User not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def reset_teacher_password(self, username_or_id, new_password):
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=int(username_or_id)) if str(username_or_id).isdigit() else User.objects.get(username__iexact=str(username_or_id))
            if len(str(new_password)) < 8:
                return {"success": False, "message": "Password must be at least 8 characters."}
            user.set_password(new_password)
            user.save()
            return {"success": True, "message": f"Password reset for '{user.username}'."}
        except User.DoesNotExist:
            return {"success": False, "message": "User not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_report(self, report_id):
        from .models import DisciplineReport
        try:
            r = DisciplineReport.objects.get(id=int(report_id))
            name = r.student.name
            r.delete()
            return {"success": True, "message": f"Report #{report_id} for '{name}' deleted."}
        except DisciplineReport.DoesNotExist:
            return {"success": False, "message": f"Report #{report_id} not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def recalculate_all_risk_scores(self):
        from .models import Student
        try:
            students = Student.objects.filter(is_active=True)
            for s in students:
                s.update_risk_score()
                s.save(update_fields=["risk_score", "risk_level"])
            return {"success": True, "message": f"Risk scores recalculated for {students.count()} students."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ── CODE WRITE OPERATIONS ─────────────────────────────────────────────────

    def exec_apply_patch(self, path: str, search: str, replace: str) -> dict:
        """Apply a confirmed search-and-replace patch to a source file."""
        try:
            base = _base_dir()
            full = (base / path).resolve()
            if not str(full).startswith(str(base)):
                return {"success": False, "message": "Path traversal rejected."}
            if not full.exists():
                return {"success": False, "message": f"File not found: {path}"}
            content = full.read_text(encoding="utf-8", errors="replace")
            if search not in content:
                return {"success": False, "message": f"Search string not found in {path}. No changes made."}
            new_content = content.replace(search, replace, 1)
            full.write_text(new_content, encoding="utf-8")
            lines_changed = new_content.count("\n") - content.count("\n")
            return {"success": True, "message": f"Patch applied to {path}. Lines delta: {lines_changed:+d}."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def exec_create_file(self, path: str, content: str) -> dict:
        """Create a new file with provided content."""
        try:
            base = _base_dir()
            full = (base / path).resolve()
            if not str(full).startswith(str(base)):
                return {"success": False, "message": "Path traversal rejected."}
            if full.exists():
                return {"success": False, "message": f"File already exists: {path}. Use apply_patch to modify it."}
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            return {"success": True, "message": f"File created: {path} ({len(content)} bytes)."}
        except Exception as e:
            return {"success": False, "message": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# AdminDataReader — rich read-only DB context for the LLM
# ─────────────────────────────────────────────────────────────────────────────

class AdminDataReader:
    def get_full_school_context(self):
        try:
            from .models import School, Stream, Student, DisciplineReport, DisciplineCategory
            from django.contrib.auth.models import User
            school = School.objects.first()
            return {
                "school": {
                    "name": school.name if school else "Unknown",
                    "motto": school.motto if school else "",
                    "current_year": school.current_year if school else "",
                    "allow_teacher_registration": bool(school.allow_teacher_registration if school else False),
                    "require_teacher_approval": bool(school.require_teacher_approval if school else False),
                },
                "streams": list(Stream.objects.filter(is_active=True).values("id", "name", "code")),
                "students": {
                    "total": Student.objects.filter(is_active=True).count(),
                    "critical": Student.objects.filter(is_active=True, risk_level="CRITICAL").count(),
                    "warning": Student.objects.filter(is_active=True, risk_level="WARNING").count(),
                    "good": Student.objects.filter(is_active=True, risk_level="GOOD").count(),
                },
                "total_reports": DisciplineReport.objects.count(),
                "total_teachers": User.objects.filter(groups__name__in=["ClassTeacher", "Teacher"]).distinct().count(),
                "categories": list(DisciplineCategory.objects.filter(is_active=True).values("id", "key", "name")),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_students_for_context(self, limit=60):
        try:
            from .models import Student
            return list(
                Student.objects.filter(is_active=True)
                .select_related("stream")
                .order_by("-risk_score")[:limit]
                .values("id", "name", "admission_number", "stream__name", "form", "year", "risk_score", "risk_level")
            )
        except Exception:
            return []

    def get_teachers_for_context(self):
        try:
            from .models import TeacherProfile
            teachers = []
            for p in TeacherProfile.objects.select_related("user", "assigned_stream").all():
                teachers.append({
                    "id": p.user.id,
                    "username": p.user.username,
                    "name": p.user.get_full_name() or p.user.username,
                    "stream": p.assigned_stream.name if p.assigned_stream else None,
                    "is_approved": p.is_approved,
                    "is_suspended": p.is_suspended,
                    "groups": list(p.user.groups.values_list("name", flat=True)),
                })
            return teachers
        except Exception:
            return []


# ─────────────────────────────────────────────────────────────────────────────
# Action parser — extract structured action from AI response
# ─────────────────────────────────────────────────────────────────────────────

def parse_action_from_response(response_text: str) -> dict | None:
    pattern = r"```action\s*(\{.*?\})\s*```"
    match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# System prompt — full engineering agent
# ─────────────────────────────────────────────────────────────────────────────

ENGINEERING_SYSTEM_PROMPT = """You are ADMIN ENGINEERING AGENT — a full-stack AI agent with complete read access to the application source code, database, logs, and routes, plus controlled write access to the database and source code. You are NOT a generic chatbot. You are an AI software engineer + system administrator embedded in this Django school discipline management system.

## YOUR TOOLS
You have explicit tools available. When an admin asks you ANYTHING, decide which tool(s) to use, use them, and answer from the result. NEVER fall back to a generic AI answer when a tool can give the real answer.

| Tool | Purpose | Write? |
|---|---|---|
| app_manifest | Full app structure: models, routes, source tree | Read |
| db_schema | All tables, columns, constraints | Read |
| db_row_counts | Row counts per table | Read |
| db_query(sql) | Raw SELECT query | Read |
| db_analyze(question) | Factual DB question → live answer | Read |
| read_file(path) | Read any source file | Read |
| search_code(pattern, path) | Regex search across source | Read |
| inspect_route(url) | Find route → view → read source | Read |
| inspect_model(name) | Fields, relations, constraints of a model | Read |
| list_routes | All URL routes | Read |
| read_logs | Error log | Read |
| parse_tracebacks | Structured traceback analysis | Read |
| diagnostics | Data integrity + backend health | Read |
| run_management_command(cmd) | Safe Django mgmt commands | Read |
| apply_patch(path,search,replace) | Patch source file (confirmation required) | ⚠️ Write |
| create_file(path,content) | Create new file (confirmation required) | ⚠️ Write |
| DB write actions (create_stream etc.) | See ACTION BLOCK below | ⚠️ Write |

## ACTION BLOCK FORMAT (for ALL write operations)
Every write command MUST end your response with this exact block:

```action
{"type": "ACTION_TYPE", "params": {PARAMS}, "description": "brief summary"}
```

## SUPPORTED ACTION TYPES (DATABASE)
create_stream, bulk_create_streams, delete_stream, reassign_stream_students, rename_stream,
add_student, bulk_add_students, edit_student, delete_student,
update_school, create_category, delete_category,
approve_teacher, suspend_teacher, reset_password,
delete_report, recalculate_risk

## SUPPORTED ACTION TYPES (CODE)
apply_patch — params: {path, search, replace}
create_file — params: {path, content}

## OPERATING MODES
🔎 INSPECT  — Read everything, answer factually, never modify. Default mode.
🧠 ANALYSIS — Investigate relationships, debug root causes. Read tools + reasoning.
🛠️ REPAIR   — Propose patches/fixes after investigation. Issues action blocks for confirmation.
🧪 TEST     — Run management commands, diagnostics, health checks.
🚨 INCIDENT — Deep triage: analyze error logs, tracebacks, 5xx routes, data anomalies.

## HOW TO HANDLE ANY REQUEST

### "List all teachers" / "How many teachers are registered?"
→ Use db_analyze("list all teachers") — gives live DB answer. Never guess.

### "Show Form 3 students in STEM stream"
→ Use db_query("SELECT name, admission_number, form, risk_level FROM core_student WHERE stream_id = (SELECT id FROM core_stream WHERE name ILIKE '%STEM%') AND form = 'Form 3' AND is_active=1")

### "Why is the teacher dashboard returning 500?"
INCIDENT MODE investigation:
1. read_logs → find the traceback
2. parse_tracebacks → identify exception + file
3. inspect_route("/teacher-dashboard/") → find view
4. read_file("core/views.py") → read the view function
5. inspect_model if relevant
6. Summarize: route → view → exception → root cause → proposed fix
7. Output apply_patch action block

### "Fix the error when creating a teacher"
REPAIR MODE:
1. search_code("def.*teacher.*create|create.*teacher", "core/views.py")
2. read_file relevant section
3. parse_tracebacks to get the actual error
4. Identify the exact line + fix
5. Output apply_patch action block with precise search/replace

### "Analyze the student management system"
INSPECT MODE:
1. inspect_model("Student")
2. db_row_counts
3. diagnostics
4. Output a structured analysis with tables, issues, and recommendations

## DEBUGGING PROTOCOL (for 500s / exceptions)
```
1. read_logs → get the latest traceback
2. parse_tracebacks → extract: exception type, file, line, function
3. inspect_route(url) → find: view name, module
4. read_file(view_file) → read: the failing function (use line context)
5. inspect_model if DB-related
6. REPORT:
   - Route: <URL>
   - View: <function name> in <file>
   - Exception: <type>: <message>
   - Cause: <1-2 sentence explanation>
   - Affected files: <list>
   - Confidence: <N>%
7. If REPAIR mode: output apply_patch action block
```

## RESPONSE FORMAT FOR TOOL CALLS
When you use a tool, show:
```tool_call
{"tool": "TOOL_NAME", "params": {...}}
```
Then on the next line show the result you're basing your answer on.

## RULES
1. Answer ONLY from live tool results. Never invent data.
2. For factual DB questions (teachers, students, reports), always use db_analyze or db_query first.
3. For code/bug questions, use inspect_route → read_file → parse_tracebacks in sequence.
4. Write operations always end with an action block. Never execute silently.
5. Form values: "Form 1", "Form 2", ... "Form 10" (normalize if needed).
6. Be concise. No preamble, no disclaimers, no generic AI filler.
7. If a tool returns an error, report the error and propose what to check next.
"""


# ─────────────────────────────────────────────────────────────────────────────
# AdminAgent — main orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class AdminAgent:
    """
    Main entry point for the engineering agent.
    Routes through the full AgentPipeline for complex intents;
    falls back to LocalQueryRouter for instant factual answers.
    """

    def __init__(self):
        self.executor = AdminActionExecutor()
        self.reader   = AdminDataReader()
        self.toolkit  = EngineeringToolkit()
        self._providers = None
        self._keys    = None
        self._models  = None

    def _load_providers(self):
        if self._providers is None:
            try:
                from core.ai_providers import load_provider_keys, load_models, configured_providers
                self._keys      = load_provider_keys()
                self._models    = load_models()
                self._providers = configured_providers()
            except Exception:
                self._providers = []
                self._keys = {}
                self._models = {}

    def _call_ai(self, messages: list, max_tokens: int = 3000, temperature: float = 0.2) -> dict:
        """Call the configured AI provider. Shared by pipeline components."""
        self._load_providers()
        import requests as req
        for provider in self._providers:
            key   = self._keys.get(provider)
            if not key:
                continue
            model = self._models.get(provider)
            try:
                if provider in ("openai", "openrouter", "groq"):
                    urls = {
                        "openai":     os.environ.get("OPENAI_URL", "https://api.openai.com/v1/chat/completions"),
                        "openrouter": os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"),
                        "groq":       os.environ.get("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions"),
                    }
                    url       = urls[provider]
                    env_max   = int(os.environ.get("AI_MAX_TOKENS", str(max_tokens)))
                    tok_key   = "max_completion_tokens" if provider == "groq" else "max_tokens"
                    payload   = {"model": model, "messages": messages, "temperature": temperature, tok_key: env_max}
                    headers   = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                    resp = req.post(url, headers=headers, json=payload, timeout=60)
                    if resp.status_code == 200:
                        text = resp.json()["choices"][0]["message"]["content"]
                        return {"success": True, "response": text, "provider": provider}
                elif provider == "gemini":
                    base_url   = os.environ.get("GEMINI_URL") or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                    text_input = "\n".join(m["content"] for m in messages if m["role"] in ("user", "system"))
                    payload    = {"contents": [{"parts": [{"text": text_input}]}]}
                    resp = req.post(base_url, params={"key": key}, json=payload, timeout=60)
                    if resp.status_code == 200:
                        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                        return {"success": True, "response": text, "provider": provider}
            except Exception as e:
                logger.warning("Agent provider %s failed: %s", provider, e)
                continue
        return {"success": False, "response": "All AI providers unavailable. Check API keys in settings.", "provider": None}

    # ── TOOL DISPATCH (called from views for inline tool results) ─────────────

    def run_tool(self, tool_name: str, params: dict) -> dict:
        """
        Execute a read tool by name and return its result.
        Write tools are routed through execute_action instead.
        """
        tk = self.toolkit
        try:
            if tool_name == "app_manifest":
                return tk.app_manifest()
            elif tool_name == "db_schema":
                return tk.db_schema()
            elif tool_name == "db_row_counts":
                return tk.db_row_counts()
            elif tool_name == "db_query":
                return tk.db_query(params.get("query", ""))
            elif tool_name == "db_analyze":
                return tk.db_analyze(params.get("question", ""))
            elif tool_name == "read_file":
                return tk.read_file(params.get("path", ""))
            elif tool_name == "search_code":
                return tk.search_code(params.get("pattern", ""), params.get("path", ""), params.get("file_ext", ".py"))
            elif tool_name == "inspect_route":
                return tk.inspect_route(params.get("url", ""))
            elif tool_name == "inspect_model":
                return tk.inspect_model(params.get("model_name", ""))
            elif tool_name == "list_routes":
                return tk.list_routes()
            elif tool_name == "read_logs":
                return tk.read_logs(int(params.get("tail_chars", 8000)))
            elif tool_name == "parse_tracebacks":
                return tk.parse_tracebacks()
            elif tool_name == "diagnostics":
                return tk.diagnostics()
            elif tool_name == "run_management_command":
                return tk.run_management_command(params.get("command", ""), params.get("args"))
            else:
                return {"ok": False, "output": f"Unknown tool: {tool_name}", "data": {}}
        except Exception as e:
            return {"ok": False, "output": str(e), "data": {}}

    def execute_action(self, action_type: str, params: dict) -> dict:
        """Execute a confirmed action (DB write or code write)."""
        ex = self.executor
        try:
            # ── Code write ──
            if action_type == "apply_patch":
                return ex.exec_apply_patch(**params)
            elif action_type == "create_file":
                return ex.exec_create_file(**params)
            # ── DB write ──
            elif action_type == "create_stream":
                return ex.create_stream(**params)
            elif action_type == "bulk_create_streams":
                return ex.bulk_create_streams(params.get("streams", []))
            elif action_type == "reassign_stream_students":
                # Normalise: LLMs sometimes emit from_stream_id/to_stream_id (integer IDs)
                # instead of the required from_stream_name/to_stream_name strings.
                # Look up the name from the DB so both forms are accepted.
                p = dict(params)
                if "from_stream_id" in p or "to_stream_id" in p:
                    from .models import Stream
                    if "from_stream_id" in p and "from_stream_name" not in p:
                        try:
                            p["from_stream_name"] = Stream.objects.get(id=int(p.pop("from_stream_id"))).name
                        except (Stream.DoesNotExist, ValueError, TypeError):
                            p["from_stream_name"] = str(p.pop("from_stream_id", ""))
                    if "to_stream_id" in p and "to_stream_name" not in p:
                        try:
                            p["to_stream_name"] = Stream.objects.get(id=int(p.pop("to_stream_id"))).name
                        except (Stream.DoesNotExist, ValueError, TypeError):
                            p["to_stream_name"] = str(p.pop("to_stream_id", ""))
                return ex.reassign_stream_students(**p)
            elif action_type == "delete_stream":
                return ex.delete_stream(**params)
            elif action_type == "rename_stream":
                return ex.rename_stream(**params)
            elif action_type == "add_student":
                return ex.add_student(**params)
            elif action_type == "bulk_add_students":
                return ex.bulk_add_students(params.get("students", []))
            elif action_type == "edit_student":
                admission_or_id = params.pop("admission_or_id", None)
                return ex.edit_student(admission_or_id, **params)
            elif action_type == "delete_student":
                return ex.delete_student(**params)
            elif action_type == "update_school":
                return ex.update_school_settings(**params)
            elif action_type == "create_category":
                return ex.create_category(**params)
            elif action_type == "delete_category":
                return ex.delete_category(**params)
            elif action_type == "approve_teacher":
                return ex.approve_teacher(**params)
            elif action_type == "suspend_teacher":
                return ex.suspend_teacher(**params)
            elif action_type == "reset_password":
                return ex.reset_teacher_password(**params)
            elif action_type == "delete_report":
                return ex.delete_report(**params)
            elif action_type == "recalculate_risk":
                return ex.recalculate_all_risk_scores()
            else:
                return {"success": False, "message": f"Unknown action type: {action_type}"}
        except Exception as e:
            logger.exception("execute_action failed for %s", action_type)
            return {"success": False, "message": str(e)}

    def chat(self, user_message: str, conversation_history: list | None = None,
             mode: str = "INSPECT") -> dict:
        """
        Main entry.

        Flow:
          1. LocalQueryRouter — instant ORM answers for pure factual reads (0ms, no LLM)
          2. AgentPipeline    — full INTENT→CONTEXT→PLAN→RISK→EXECUTE→VERIFY→AUDIT chain

        Returns:
          {success, response, action, provider, think_steps, audit, intent,
           replan_count, tool_calls}
        """
        # ── 0. Classify intent first so we can decide the fast path ───────────
        from core.agent_pipeline import IntentClassifier, Intent
        classifier = IntentClassifier()
        intent = classifier.classify(user_message)

        # ── 1. Fast path: LocalQueryRouter only for pure factual reads ─────────
        # Complex intents (ANALYSIS, INCIDENT, REPAIR, INSPECT_CODE, TEST) go
        # straight to the full pipeline — LQR cannot handle them.
        if intent in (Intent.READ_DATA, Intent.DB_WRITE):
            try:
                from core.admin_agent_queries import LocalQueryRouter
                router = LocalQueryRouter()
                local_answer = router.answer(user_message)
                if local_answer:
                    return {
                        "success":      True,
                        "response":     local_answer,
                        "action":       None,
                        "provider":     "local",
                        "source":       "local_db",
                        "raw_response": local_answer,
                        "tool_calls":   [],
                        "think_steps":  [{"phase": "INTENT", "label": "⚡ Local DB answer",
                                          "detail": "No LLM call needed", "status": "ok",
                                          "risk": "", "ms": 0}],
                        "audit":        [],
                        "intent":       "READ_DATA",
                        "replan_count": 0,
                    }
            except Exception:
                pass

        # ── 2. Full pipeline for everything else ──────────────────────────────
        try:
            from core.agent_pipeline import AgentPipeline
            pipeline = AgentPipeline(
                toolkit=self.toolkit,
                ai_caller=self._call_ai,
            )
            run = pipeline.run(
                message=user_message,
                mode=mode,
                conversation_history=conversation_history,
            )
            result = run.to_response_dict()
            result["raw_response"] = result["response"]
            result["success"] = bool(result.get("response"))
            return result

        except Exception as e:
            logger.exception("AgentPipeline failed, falling back to legacy path")
            # ── 3. Graceful fallback: single-shot LLM if pipeline errors ─────
            return self._legacy_chat(user_message, mode)

    def _legacy_chat(self, user_message: str, mode: str) -> dict:
        """Single-shot LLM fallback — used only if pipeline raises an exception."""
        try:
            from core.admin_agent_queries import AdminDataReader
            reader = AdminDataReader()
            ctx = reader.get_full_school_context()
        except Exception:
            ctx = {}
        system_prompt = (
            ENGINEERING_SYSTEM_PROMPT
            + f"\n\n## CURRENT MODE: {mode.upper()}"
            + "\n\n## LIVE DATABASE STATE\n"
            + json.dumps(ctx, indent=2, default=str)
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]
        result = self._call_ai(messages)
        if not result["success"]:
            return {
                "success": False, "response": result["response"],
                "action": None, "provider": None,
                "raw_response": result["response"],
                "tool_calls": [], "think_steps": [], "audit": [],
                "intent": "UNKNOWN", "replan_count": 0,
            }
        raw    = result["response"]
        action = parse_action_from_response(raw)
        display_text = re.sub(
            r"```action\s*\{.*?\}\s*```", "", raw,
            flags=re.DOTALL | re.IGNORECASE
        ).strip()
        return {
            "success": True, "response": display_text,
            "action": action, "provider": result.get("provider"),
            "raw_response": raw,
            "tool_calls": [], "think_steps": [], "audit": [],
            "intent": "UNKNOWN", "replan_count": 0,
        }
