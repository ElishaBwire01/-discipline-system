# core/ai_chat.py
import json
import os
import re
import time
import logging
from datetime import datetime, timedelta
from core.ai_providers import load_provider_keys, load_models, PROVIDERS, get_providers_for_task, configured_providers

import requests
from django.db.models import Avg, Count, Q, Sum
try:
    # Import django timezone if available
    from django.utils import timezone  # type: ignore
except Exception:
    timezone = None

# Models are imported lazily inside methods so this module can be imported
# in non-Django contexts (tests, scripts) without failing on Django setup.


class PollinationAIChat:
    """Enhanced AI Chat with full database integration"""

    def __init__(self):
        # Configure logger
        self.logger = logging.getLogger("core.ai_chat")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
            )
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Provider configuration is centralized in core.ai_providers
        # Default provider order is the set of configured providers (those with keys)
        self.providers = configured_providers()
        self.provider_keys = load_provider_keys()
        self.models = load_models()

        # Cache for frequently accessed data
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = int(os.environ.get("AI_CACHE_SECONDS", "300"))

        # Retry/backoff settings
        self.max_retries = int(os.environ.get("AI_MAX_RETRIES", "2"))
        self.backoff_factor = float(os.environ.get("AI_BACKOFF_FACTOR", "0.5"))

    def _get_cached(self, key):
        """Get cached data if valid"""
        if key in self._cache and key in self._cache_time:
            delta = self._now() - self._cache_time[key]
            if delta.total_seconds() < self._cache_duration:
                return self._cache[key]
        return None

    def _set_cache(self, key, value):
        """Set cached data"""
        self._cache[key] = value
        self._cache_time[key] = self._now()

    def _now(self):
        """Return current timezone-aware datetime. Prefer Django timezone when available."""
        try:
            if timezone is not None:
                return timezone.now()
        except Exception:
            pass
        # Fallback to UTC datetime
        from datetime import datetime, timezone as dt_tz

        return datetime.now(dt_tz.utc)

    def get_system_prompt(self, context=None):
        """Get enhanced system prompt with context"""
        # The system prompt provides guidance but avoids unsafe "FULL ACCESS" claims.
        base_prompt = """You are an AI Education Assistant with authorized access to the school's discipline management system. You may reference summarized, authorized student and report data when answering. Do not request or reveal secrets such as system keys or credentials.

CAPABILITIES:
1. Query student records by name, admission number, stream, or form
2. Retrieve discipline reports with dates, categories, and ratings
3. Generate school-wide statistics and analytics
4. Provide personalized student recommendations
5. Answer questions about Kenyan Education Law
6. Analyze trends and patterns in student behavior
7. Compare students, streams, and classes
8. Track intervention effectiveness

RESPONSE FORMAT:
- Be conversational and helpful
- Use bullet points for lists
- Bold important information
- Provide specific numbers and dates when available
- If data is not found, suggest alternatives

PERSONALITY:
- Professional but friendly
- Proactive in offering help
- Clear and concise
- Confident but not arrogant

ACCESSIBLE DATA:
- All students (name, admission, stream, form, risk score)
- All discipline reports (date, category, rating, points)
- Teacher profiles and assignments
- School statistics (totals, averages, distributions)
- Academic terms and streams
- Category breakdowns and trends

RESPONSE GUIDELINES:
1. Always confirm what you found
2. If multiple matches, list them
3. Offer to drill down deeper
4. Suggest related information they might need
5. Reference Kenyan laws when relevant

You are the ultimate assistant for this school's discipline management - use your database access to provide comprehensive, accurate, and helpful responses."""

        if context:
            # Only include non-sensitive context fields (do not dump raw env values)
            safe_context = dict(context)
            safe_context.pop("raw_env", None)
            return base_prompt + f"\n\nCURRENT CONTEXT:\n{json.dumps(safe_context, indent=2)}"

        return base_prompt

    def get_student_data(self, student_id=None, name=None, admission=None):
        """Fetch detailed student data from database"""
        try:
            from .models import Student, TeacherProfile
        except Exception:
            return {"error": "Django models not available in this environment"}
        try:
            if student_id:
                student = Student.objects.get(id=student_id, is_active=True)
            elif admission:
                student = Student.objects.get(
                    admission_number=admission, is_active=True
                )
            elif name:
                # Try exact match first, then partial
                student = Student.objects.filter(
                    name__iexact=name, is_active=True
                ).first()
                if not student:
                    student = Student.objects.filter(
                        name__icontains=name, is_active=True
                    ).first()
            else:
                return None

            if not student:
                return None

            # Get reports
            reports = student.reports.select_related(
                "category", "reported_by"
            ).order_by("-reported_at")
            total_reports = reports.count()

            # Category breakdown
            category_breakdown = list(
                reports.values("category__name")
                .annotate(count=Count("id"))
                .order_by("-count")
            )

            # Get class teacher
            class_teacher = None
            if student.stream:
                teacher_profile = TeacherProfile.objects.filter(
                    assigned_stream=student.stream,
                    assigned_form=student.form,
                    is_approved=True,
                ).first()
                if teacher_profile:
                    class_teacher = {
                        "name": teacher_profile.user.get_full_name()
                        or teacher_profile.user.username,
                        "email": teacher_profile.user.email,
                        "phone": teacher_profile.phone_number,
                    }

            # Recent reports with details
            recent_reports = []
            for report in reports[:10]:
                recent_reports.append(
                    {
                        "date": report.reported_at.strftime("%Y-%m-%d %H:%M"),
                        "category": report.category.name,
                        "rating": report.get_rating_display(),
                        "points": report.points,
                        "reported_by": report.reported_by.get_full_name()
                        or report.reported_by.username,
                        "comments": (
                            report.comments[:100] + "..."
                            if len(report.comments) > 100
                            else report.comments
                        ),
                    }
                )

            # Calculate days since last incident
            days_since = None
            if student.last_incident_date:
                delta = self._now() - student.last_incident_date
                days_since = delta.days

            data = {
                "id": student.id,
                "name": student.name,
                "admission_number": student.admission_number,
                "stream": student.stream.name if student.stream else "Not Assigned",
                "form": student.form,
                "year": student.year,
                "risk_score": student.risk_score,
                "risk_level": student.risk_level,
                "total_reports": total_reports,
                "intervention_count": student.intervention_count,
                "days_since_last_incident": days_since,
                "is_active": student.is_active,
                "created_at": student.created_at.strftime("%Y-%m-%d"),
                "class_teacher": class_teacher,
                "category_breakdown": category_breakdown,
                "recent_reports": recent_reports,
                "optional_notes": student.optional_notes,
            }

            # Cache the data
            self._set_cache(f"student_{student.id}", data)

            return data

        except Student.DoesNotExist:
            return None
        except Exception as e:
            return {"error": str(e)}

    def get_school_stats(self):
        """Get comprehensive school statistics"""
        cache_key = "school_stats"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            from .models import Student, Stream, DisciplineReport, TeacherProfile

            students = Student.objects.filter(is_active=True)
            total_students = students.count()

            # Risk distribution
            critical = students.filter(risk_level="CRITICAL").count()
            warning = students.filter(risk_level="WARNING").count()
            good = students.filter(risk_level="GOOD").count()

            # Stream breakdown
            stream_stats = {}
            for stream in Stream.objects.filter(is_active=True):
                count = students.filter(stream=stream).count()
                if count > 0:
                    stream_stats[stream.name] = count

            # Form breakdown
            form_stats = {}
            for form in Student.FORM_CHOICES:
                form_name = form[0]
                count = students.filter(form=form_name).count()
                if count > 0:
                    form_stats[form_name] = count

            # Report statistics
            total_reports = DisciplineReport.objects.count()
            reports_today = DisciplineReport.objects.filter(
                reported_at__date=self._now().date()
            ).count()
            reports_this_week = DisciplineReport.objects.filter(
                reported_at__week=self._now().isocalendar()[1]
            ).count()

            # Top categories
            top_categories = list(
                DisciplineReport.objects.values("category__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
            )

            # Online teachers
            online_teachers = TeacherProfile.objects.filter(is_online=True).count()
            total_teachers = TeacherProfile.objects.filter(is_approved=True).count()

            # Average risk
            avg_risk = students.aggregate(avg=Avg("risk_score"))["avg"] or 0

            stats = {
                "total_students": total_students,
                "critical_count": critical,
                "warning_count": warning,
                "good_count": good,
                "avg_risk_score": round(avg_risk, 1),
                "total_reports": total_reports,
                "reports_today": reports_today,
                "reports_this_week": reports_this_week,
                "online_teachers": online_teachers,
                "total_teachers": total_teachers,
                "top_categories": top_categories,
                "stream_breakdown": stream_stats,
                "form_breakdown": form_stats,
                "timestamp": timezone.now().isoformat(),
            }

            self._set_cache(cache_key, stats)
            return stats

        except Exception as e:
            return {"error": str(e)}

    def search_students(self, query):
        """Search for students by name or admission number"""
        cache_key = f"search_{query}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            from .models import Student

            results = []

            # Search by admission number
            if query.isdigit():
                students = Student.objects.filter(
                    admission_number__icontains=query, is_active=True
                )[:5]
            else:
                # Search by name
                students = Student.objects.filter(
                    Q(name__icontains=query) | Q(name__istartswith=query),
                    is_active=True,
                )[:10]

            for student in students:
                results.append(
                    {
                        "id": student.id,
                        "name": student.name,
                        "admission_number": student.admission_number,
                        "stream": student.stream.name if student.stream else "N/A",
                        "form": student.form,
                        "risk_score": student.risk_score,
                        "risk_level": student.risk_level,
                        "total_reports": student.reports.count(),
                    }
                )

            self._set_cache(cache_key, results)
            return results

        except Exception as e:
            return {"error": str(e)}

    def get_stream_analysis(self, stream_id):
        """Get detailed analysis for a specific stream"""
        try:
            from .models import Stream, Student

            stream = Stream.objects.get(id=stream_id, is_active=True)
            students = Student.objects.filter(stream=stream, is_active=True)

            total = students.count()
            if total == 0:
                return {
                    "stream": stream.name,
                    "message": "No students in this stream",
                }

            critical = students.filter(risk_level="CRITICAL").count()
            warning = students.filter(risk_level="WARNING").count()
            good = students.filter(risk_level="GOOD").count()
            avg_risk = students.aggregate(avg=Avg("risk_score"))["avg"] or 0

            # Top offenders
            top_offenders = list(
                students.annotate(report_count=Count("reports"))
                .filter(report_count__gt=0)
                .order_by("-report_count")[:5]
                .values("name", "admission_number", "report_count", "risk_score")
            )

            return {
                "stream": stream.name,
                "total_students": total,
                "critical_count": critical,
                "warning_count": warning,
                "good_count": good,
                "average_risk": round(avg_risk, 1),
                "top_offenders": top_offenders,
            }

        except Stream.DoesNotExist:
            return {"error": "Stream not found"}
        except Exception as e:
            return {"error": str(e)}

    def get_all_students_summary(self):
        """Get summary of all students with basic info"""
        cache_key = os.environ.get("ALL_STUDENTS_SUMMARY_VALUE", "all_students_summary")
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            from .models import Student

            students = Student.objects.filter(is_active=True).select_related("stream")
            summary = []

            for student in students[:50]:  # Limit to 50 for performance
                summary.append(
                    {
                        "id": student.id,
                        "name": student.name,
                        "admission": student.admission_number,
                        "stream": student.stream.name if student.stream else "N/A",
                        "form": student.form,
                        "risk": student.risk_score,
                        "level": student.risk_level,
                        "reports": student.reports.count(),
                    }
                )

            self._set_cache(cache_key, summary)
            return summary

        except Exception as e:
            return {"error": str(e)}

    def _try_model(self, messages, model_name):
        """Deprecated generic call - preserved for compatibility. Use provider-specific callers.

        This function is retained for backwards compatibility but will attempt to call
        providers in order using `_call_provider`.
        """
        return {"success": False, "error": "Use provider-specific calls via _call_provider"}

    def _call_provider(self, provider, messages):
        """Call a single provider and return standardized result dict.

        Result: {success: bool, response: str, usage: dict, model_used: str, error: str}
        """
        api_key = self.provider_keys.get(provider)
        if not api_key:
            self.logger.debug("Skipping provider %s (no API key)", provider)
            return {"success": False, "error": "missing_api_key"}

        model_name = self.models.get(provider)

        # Build payloads and endpoints per provider
        try:
            if provider in ("openai", "openrouter", "groq"):
                # OpenAI-compatible chat completion (with provider-specific tweaks)
                if provider == "openai":
                    url = os.environ.get("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
                elif provider == "openrouter":
                    url = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
                else:  # groq
                    url = os.environ.get("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                # Groq uses a slightly different payload key for max tokens and may rate-limit.
                if provider == "groq":
                    max_tokens = int(os.environ.get("AI_MAX_TOKENS", "2048"))
                    temperature = float(os.environ.get("AI_TEMPERATURE", "1.0"))
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_completion_tokens": max_tokens,
                        "top_p": float(os.environ.get("AI_TOP_P", "1")),
                        "stream": False,
                    }

                    # Post and handle adaptive throttling on 429 by reducing max tokens once
                    resp = requests.post(url, headers=headers, json=payload, timeout=30)
                    if resp.status_code == 429:
                        # honor Retry-After header if present
                        try:
                            retry_after = int(resp.headers.get("Retry-After") or resp.headers.get("retry-after") or 0)
                        except Exception:
                            retry_after = 0
                        self.logger.info("Groq rate-limited (Retry-After=%s). Attempting adaptive token reduction.", retry_after)
                        try:
                            if retry_after:
                                time.sleep(min(int(retry_after), 60))
                        except Exception:
                            pass

                        # Reduce tokens and retry once
                        reduced = max(64, max_tokens // 2)
                        if reduced < max_tokens:
                            payload["max_completion_tokens"] = reduced
                            self.logger.info("Retrying Groq with reduced tokens=%s", reduced)
                            resp = requests.post(url, headers=headers, json=payload, timeout=30)

                    if resp.status_code != 200:
                        try:
                            body = resp.text
                        except Exception:
                            body = "<unreadable>"
                        retry_after = 0
                        try:
                            retry_after = int(resp.headers.get("Retry-After") or resp.headers.get("retry-after") or 0)
                        except Exception:
                            retry_after = 0
                        safe_headers = {k: v for k, v in resp.headers.items() if k.lower() != "authorization"}
                        self.logger.warning(
                            "Provider %s returned %s for %s (model=%s): %s headers=%s",
                            provider,
                            resp.status_code,
                            url,
                            model_name,
                            (body[:1000] + "...") if len(body) > 1000 else body,
                            safe_headers,
                        )
                        return {"success": False, "error": f"http_{resp.status_code}", "raw": body, "retry_after": retry_after}
                    try:
                        data = resp.json()
                    except Exception:
                        data = None
                else:
                    # Standard OpenAI-style payload for openai/openrouter
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": float(os.environ.get("AI_TEMPERATURE", "0.7")),
                        "max_tokens": int(os.environ.get("AI_MAX_TOKENS", "1024")),
                        "top_p": float(os.environ.get("AI_TOP_P", "1")),
                    }
                    resp = requests.post(url, headers=headers, json=payload, timeout=30)
                    if resp.status_code != 200:
                        try:
                            body = resp.text
                        except Exception:
                            body = "<unreadable>"
                        retry_after = 0
                        try:
                            retry_after = int(resp.headers.get("Retry-After") or resp.headers.get("retry-after") or 0)
                        except Exception:
                            retry_after = 0
                        safe_headers = {k: v for k, v in resp.headers.items() if k.lower() != "authorization"}
                        self.logger.warning(
                            "Provider %s returned %s for %s (model=%s): %s headers=%s",
                            provider,
                            resp.status_code,
                            url,
                            model_name,
                            (body[:1000] + "...") if len(body) > 1000 else body,
                            safe_headers,
                        )
                        return {"success": False, "error": f"http_{resp.status_code}", "raw": body, "retry_after": retry_after}
                    try:
                        data = resp.json()
                    except Exception:
                        data = None

                # Parse OpenAI-style response if present
                try:
                    if isinstance(data, dict) and data.get("choices"):
                        # Chat completions v1
                        text = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
                    else:
                        text = json.dumps(data)
                except Exception:
                    text = json.dumps(data) if data is not None else ""

                return {"success": True, "response": text, "usage": data.get("usage", {}) if isinstance(data, dict) else {}, "model_used": model_name}

            if provider == "gemini":
                # Google Generative Language: try multiple payload shapes to maximize compatibility
                model = model_name
                base_url = os.environ.get("GEMINI_URL") or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                params = {"key": api_key} if api_key and not api_key.startswith("ya29") else {}

                text_input = messages[-1]["content"]
                temperature = float(os.environ.get("AI_TEMPERATURE", "0.7"))
                max_output_tokens = int(os.environ.get("AI_MAX_TOKENS", "512"))

                # Define a set of payload variants (newer and older shapes)
                payload_variants = [
                    # try newer generateText-like shape
                    {"prompt": {"text": text_input}, "temperature": temperature, "maxOutputTokens": max_output_tokens},
                    # alternative top-level input
                    {"input": text_input, "temperature": temperature, "maxOutputTokens": max_output_tokens},
                    # older 'contents' shape (fallback)
                    {"contents": [{"parts": [{"text": text_input}]}], "temperature": temperature, "maxOutputTokens": max_output_tokens},
                ]

                last_body = None
                last_retry_after = 0
                for payload in payload_variants:
                    try:
                        resp = requests.post(base_url, params=params or None, json=payload, timeout=30)
                    except Exception as e:
                        self.logger.debug("Gemini request error for payload variant: %s", e)
                        resp = None

                    if not resp:
                        continue

                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                        except Exception:
                            data = None
                        # Try a few likely locations for generated text
                        text = None
                        if isinstance(data, dict):
                            # common shapes
                            if "candidates" in data:
                                try:
                                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                                except Exception:
                                    pass
                            if not text and "output" in data:
                                text = data.get("output")
                            if not text and "choices" in data:
                                try:
                                    text = data["choices"][0].get("message", {}).get("content")
                                except Exception:
                                    pass
                        if not text:
                            # last resort stringify
                            text = json.dumps(data)
                        return {"success": True, "response": text, "usage": {}, "model_used": model}

                    # On 400, check for schema complaints like unknown 'temperature' and retry without temperature for this shape
                    try:
                        body = resp.text
                    except Exception:
                        body = "<unreadable>"
                    last_body = body
                    try:
                        last_retry_after = int(resp.headers.get("Retry-After") or resp.headers.get("retry-after") or 0)
                    except Exception:
                        last_retry_after = 0

                    if resp.status_code == 400 and "temperature" in (body or ""):
                        self.logger.info("Gemini rejected 'temperature' field for variant; retrying payload without it")
                        payload_no_temp = {k: v for k, v in payload.items() if k != "temperature"}
                        try:
                            resp2 = requests.post(base_url, params=params or None, json=payload_no_temp, timeout=30)
                        except Exception as e:
                            self.logger.debug("Gemini retry error: %s", e)
                            resp2 = None

                        if resp2 and resp2.status_code == 200:
                            try:
                                data = resp2.json()
                            except Exception:
                                data = None
                            text = None
                            if isinstance(data, dict) and "candidates" in data:
                                try:
                                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                                except Exception:
                                    pass
                            if not text:
                                text = json.dumps(data)
                            return {"success": True, "response": text, "usage": {}, "model_used": model}

                    safe_headers = {k: v for k, v in resp.headers.items() if k.lower() != "authorization"}
                    self.logger.warning(
                        "Provider %s returned %s for %s (model=%s) while trying Gemini variant: %s headers=%s",
                        provider,
                        resp.status_code,
                        base_url,
                        model,
                        (body[:1000] + "...") if len(body) > 1000 else body,
                        safe_headers,
                    )

                # If we exit the loop without success, return last seen error
                return {"success": False, "error": f"http_{resp.status_code if resp else 'no_response'}", "raw": last_body, "retry_after": last_retry_after}

            # Pollinations provider removed from supported providers per project policy

            return {"success": False, "error": "unknown_provider"}
        except Exception as e:
            self.logger.exception("Provider %s call failed", provider)
            return {"success": False, "error": str(e)}

    def _call_providers_in_order(self, messages, provider_order=None):
        """Try providers in the given order (or configured order) with retries and exponential backoff.

        `provider_order` may be supplied (list of provider keys) to prioritize certain
        providers for a task. Only providers with configured API keys are attempted.
        """
        last_error = None
        order = provider_order or self.providers
        for provider in order:
            # Skip providers without keys
            if not self.provider_keys.get(provider):
                self.logger.debug("Provider %s skipped (no key)", provider)
                continue

            for attempt in range(0, self.max_retries + 1):
                if attempt > 0:
                    backoff = self.backoff_factor * (2 ** (attempt - 1))
                    time.sleep(backoff)
                self.logger.info("Trying provider %s attempt %d", provider, attempt + 1)
                result = self._call_provider(provider, messages)
                if result.get("success"):
                    result["provider"] = provider
                    return result
                # If provider asked for a retry-after (rate limit), honor it before next attempt
                retry_after = result.get("retry_after")
                if retry_after and (result.get("error") or "").startswith("http_429"):
                    self.logger.info("Provider %s asked to retry after %s seconds", provider, retry_after)
                    try:
                        time.sleep(int(retry_after))
                    except Exception:
                        pass

                last_error = result.get("error") or result.get("raw")
                # If provider reports invalid model or missing key, stop retrying this provider
                if last_error in ("missing_api_key", "invalid_model"):
                    break

        return {"success": False, "error": last_error or "all_providers_failed"}

    def _parse_user_intent(self, message):
        """Parse user message to understand intent and extract entities"""
        message_lower = message.lower()

        intent = {"type": "general", "entities": {}, "action": None}

        # Check for student queries
        student_patterns = [
            r"student\s+(\w+)",
            r"admission\s*[#:]*\s*(\d+)",
            r"pupil\s+(\w+)",
            r"learner\s+(\w+)",
            r"about\s+(\w+)",
        ]

        for pattern in student_patterns:
            match = re.search(pattern, message_lower)
            if match:
                intent["type"] = "student"
                intent["entities"]["query"] = match.group(1)
                break

        # Check for admission number
        admission_match = re.search(r"\b(\d{4,6})\b", message)
        if admission_match:
            intent["type"] = "student"
            intent["entities"]["admission"] = admission_match.group(1)

        # Check for statistics queries
        if any(
            word in message_lower
            for word in ["how many", "total", "count", "statistics", "stats"]
        ):
            intent["type"] = "stats"

        # Check for stream queries
        stream_match = re.search(r"stream\s+(\w+)", message_lower)
        if stream_match:
            intent["type"] = "stream"
            intent["entities"]["stream"] = stream_match.group(1)

        # Check for reports queries
        if any(
            word in message_lower for word in ["report", "case", "offense", "incident"]
        ):
            intent["action"] = "reports"

        return intent

    def _generate_fallback_response(self, intent, data):
        """Generate intelligent fallback response based on intent and data"""
        response = ""

        if intent["type"] == "student" and data:
            student_data = data
            name = student_data.get("name", "the student")

            response = f"📊 **Student Profile: {name}**\n\n"
            response += (
                f"• **Admission:** {student_data.get('admission_number', 'N/A')}\n"
            )
            response += f"• **Stream:** {student_data.get('stream', 'Not Assigned')}\n"
            response += f"• **Form:** {student_data.get('form', 'N/A')}\n"
            response += (
                f"• **Risk Level:** {student_data.get('risk_level', 'Unknown')}\n"
            )
            response += f"• **Risk Score:** {student_data.get('risk_score', 0)}%\n"
            response += f"• **Total Reports:** {student_data.get('total_reports', 0)}\n"

            if student_data.get("days_since_last_incident") is not None:
                response += f"• **Days Since Last Incident:** {student_data['days_since_last_incident']}\n"

            if student_data.get("intervention_count", 0) > 0:
                response += (
                    f"• **Interventions:** {student_data['intervention_count']}\n"
                )

            if student_data.get("class_teacher"):
                response += (
                    f"• **Class Teacher:** {student_data['class_teacher']['name']}\n"
                )

            # Category breakdown
            if student_data.get("category_breakdown"):
                response += "\n**Top Offenses:**\n"
                for cat in student_data["category_breakdown"][:3]:
                    response += f"• {cat['category__name']}: {cat['count']} reports\n"

            # Recent reports
            if student_data.get("recent_reports"):
                response += "\n**Recent Reports:**\n"
                for report in student_data["recent_reports"][:3]:
                    response += f"• {report['date']} - {report['category']} ({report['rating']})\n"

            # Recommendations based on risk level
            if student_data.get("risk_level") == "CRITICAL":
                response += "\n⚠️ **Immediate Action Required:**\n"
                response += "1. Schedule parent-teacher conference TODAY\n"
                response += "2. Refer to school counselor\n"
                response += "3. Create behavior intervention plan\n"
            elif student_data.get("risk_level") == "WARNING":
                response += "\n📋 **Recommended Actions:**\n"
                response += "1. Schedule parent meeting within 1 week\n"
                response += "2. Implement behavior tracking\n"
                response += "3. Assign mentor or buddy\n"
            else:
                response += "\n✅ **Status: Good**\n"
                response += "Continue positive reinforcement and monitoring.\n"

        elif intent["type"] == "stats":
            stats = data.get("stats", {})
            response = f"📊 **School Statistics**\n\n"
            response += f"• **Total Students:** {stats.get('total_students', 0)}\n"
            response += f"• **Critical Cases:** {stats.get('critical_count', 0)}\n"
            response += f"• **Warning Cases:** {stats.get('warning_count', 0)}\n"
            response += f"• **Good Status:** {stats.get('good_count', 0)}\n"
            response += f"• **Average Risk:** {stats.get('avg_risk_score', 0)}%\n"
            response += f"• **Total Reports:** {stats.get('total_reports', 0)}\n"
            response += f"• **Reports Today:** {stats.get('reports_today', 0)}\n"
            response += f"• **Online Teachers:** {stats.get('online_teachers', 0)}/{stats.get('total_teachers', 0)}\n"

            if stats.get("top_categories"):
                response += "\n**Top Offense Categories:**\n"
                for cat in stats["top_categories"]:
                    response += f"• {cat['category__name']}: {cat['count']} reports\n"

            if stats.get("stream_breakdown"):
                response += "\n**Stream Breakdown:**\n"
                for name, count in stats["stream_breakdown"].items():
                    response += f"• {name}: {count} students\n"

        elif intent["type"] == "stream" and data:
            stream_data = data
            response = (
                f"📊 **Stream Analysis: {stream_data.get('stream', 'Unknown')}**\n\n"
            )
            response += (
                f"• **Total Students:** {stream_data.get('total_students', 0)}\n"
            )
            response += f"• **Critical:** {stream_data.get('critical_count', 0)}\n"
            response += f"• **Warning:** {stream_data.get('warning_count', 0)}\n"
            response += f"• **Good:** {stream_data.get('good_count', 0)}\n"
            response += f"• **Average Risk:** {stream_data.get('average_risk', 0)}%\n"

            if stream_data.get("top_offenders"):
                response += "\n**Top Offenders:**\n"
                for student in stream_data["top_offenders"]:
                    response += f"• {student['name']} ({student['admission_number']}): {student['report_count']} reports\n"

        else:
            response = "🤖 I'm here to help you with the school discipline system.\n\n"
            response += "**What I can do:**\n"
            response += "• 📊 Show school statistics\n"
            response += "• 👤 Look up student profiles\n"
            response += "• 📋 View discipline reports\n"
            response += "• 📈 Analyze stream/class performance\n"
            response += "• 📚 Answer questions about Kenyan Education Law\n\n"
            response += "**Try asking:**\n"
            response += "• 'Show me student John Doe'\n"
            response += "• 'How many students are in the system?'\n"
            response += "• 'What are the reports for admission 9486?'\n"
            response += "• 'Analyze the Gonza stream'\n"
            response += "• 'What does the Education Act say about discipline?'"

        return response

    def chat(self, user_message, student_id=None, conversation_history=None):
        """Enhanced chat with full database integration"""

        # Parse user intent
        intent = self._parse_user_intent(user_message)

        # Get student data if referenced
        student_data = None
        if intent["type"] == "student":
            query = intent["entities"].get("query")
            admission = intent["entities"].get("admission")

            if admission:
                student_data = self.get_student_data(admission=admission)
            elif query:
                student_data = self.get_student_data(name=query)
            elif student_id:
                student_data = self.get_student_data(student_id=student_id)

        # Get school stats if needed
        school_stats = None
        if intent["type"] == "stats":
            school_stats = self.get_school_stats()

        # Get stream analysis if needed
        stream_data = None
        if intent["type"] == "stream":
            stream_name = intent["entities"].get("stream")
            if stream_name:
                try:
                    from .models import Stream

                    stream = Stream.objects.filter(name__icontains=stream_name).first()
                    if stream:
                        stream_data = self.get_stream_analysis(stream.id)
                except Exception:
                    stream_data = None

        # Build context
        context = {
            "intent": intent,
            "student": student_data,
            "stats": school_stats,
            "stream_analysis": stream_data,
            "timestamp": self._now().isoformat(),
        }

        # If student data is not found by AI, fallback to data-driven response
        if not student_data and intent["type"] == "student":
            fallback_response = self._generate_fallback_response(intent, None)
            return {
                "success": True,
                "response": fallback_response,
                "mode": "data_fallback",
                "context": context,
            }

        # If stats requested and we have data
        if intent["type"] == "stats" and school_stats:
            fallback_response = self._generate_fallback_response(intent, context)
            return {
                "success": True,
                "response": fallback_response,
                "mode": "data_fallback",
                "context": context,
            }

        # If stream data requested
        if intent["type"] == "stream" and stream_data:
            fallback_response = self._generate_fallback_response(intent, context)
            return {
                "success": True,
                "response": fallback_response,
                "mode": "data_fallback",
                "context": context,
            }

        # Build messages for AI
        messages = [{"role": "system", "content": self.get_system_prompt(context)}]

        if conversation_history:
            for msg in conversation_history[-10:]:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        # Determine provider order based on task routing (if any)
        task_type = intent.get("type")
        # Map internal intent types to routing keys when possible
        routing_key = None
        if task_type == "student":
            routing_key = "report_generation"
        elif task_type == "stats":
            routing_key = "report_generation"
        elif intent.get("action") == "reports":
            routing_key = "report_generation"
        # Allow explicit short/long hints in message (quick heuristic)
        if any(word in user_message.lower() for word in ["short", "brief", "one-liner"]):
            routing_key = "short_responses"
        if any(word in user_message.lower() for word in ["analyze", "deep", "long", "detailed", "thorough"]):
            routing_key = routing_key or "long_context_analysis"

        provider_order = get_providers_for_task(routing_key) if routing_key else None

        # Try providers in order with automatic failover
        provider_result = self._call_providers_in_order(messages, provider_order=provider_order)
        if provider_result.get("success"):
            return {
                "success": True,
                "response": provider_result["response"],
                "usage": provider_result.get("usage", {}),
                "mode": "ai",
                "provider": provider_result.get("provider"),
                "model_used": provider_result.get("model_used"),
                "context": context,
            }

        # If all providers failed, fall back to data-driven response
        self.logger.warning("All AI providers failed: %s", provider_result.get("error"))
        fallback_response = self._generate_fallback_response(intent, context)
        return {
            "success": True,
            "response": fallback_response,
            "mode": "data_fallback",
            "context": context,
        }
