# core/agent_pipeline.py
"""
Admin Engineering Agent — Full Agentic Pipeline

Implements the complete chain:

  ADMIN
    ↓
  IntentClassifier   — What does the admin want? (mode + intent tags)
    ↓
  ContextBuilder     — Discover relevant app knowledge (routes, views, logs, schema)
    ↓
  Planner            — LLM-driven investigation plan (ordered steps + tool selection)
    ↓
  RiskAssessor       — SAFE / LOW / MEDIUM / HIGH / CRITICAL per planned step
    ↓
  Executor           — Run read steps automatically; gate write steps behind approval
    ↓
  Verifier           — Did it work? DB consistent? Error gone? API responding?
    ↓
  AuditLog           — Persistent per-session record of all actions and outcomes
    ↓
  AdminResponse      — What was found / changed / tested / current status

When Verifier returns FAIL → Replanner re-analyses with new context and loops.

Key design principles:
  1. The LLM never sees everything at once — ContextBuilder retrieves only relevant info.
  2. Every mutation is assessed for risk before execution.
  3. The system can iterate (max 3 replan loops) rather than stopping on first failure.
  4. All thinking steps are returned as a structured trace for the frontend to render.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("core.agent_pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# Enums & data classes
# ─────────────────────────────────────────────────────────────────────────────

class Intent(str, Enum):
    READ_DATA     = "READ_DATA"      # list teachers, count students, etc.
    INSPECT_CODE  = "INSPECT_CODE"   # read file, inspect route, search code
    ANALYSIS      = "ANALYSIS"       # why is X failing? relationship queries
    INCIDENT      = "INCIDENT"       # 500 error, traceback, crash debug
    REPAIR        = "REPAIR"         # fix a bug, patch code, apply change
    DB_WRITE      = "DB_WRITE"       # add student, approve teacher, etc.
    TEST          = "TEST"           # run checks, diagnostics, commands
    UNKNOWN       = "UNKNOWN"


class RiskLevel(str, Enum):
    SAFE     = "SAFE"      # pure reads, no side-effects
    LOW      = "LOW"       # read + trivial write (e.g. recalculate risk)
    MEDIUM   = "MEDIUM"    # create/edit records
    HIGH     = "HIGH"      # delete records / suspend users / patch code
    CRITICAL = "CRITICAL"  # mass deletes / drop / irreversible schema change


@dataclass
class ThinkStep:
    """One step in the agent's visible thinking trace."""
    phase:   str           # INTENT | CONTEXT | PLAN | RISK | EXECUTE | VERIFY | AUDIT
    label:   str           # Human-readable label
    detail:  str = ""      # Supporting detail / tool output
    status:  str = "ok"    # ok | warning | error | pending | skipped
    risk:    str = ""      # RiskLevel if applicable
    ms:      int = 0       # Elapsed milliseconds

    def to_dict(self) -> dict:
        return {
            "phase":  self.phase,
            "label":  self.label,
            "detail": self.detail,
            "status": self.status,
            "risk":   self.risk,
            "ms":     self.ms,
        }


@dataclass
class PlanStep:
    """One step in the execution plan produced by the Planner."""
    step_id:     int
    description: str
    tool:        str               # tool name to call
    params:      dict = field(default_factory=dict)
    risk:        RiskLevel = RiskLevel.SAFE
    requires_approval: bool = False
    result:      Any = None
    status:      str = "pending"   # pending | done | failed | skipped | awaiting_approval


@dataclass
class AgentRun:
    """Full state of one agent invocation — passed through the pipeline."""
    message:       str
    intent:        Intent = Intent.UNKNOWN
    mode:          str = "INSPECT"
    context:       dict = field(default_factory=dict)
    plan:          list[PlanStep] = field(default_factory=list)
    think_steps:   list[ThinkStep] = field(default_factory=list)
    audit_entries: list[dict] = field(default_factory=list)
    final_response: str = ""
    pending_action: dict | None = None   # action needing frontend approval
    provider:      str = ""
    replan_count:  int = 0
    start_time:    float = field(default_factory=time.monotonic)

    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def add_think(self, phase: str, label: str, detail: str = "",
                  status: str = "ok", risk: str = "") -> ThinkStep:
        step = ThinkStep(phase=phase, label=label, detail=detail,
                         status=status, risk=risk, ms=self.elapsed_ms())
        self.think_steps.append(step)
        return step

    def to_response_dict(self) -> dict:
        return {
            "success":       bool(self.final_response),
            "response":      self.final_response,
            "action":        self.pending_action,
            "provider":      self.provider,
            "think_steps":   [s.to_dict() for s in self.think_steps],
            "audit":         self.audit_entries,
            "intent":        self.intent.value,
            "replan_count":  self.replan_count,
            "tool_calls":    [s.tool for s in self.plan if s.status == "done"],
        }


# ─────────────────────────────────────────────────────────────────────────────
# IntentClassifier
# ─────────────────────────────────────────────────────────────────────────────

class IntentClassifier:
    """
    Classifies the admin's message into an Intent without calling the LLM.
    Fast regex-based classification — ~0ms.
    """

    _PATTERNS: list[tuple[re.Pattern, Intent]] = [
        # Repair / fix — checked FIRST so "fix the ... 500" routes to REPAIR not INCIDENT
        (re.compile(
            r"\bfix\s+(the|this|an?)\b|"
            r"\b(repair|apply.{0,10}patch|write.{0,10}fix|"
            r"correct\s+the|resolve\s+the|modify.{0,10}file)\b", re.I),
         Intent.REPAIR),
        # Incident — specific "why is X failing / returning / 500 / traceback"
        (re.compile(
            r"\b(500|traceback|crash|stack.?trace)\b|"
            r"why\s+is.{0,50}(failing|returning|broken|not\s+work)|"
            r"\b(exception|incident)\b", re.I),
         Intent.INCIDENT),
        # Analysis — investigate*, analyze/analyse, relationship, pattern
        (re.compile(
            r"\binvestigat\w*|"
            r"\b(analy[sz]e?|relation|depend|impact|affect|"
            r"missing\s+from|why\s+are|students\s+with|students\s+without|"
            r"most\s+reported|correlation|pattern|how\s+does)\b", re.I),
         Intent.ANALYSIS),
        # Code inspection
        (re.compile(
            r"\binspect.{0,10}(route|model)|read.{0,10}file|search.{0,10}code|"
            r"show.{0,10}source|list.{0,10}routes?|source.{0,10}code|"
            r"view.{0,10}code|look.{0,10}at.{0,10}file|open.{0,10}file\b", re.I),
         Intent.INSPECT_CODE),
        # Test / health checks
        (re.compile(
            r"\b(run.{0,10}command|showmigration|system.{0,10}check|"
            r"backend.{0,10}health|health.{0,10}check|django.{0,10}check)\b|"
            r"\b(test|check|migration|diagnos)\b", re.I),
         Intent.TEST),
        # DB writes — specific mutation verbs on named objects
        (re.compile(
            r"\b(add\s+student|create\s+stream|delete\s+student|remove\s+student|"
            r"rename\s+stream|approve\s+teacher|suspend\s+teacher|"
            r"unsuspend|reset\s+password|bulk\s+(add|create|import)|"
            r"recalculate|deactivate|assign\s+teacher|ban\s+user)\b|"
            r"\b(add|create|delete|remove|rename|update|edit)\b", re.I),
         Intent.DB_WRITE),
        # Pure data reads — most general, last
        (re.compile(
            r"\b(list|show|display|count|how\s+many|what.{0,10}is|tell.{0,10}me|"
            r"give.{0,10}me|who|which)\b|"
            r"\ball\s+(teacher|student|stream|report|categor|route)\b", re.I),
         Intent.READ_DATA),
    ]

    def classify(self, message: str) -> Intent:
        for pattern, intent in self._PATTERNS:
            if pattern.search(message):
                return intent
        return Intent.READ_DATA  # safe fallback

    def to_mode(self, intent: Intent) -> str:
        mapping = {
            Intent.READ_DATA:    "INSPECT",
            Intent.INSPECT_CODE: "INSPECT",
            Intent.ANALYSIS:     "ANALYSIS",
            Intent.INCIDENT:     "INCIDENT",
            Intent.REPAIR:       "REPAIR",
            Intent.DB_WRITE:     "INSPECT",
            Intent.TEST:         "TEST",
            Intent.UNKNOWN:      "INSPECT",
        }
        return mapping.get(intent, "INSPECT")


# ─────────────────────────────────────────────────────────────────────────────
# ContextBuilder
# ─────────────────────────────────────────────────────────────────────────────

class ContextBuilder:
    """
    Retrieves only the information relevant to the current intent.
    Never dumps everything — targeted discovery prevents token bloat.
    """

    def __init__(self, toolkit):
        self.tk = toolkit

    def build(self, run: AgentRun) -> dict:
        ctx = {}
        msg = run.message.lower()
        intent = run.intent

        t0 = time.monotonic()

        # Always include school overview (tiny)
        try:
            from core.admin_agent_queries import AdminDataReader
            reader = AdminDataReader()
            ctx["school_overview"] = reader.get_full_school_context()
        except Exception:
            pass

        # ── For incidents: logs + tracebacks are always first ────────────────
        if intent in (Intent.INCIDENT, Intent.ANALYSIS, Intent.REPAIR):
            r = self.tk.parse_tracebacks()
            if r["ok"] and r["data"]:
                ctx["tracebacks"] = r["data"]
                run.add_think("CONTEXT", "📋 Tracebacks extracted",
                              f"{len(r['data'])} traceback(s) found", "ok")

            log_r = self.tk.read_logs(tail_chars=6000)
            if log_r["ok"]:
                ctx["recent_logs"] = log_r["data"][-3000:]
                run.add_think("CONTEXT", "📄 Error log loaded",
                              f"{len(log_r['data'])} chars", "ok")

        # ── Route + view discovery for URL-related queries ────────────────────
        url_hints = re.findall(
            r"(?:/[\w/.-]+|'[\w/.-]+'|\"[\w/.-]+\"|"
            r"\b(?:teacher|student|dashboard|admin|report|stream|"
            r"login|profile|upload|api)\b)",
            msg,
        )
        if url_hints and intent in (Intent.INCIDENT, Intent.REPAIR, Intent.INSPECT_CODE, Intent.ANALYSIS):
            for hint in url_hints[:3]:
                hint = hint.strip("'\"")
                r = self.tk.inspect_route(hint)
                if r["ok"]:
                    key = f"route_{hint.replace('/','_').strip('_')}"
                    ctx[key] = r["data"]
                    run.add_think("CONTEXT", f"🔎 Route inspected: {hint}",
                                  r["output"], "ok")
                    break  # first hit is enough for context building

        # ── Model discovery ───────────────────────────────────────────────────
        model_keywords = {
            "teacher": "TeacherProfile",
            "student": "Student",
            "stream":  "Stream",
            "report":  "DisciplineReport",
            "category": "DisciplineCategory",
            "school":  "School",
            "session": "UserSession",
            "notification": "Notification",
        }
        for kw, model_name in model_keywords.items():
            if kw in msg and intent not in (Intent.READ_DATA,):
                r = self.tk.inspect_model(model_name)
                if r["ok"]:
                    ctx[f"model_{model_name}"] = {
                        "table": r["data"].get("table"),
                        "fields": r["data"].get("fields", []),
                    }
                    run.add_think("CONTEXT", f"🗂️ Model: {model_name}",
                                  f"{len(r['data'].get('fields',[]))} fields", "ok")
                break  # one model per context pass is enough

        # ── DB schema for data/analysis queries ───────────────────────────────
        if intent in (Intent.ANALYSIS, Intent.INCIDENT, Intent.REPAIR):
            r = self.tk.db_row_counts()
            if r["ok"]:
                ctx["db_row_counts"] = r["data"]
                run.add_think("CONTEXT", "🗄️ DB row counts loaded", r["output"], "ok")

        # ── Source search for repair / inspect ────────────────────────────────
        if intent in (Intent.REPAIR, Intent.INSPECT_CODE):
            # Search for the most relevant function/view
            search_terms = []
            if "teacher" in msg:
                search_terms.append("def.*teacher|teacher.*view|TeacherProfile")
            if "student" in msg:
                search_terms.append("def.*student|student.*view")
            if "report" in msg:
                search_terms.append("def.*report|DisciplineReport")
            if "dashboard" in msg:
                search_terms.append("def.*dashboard")
            if "password" in msg or "reset" in msg:
                search_terms.append("def.*password|def.*reset")

            for term in search_terms[:2]:
                r = self.tk.search_code(term, "core/views.py")
                if r["ok"] and r["data"] and r["data"] != "(no matches)":
                    ctx[f"code_search_{term[:20]}"] = r["data"][:2000]
                    run.add_think("CONTEXT", f"🔍 Code search: {term[:30]}",
                                  r["output"], "ok")
                    break

        ms = int((time.monotonic() - t0) * 1000)
        run.add_think("CONTEXT", f"✅ Context assembled ({len(ctx)} sources)",
                      f"{ms}ms", "ok")
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
# RiskAssessor
# ─────────────────────────────────────────────────────────────────────────────

class RiskAssessor:
    """
    Maps action types to risk levels.
    Reads never need approval. Writes are gated by risk level.
    """

    # Risk level per action / tool
    _RISK_MAP: dict[str, RiskLevel] = {
        # Pure reads — always safe
        "app_manifest":         RiskLevel.SAFE,
        "db_schema":            RiskLevel.SAFE,
        "db_row_counts":        RiskLevel.SAFE,
        "db_query":             RiskLevel.SAFE,
        "db_analyze":           RiskLevel.SAFE,
        "read_file":            RiskLevel.SAFE,
        "search_code":          RiskLevel.SAFE,
        "inspect_route":        RiskLevel.SAFE,
        "inspect_model":        RiskLevel.SAFE,
        "list_routes":          RiskLevel.SAFE,
        "read_logs":            RiskLevel.SAFE,
        "parse_tracebacks":     RiskLevel.SAFE,
        "diagnostics":          RiskLevel.SAFE,
        # Low risk — reversible, low impact
        "run_management_command": RiskLevel.LOW,
        "recalculate_risk":     RiskLevel.LOW,
        "approve_teacher":      RiskLevel.LOW,
        # Medium risk — creates new records
        "create_stream":        RiskLevel.MEDIUM,
        "bulk_create_streams":  RiskLevel.MEDIUM,
        "add_student":          RiskLevel.MEDIUM,
        "bulk_add_students":    RiskLevel.MEDIUM,
        "edit_student":         RiskLevel.MEDIUM,
        "update_school":        RiskLevel.MEDIUM,
        "create_category":      RiskLevel.MEDIUM,
        "rename_stream":        RiskLevel.MEDIUM,
        # High risk — deletes, suspensions, code changes
        "delete_stream":        RiskLevel.HIGH,
        "delete_student":       RiskLevel.HIGH,
        "delete_category":      RiskLevel.HIGH,
        "delete_report":        RiskLevel.HIGH,
        "suspend_teacher":      RiskLevel.HIGH,
        "reset_password":       RiskLevel.HIGH,
        "apply_patch":          RiskLevel.HIGH,
        "create_file":          RiskLevel.MEDIUM,
        "reassign_stream_students": RiskLevel.HIGH,
        # Critical — mass operations
        "bulk_delete":          RiskLevel.CRITICAL,
        "drop_table":           RiskLevel.CRITICAL,
    }

    # Minimum risk level that requires admin approval (inclusive)
    APPROVAL_THRESHOLD = RiskLevel.MEDIUM

    _ORDER = [RiskLevel.SAFE, RiskLevel.LOW, RiskLevel.MEDIUM,
              RiskLevel.HIGH, RiskLevel.CRITICAL]

    def assess(self, tool_or_action: str) -> RiskLevel:
        return self._RISK_MAP.get(tool_or_action, RiskLevel.MEDIUM)

    def requires_approval(self, risk: RiskLevel) -> bool:
        return self._ORDER.index(risk) >= self._ORDER.index(self.APPROVAL_THRESHOLD)

    def badge_color(self, risk: RiskLevel) -> str:
        return {
            RiskLevel.SAFE:     "#059669",
            RiskLevel.LOW:      "#0891b2",
            RiskLevel.MEDIUM:   "#d97706",
            RiskLevel.HIGH:     "#dc2626",
            RiskLevel.CRITICAL: "#7c2d12",
        }.get(risk, "#6b7280")


# ─────────────────────────────────────────────────────────────────────────────
# Planner  (LLM-driven)
# ─────────────────────────────────────────────────────────────────────────────

class Planner:
    """
    Uses the LLM to produce a structured JSON investigation plan.
    The plan is a list of steps with tool names and parameters.
    """

    PLAN_PROMPT = """You are a planning engine for an admin engineering agent.

Given:
- Admin message: {message}
- Intent: {intent}
- Mode: {mode}
- Context gathered so far: {context_summary}

Produce a JSON array of investigation steps. Each step has:
  - "step_id": integer starting at 1
  - "description": what this step does (one sentence)
  - "tool": one of the allowed tools below
  - "params": dict of parameters for the tool

ALLOWED TOOLS:
  read_file(path)
  search_code(pattern, path, file_ext)
  inspect_route(url)
  inspect_model(model_name)   -- model_name MUST be the Python class name e.g. "Stream", "Student", "TeacherProfile" (NOT the DB table name like "core_stream")
  list_routes()
  read_logs(tail_chars)
  parse_tracebacks()
  diagnostics()
  db_query(query)
  db_row_counts()
  app_manifest()
  run_management_command(command, args)

For write operations (they will be shown for approval separately), include:
  create_stream / add_student / edit_student / delete_student /
  approve_teacher / suspend_teacher / reset_password /
  delete_report / recalculate_risk / update_school /
  apply_patch(path, search, replace) / create_file(path, content)

RULES:
1. Maximum 6 steps per plan.
2. Start with the most targeted read steps first.
3. For INCIDENT: always start with parse_tracebacks, then inspect_route, then read_file.
4. For REPAIR: plan ends with an apply_patch or create_file step.
5. For READ_DATA or INSPECT: 1-2 steps maximum.
6. Output ONLY valid JSON array. No explanation before or after.

Example for "why is teacher dashboard returning 500":
[
  {{"step_id":1,"description":"Extract latest tracebacks from error log","tool":"parse_tracebacks","params":{{}}}},
  {{"step_id":2,"description":"Inspect the teacher-dashboard route and view","tool":"inspect_route","params":{{"url":"teacher-dashboard"}}}},
  {{"step_id":3,"description":"Read the teacher_dashboard view source","tool":"read_file","params":{{"path":"core/views.py"}}}},
  {{"step_id":4,"description":"Inspect TeacherProfile model for constraint issues","tool":"inspect_model","params":{{"model_name":"TeacherProfile"}}}}
]
"""

    def __init__(self, ai_caller):
        self._call_ai = ai_caller

    def plan(self, run: AgentRun) -> list[PlanStep]:
        context_summary = self._summarize_context(run.context)
        prompt = self.PLAN_PROMPT.format(
            message=run.message,
            intent=run.intent.value,
            mode=run.mode,
            context_summary=context_summary,
        )
        messages = [
            {"role": "system", "content": "You are a JSON-only planning engine. Output only valid JSON arrays. No markdown, no explanation."},
            {"role": "user",   "content": prompt},
        ]
        result = self._call_ai(messages, max_tokens=800, temperature=0.1)
        if not result["success"]:
            run.add_think("PLAN", "⚠️ Planner LLM failed — using default plan",
                          result["response"], "warning")
            return self._default_plan(run)

        raw = result["response"].strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

        try:
            steps_data = json.loads(raw)
            if not isinstance(steps_data, list):
                raise ValueError("Not a list")
            assessor = RiskAssessor()
            steps = []
            for s in steps_data[:6]:
                tool   = s.get("tool", "diagnostics")
                risk   = assessor.assess(tool)
                steps.append(PlanStep(
                    step_id=s.get("step_id", len(steps)+1),
                    description=s.get("description", ""),
                    tool=tool,
                    params=s.get("params", {}),
                    risk=risk,
                    requires_approval=assessor.requires_approval(risk),
                ))
            run.add_think("PLAN", f"📋 Plan created: {len(steps)} step(s)",
                          "\n".join(f"  {s.step_id}. [{s.tool}] {s.description}" for s in steps),
                          "ok")
            run.provider = result.get("provider", "")
            return steps
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            run.add_think("PLAN", "⚠️ Plan parse failed — using default plan",
                          str(e), "warning")
            return self._default_plan(run)

    def _default_plan(self, run: AgentRun) -> list[PlanStep]:
        """Fallback plan based on intent when LLM plan fails."""
        assessor = RiskAssessor()
        if run.intent == Intent.INCIDENT:
            tools = [
                ("parse_tracebacks", {}, "Extract tracebacks"),
                ("read_logs",        {"tail_chars": 5000}, "Read error log"),
                ("diagnostics",      {}, "Run data diagnostics"),
            ]
        elif run.intent == Intent.REPAIR:
            tools = [
                ("parse_tracebacks", {}, "Extract tracebacks"),
                ("diagnostics",      {}, "Check data integrity"),
            ]
        elif run.intent == Intent.TEST:
            tools = [
                ("diagnostics",   {}, "Run health check"),
                ("db_row_counts", {}, "Count DB rows"),
            ]
        elif run.intent == Intent.INSPECT_CODE:
            tools = [
                ("list_routes",   {}, "List all routes"),
                ("app_manifest",  {}, "App manifest"),
            ]
        else:
            tools = [("diagnostics", {}, "System diagnostics")]

        steps = []
        for i, (tool, params, desc) in enumerate(tools, 1):
            risk = assessor.assess(tool)
            steps.append(PlanStep(
                step_id=i, description=desc, tool=tool, params=params,
                risk=risk, requires_approval=assessor.requires_approval(risk),
            ))
        return steps

    def _summarize_context(self, ctx: dict) -> str:
        parts = []
        for key, val in list(ctx.items())[:8]:
            if isinstance(val, str):
                parts.append(f"{key}: {val[:200]}")
            elif isinstance(val, dict):
                parts.append(f"{key}: {json.dumps(val, default=str)[:200]}")
            elif isinstance(val, list):
                parts.append(f"{key}: [{len(val)} items]")
        return "\n".join(parts) or "(no context)"


# ─────────────────────────────────────────────────────────────────────────────
# Executor
# ─────────────────────────────────────────────────────────────────────────────

class Executor:
    """
    Runs each plan step using the EngineeringToolkit.
    - SAFE/LOW steps run automatically.
    - MEDIUM+ steps are returned as pending_action (require frontend approval).
    """

    def __init__(self, toolkit):
        self.tk = toolkit

    def run_step(self, step: PlanStep, run: AgentRun) -> bool:
        """
        Execute one step. Returns True if execution proceeded (even if tool failed).
        Returns False if step needs approval and was deferred.
        """
        t0 = time.monotonic()

        # Write steps that need approval — defer
        if step.requires_approval:
            run.pending_action = {
                "type":        step.tool,
                "params":      step.params,
                "description": step.description,
                "risk":        step.risk.value,
            }
            step.status = "awaiting_approval"
            run.add_think("EXECUTE",
                          f"⏸️ Approval needed: {step.tool}",
                          f"Risk: {step.risk.value} — {step.description}",
                          "warning", step.risk.value)
            return False

        # Execute read tool
        result = self._dispatch_tool(step.tool, step.params)
        ms = int((time.monotonic() - t0) * 1000)

        step.result = result
        if result.get("ok", False):
            step.status = "done"
            detail = str(result.get("data", result.get("output", "")))[:400]
            run.add_think("EXECUTE",
                          f"✅ {step.tool}: {result.get('output','ok')}",
                          detail, "ok", step.risk.value)
            # Fold tool output into context for subsequent steps
            run.context[f"result_{step.tool}_{step.step_id}"] = result.get("data") or result.get("output", "")
        else:
            step.status = "failed"
            run.add_think("EXECUTE",
                          f"❌ {step.tool} failed",
                          result.get("output", "unknown error"),
                          "error", step.risk.value)

        run.audit_entries.append({
            "step_id":   step.step_id,
            "tool":      step.tool,
            "status":    step.status,
            "ms":        ms,
            "output":    str(result.get("output", ""))[:200],
        })
        return True

    def _dispatch_tool(self, tool: str, params: dict) -> dict:
        tk = self.tk
        dispatch = {
            "app_manifest":           lambda p: tk.app_manifest(),
            "db_schema":              lambda p: tk.db_schema(),
            "db_row_counts":          lambda p: tk.db_row_counts(),
            "db_query":               lambda p: tk.db_query(p.get("query", "")),
            "db_analyze":             lambda p: tk.db_analyze(p.get("question", "")),
            "read_file":              lambda p: tk.read_file(p.get("path", "")),
            "search_code":            lambda p: tk.search_code(
                                          p.get("pattern", ""),
                                          p.get("path", ""),
                                          p.get("file_ext", ".py")),
            "inspect_route":          lambda p: tk.inspect_route(p.get("url", "")),
            "inspect_model":          lambda p: tk.inspect_model(p.get("model_name", "")),
            "list_routes":            lambda p: tk.list_routes(),
            "read_logs":              lambda p: tk.read_logs(int(p.get("tail_chars", 8000))),
            "parse_tracebacks":       lambda p: tk.parse_tracebacks(),
            "diagnostics":            lambda p: tk.diagnostics(),
            "run_management_command": lambda p: tk.run_management_command(
                                          p.get("command", "check"),
                                          p.get("args")),
        }
        fn = dispatch.get(tool)
        if fn:
            try:
                return fn(params)
            except Exception as e:
                return {"ok": False, "output": str(e), "data": None}
        return {"ok": False, "output": f"Unknown tool: {tool}", "data": None}


# ─────────────────────────────────────────────────────────────────────────────
# Verifier
# ─────────────────────────────────────────────────────────────────────────────

class Verifier:
    """
    After executing plan steps, checks whether the investigation is complete
    or whether a replan is needed.

    Verification checks:
      - For INCIDENT: is the traceback identified? Is a root cause proposed?
      - For REPAIR: was the patch applied? Did management check pass?
      - For others: did key steps succeed?
    """

    def verify(self, run: AgentRun) -> tuple[bool, str]:
        """Returns (passed: bool, reason: str)."""
        done   = [s for s in run.plan if s.status == "done"]
        failed = [s for s in run.plan if s.status == "failed"]
        deferred = [s for s in run.plan if s.status == "awaiting_approval"]

        # If there's a pending approval, verification pauses
        if deferred:
            run.add_think("VERIFY", "⏸️ Awaiting admin approval",
                          f"{deferred[0].description}", "warning")
            return True, "awaiting_approval"

        # Fail if any steps failed AND failed count >= done count (tie or majority).
        # Strictly greater-than allowed a 50/50 tie to pass silently; this closes that gap.
        # The `len(failed) > 0` guard avoids a spurious replan on an empty plan.
        if len(failed) > 0 and len(failed) >= len(done):
            reason = f"{len(failed)} of {len(run.plan)} steps failed"
            run.add_think("VERIFY", f"❌ Verification failed: {reason}",
                          "Will replan with adjusted approach", "error")
            return False, reason

        # For INCIDENT: we need at least one traceback or log result
        if run.intent == Intent.INCIDENT:
            has_trace = any(
                "traceback" in str(s.result or "").lower() or
                "exception" in str(s.result or "").lower() or
                (s.tool == "parse_tracebacks" and s.status == "done")
                for s in done
            )
            if not has_trace and run.context.get("tracebacks"):
                has_trace = True
            if not has_trace and not failed:
                run.add_think("VERIFY", "⚠️ No traceback data found",
                              "Logs may be empty or error may be intermittent", "warning")
                # Don't force replan if logs are simply empty
                return True, "no_traceback_but_ok"

        # For REPAIR: check if patch step was included
        if run.intent == Intent.REPAIR:
            patch_steps = [s for s in run.plan if s.tool == "apply_patch"]
            if patch_steps and all(s.status == "done" for s in patch_steps):
                # Run a quick system check to verify patch didn't break anything
                from .admin_agent import EngineeringToolkit
                tk = EngineeringToolkit()
                check_result = tk.run_management_command("check")
                if check_result["ok"]:
                    run.add_think("VERIFY", "✅ Django system check passed after patch",
                                  check_result["output"][:300], "ok")
                else:
                    run.add_think("VERIFY", "❌ System check failed after patch",
                                  check_result["output"][:300], "error")
                    return False, f"System check failed: {check_result['output'][:100]}"

        if done:
            run.add_think("VERIFY", f"✅ Verification passed ({len(done)} step(s) completed)",
                          "", "ok")
        return True, "ok"


# ─────────────────────────────────────────────────────────────────────────────
# Synthesizer  (LLM-driven — builds the final response from all evidence)
# ─────────────────────────────────────────────────────────────────────────────

class Synthesizer:
    """
    Takes all collected context + plan results and asks the LLM to produce
    the final, grounded response to the admin.
    """

    SYNTH_PROMPT = """You are the Admin Engineering Agent for a Django school discipline management system.

## ADMIN QUESTION
{message}

## INTENT
{intent}

## INVESTIGATION RESULTS
{results}

## INSTRUCTIONS
1. Answer the admin's question directly and specifically using the investigation results above.
2. If this is an INCIDENT: state the route → view → exception → root cause → confidence %.
3. If this is REPAIR: include the exact apply_patch action block for the fix.
4. If this is READ_DATA: answer factually from the data.
5. If this is ANALYSIS: explain the relationship/pattern found.
6. Be direct. No preamble. No "I'll help you with that."
7. If a write action is needed, end with the action block:

```action
{{"type": "ACTION_TYPE", "params": {{...}}, "description": "brief summary", "risk": "HIGH"}}
```

## WRITE ACTIONS AVAILABLE
create_stream, bulk_create_streams, delete_stream, reassign_stream_students, rename_stream,
add_student, bulk_add_students, edit_student, delete_student,
update_school, create_category, delete_category,
approve_teacher, suspend_teacher, reset_password, delete_report, recalculate_risk,
apply_patch(path, search, replace), create_file(path, content)
"""

    def __init__(self, ai_caller):
        self._call_ai = ai_caller

    def synthesize(self, run: AgentRun) -> str:
        results = self._collect_results(run)
        prompt  = self.SYNTH_PROMPT.format(
            message=run.message,
            intent=run.intent.value,
            results=results,
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user",   "content": run.message},
        ]
        result = self._call_ai(messages, max_tokens=2000, temperature=0.2)
        if result["success"]:
            run.provider = result.get("provider", "")
            return result["response"]
        return f"Investigation complete. {len([s for s in run.plan if s.status=='done'])} step(s) executed. AI synthesis unavailable: {result['response']}"

    def _collect_results(self, run: AgentRun) -> str:
        parts = []
        # Context gathered
        for key, val in list(run.context.items())[:10]:
            if isinstance(val, (str, list, dict)):
                snippet = json.dumps(val, default=str) if not isinstance(val, str) else val
                parts.append(f"[{key}]\n{snippet[:1500]}")
        # Step results
        for step in run.plan:
            if step.status == "done" and step.result:
                data = step.result.get("data") or step.result.get("output", "")
                snippet = json.dumps(data, default=str) if not isinstance(data, str) else data
                parts.append(f"[{step.tool} result]\n{snippet[:1500]}")
        return "\n\n---\n\n".join(parts) or "(no results gathered)"


# ─────────────────────────────────────────────────────────────────────────────
# AuditLog
# ─────────────────────────────────────────────────────────────────────────────

class AuditLog:
    """
    Builds a structured audit trail entry from the completed AgentRun.
    In production this would be written to a DB table. For now it's
    returned in-band with the response so the frontend can render it.
    """

    def record(self, run: AgentRun, final_response: str) -> list[dict]:
        entries = run.audit_entries.copy()
        entries.append({
            "phase":   "RESPONSE",
            "summary": final_response[:200],
            "intent":  run.intent.value,
            "mode":    run.mode,
            "replan_count": run.replan_count,
            "provider": run.provider,
            "total_ms": run.elapsed_ms(),
            "steps_done": len([s for s in run.plan if s.status == "done"]),
            "steps_failed": len([s for s in run.plan if s.status == "failed"]),
        })
        run.add_think("AUDIT",
                      f"📝 Audit recorded ({run.elapsed_ms()}ms total)",
                      f"Intent={run.intent.value} Provider={run.provider} Replans={run.replan_count}",
                      "ok")
        return entries


# ─────────────────────────────────────────────────────────────────────────────
# AgentPipeline — the main loop
# ─────────────────────────────────────────────────────────────────────────────

class AgentPipeline:
    """
    Orchestrates the full INTENT → CONTEXT → PLAN → RISK → EXECUTE → VERIFY → AUDIT → RESPOND loop.
    Supports up to MAX_REPLANS replan iterations on verification failure.
    """

    MAX_REPLANS = 2

    def __init__(self, toolkit, ai_caller):
        self.toolkit    = toolkit
        self.classifier = IntentClassifier()
        self.ctx_builder = ContextBuilder(toolkit)
        self.planner    = Planner(ai_caller)
        self.risk       = RiskAssessor()
        self.executor   = Executor(toolkit)
        self.verifier   = Verifier()
        self.synthesizer = Synthesizer(ai_caller)
        self.auditor    = AuditLog()

    def run(self, message: str, mode: str = "INSPECT",
            conversation_history: list | None = None) -> AgentRun:

        run = AgentRun(message=message, mode=mode)

        # ── 1. INTENT ─────────────────────────────────────────────────────────
        run.intent = self.classifier.classify(message)
        # If mode was explicitly set by user, it overrides classifier suggestion
        # but we keep intent for internal routing
        if mode == "INSPECT" and run.intent != Intent.READ_DATA:
            run.mode = self.classifier.to_mode(run.intent)
        else:
            run.mode = mode

        run.add_think("INTENT",
                      f"🎯 Intent: {run.intent.value}  Mode: {run.mode}",
                      f"Message classified as {run.intent.value}", "ok")

        # ── 2. CONTEXT ────────────────────────────────────────────────────────
        run.context = self.ctx_builder.build(run)

        # ── 3. PLAN → RISK → EXECUTE → VERIFY loop ────────────────────────────
        for loop_idx in range(self.MAX_REPLANS + 1):
            if loop_idx > 0:
                run.replan_count += 1
                run.add_think("PLAN",
                              f"🔄 Replanning (attempt {loop_idx + 1})",
                              "Previous verification failed — adjusting approach",
                              "warning")

            # PLAN
            run.plan = self.planner.plan(run)

            # RISK — annotate each step (already done in Planner but add summary)
            high_risk = [s for s in run.plan if self.risk.requires_approval(s.risk)]
            if high_risk:
                run.add_think("RISK",
                              f"⚠️ {len(high_risk)} step(s) require approval",
                              "\n".join(f"  {s.tool}: {s.risk.value}" for s in high_risk),
                              "warning")
            else:
                run.add_think("RISK", "✅ All steps are read-only / safe", "", "ok")

            # EXECUTE
            for step in run.plan:
                proceeded = self.executor.run_step(step, run)
                if not proceeded:
                    # Approval needed — stop execution and return to frontend
                    break

            # VERIFY
            passed, reason = self.verifier.verify(run)

            if passed:
                break
            # else loop for replan

        # ── 4. SYNTHESIZE RESPONSE ────────────────────────────────────────────
        # Check if we have a pending approval — skip synthesis, just explain
        if run.pending_action:
            run.final_response = self._approval_prompt(run)
        else:
            run.final_response = self.synthesizer.synthesize(run)

        # Extract action block from synthesis if present
        action = self._extract_action(run.final_response)
        if action:
            run.pending_action = action
            # Strip the block from display text
            run.final_response = re.sub(
                r"```action\s*\{.*?\}\s*```", "",
                run.final_response, flags=re.DOTALL | re.IGNORECASE
            ).strip()
            # Fix 1: if the LLM emitted only the action block with no prose,
            # stripping leaves an empty string — show the approval prompt instead.
            if not run.final_response:
                run.final_response = self._approval_prompt(run)

        # ── 5. AUDIT ──────────────────────────────────────────────────────────
        run.audit_entries = self.auditor.record(run, run.final_response)

        return run

    def _approval_prompt(self, run: AgentRun) -> str:
        action = run.pending_action
        risk_val = action.get("risk", "MEDIUM")
        return (
            f"I need your approval before proceeding.\n\n"
            f"**Planned action:** {action.get('description', action.get('type',''))}\n"
            f"**Tool:** `{action.get('type','')}`\n"
            f"**Risk level:** {risk_val}\n\n"
            f"Review the parameters below and click **Execute Now** to confirm, or **Cancel** to abort."
        )

    def _extract_action(self, text: str) -> dict | None:
        pattern = r"```action\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return None
