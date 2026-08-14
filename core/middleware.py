# core/middleware.py
import json
import os
import sys
import traceback
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


class OnlineStatusMiddleware(MiddlewareMixin):
    """Update user's online status on each request."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                from .models import TeacherProfile
                profile = TeacherProfile.objects.get(user=request.user)
                profile.last_activity = timezone.now()
                profile.is_online = True
                profile.save(update_fields=['last_activity', 'is_online'])
            except TeacherProfile.DoesNotExist:
                pass
            except Exception as e:
                print(f"OnlineStatusMiddleware error: {e}")
        
        response = self.get_response(request)
        return response


class ErrorLoggingMiddleware(MiddlewareMixin):
    """Middleware to log all errors and store them for the 500 page."""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log the error
            self._log_error(request, e)

            # For API requests, return JSON error
            if request.path.startswith("/api/"):
                return JsonResponse(
                    {"error": str(e), "type": type(e).__name__, "path": request.path},
                    status=500,
                )

            # Re-raise for Django to handle
            raise

    def process_exception(self, request, exception):
        """Process exceptions that occur during view rendering."""
        self._log_error(request, exception)

        # For API requests, return JSON error
        if request.path.startswith("/api/"):
            return JsonResponse(
                {
                    "error": str(exception),
                    "type": type(exception).__name__,
                    "path": request.path,
                },
                status=500,
            )

        # Return None to let Django handle it
        return None

    def _log_error(self, request, exception):
        """Log error details to console and file."""
        error_type = type(exception).__name__
        error_message = str(exception)
        error_traceback = traceback.format_exc()

        # Print to console
        print("\n" + "=" * 80)
        print("?? DJANGO ERROR DETECTED")
        print("=" * 80)
        print(f"? Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"?? Error Type: {error_type}")
        print(f"?? Error Message: {error_message}")
        print(f"?? URL: {request.path}")
        print(
            f"?? User: {request.user.username if request.user.is_authenticated else 'Anonymous'}"
        )
        print(f"?? Method: {request.method}")
        print(f"?? IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
        print("-" * 80)
        print("?? Full Traceback:")
        print(error_traceback)
        print("=" * 80 + "\n")

        # Log to file
        log_file = settings.BASE_DIR / "error_logs.txt"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL: {request.path}\n")
                f.write(f"Method: {request.method}\n")
                f.write(
                    f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}\n"
                )
                f.write(f"IP: {request.META.get('REMOTE_ADDR', 'Unknown')}\n")
                f.write(f"Error: {error_type}: {error_message}\n")
                f.write(f"{'-'*80}\n")
                f.write(error_traceback)
                f.write(f"\n{'='*80}\n")
        except Exception as log_error:
            # If we can't write to log file, at least print the error
            print(f"?? Could not write to log file: {log_error}")


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log all requests for debugging."""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Log request
        self._log_request(request)

        response = self.get_response(request)

        # Log response
        self._log_response(request, response)

        return response

    def _log_request(self, request):
        """Log incoming request details."""
        # Only log in debug mode or for specific paths
        if not settings.DEBUG and not request.path.startswith("/admin-dashboard/"):
            return

        print(f"\n?? REQUEST: {request.method} {request.path}")
        if request.user.is_authenticated:
            print(f"?? User: {request.user.username}")
        if request.method == "POST":
            # Don't log passwords
            post_data = {
                k: v for k, v in request.POST.items() if "password" not in k.lower()
            }
            if post_data:
                print(f"?? POST Data: {post_data}")

    def _log_response(self, request, response):
        """Log response details."""
        if not settings.DEBUG and not request.path.startswith("/admin-dashboard/"):
            return

        if hasattr(response, "status_code"):
            status = response.status_code
            if status >= 400:
                print(f"? RESPONSE: {status} ERROR - {request.path}")
            else:
                print(f"? RESPONSE: {status} - {request.path}")


class SessionDebugMiddleware(MiddlewareMixin):
    """Middleware to debug session issues."""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Check session before request
        if settings.DEBUG and request.user.is_authenticated:
            session_key = request.session.session_key
            print(f"?? Session: {session_key}")

        response = self.get_response(request)

        # Check session after request
        if settings.DEBUG and request.user.is_authenticated:
            print(f"?? Session after: {request.session.session_key}")

        return response


class DatabaseQueryLoggingMiddleware(MiddlewareMixin):
    """Middleware to log database queries for debugging."""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Only log in debug mode
        if not settings.DEBUG:
            return self.get_response(request)

        from django.db import connection

        # Reset query count
        initial_queries = len(connection.queries)

        response = self.get_response(request)

        # Log query count
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries

        if query_count > 50:
            print(f"?? High query count: {query_count} queries for {request.path}")
            # Print slow queries if any
            for query in connection.queries[-5:]:
                if "time" in query and float(query.get("time", 0)) > 1.0:
                    print(
                        f"?? Slow query ({query.get('time', 0)}s): {query.get('sql', '')[:100]}..."
                    )

        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """Middleware to handle maintenance mode."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.maintenance_mode = (
            os.environ.get("MAINTENANCE_MODE", "False").lower() == "true"
        )
        super().__init__(get_response)

    def __call__(self, request):
        # Check if maintenance mode is enabled
        if self.maintenance_mode:
            # Allow admins to access the site
            if request.user.is_authenticated and request.user.is_superuser:
                return self.get_response(request)

            # Block all other requests
            if not request.path.startswith("/admin/") and not request.path.startswith(
                "/static/"
            ):
                from django.shortcuts import render

                return render(request, "maintenance.html", status=503)

        return self.get_response(request)


def get_error_logs(request):
    """View function to retrieve error logs (admin only)."""
    from django.contrib.admin.views.decorators import staff_member_required

    if not request.user.is_superuser:
        return JsonResponse({"error": "Permission denied"}, status=403)

    log_file = settings.BASE_DIR / "error_logs.txt"

    if not log_file.exists():
        return JsonResponse({"logs": [], "message": "No error logs found"})

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse logs into entries
        entries = []
        current_entry = {}

        for line in content.split("\n"):
            if line.startswith("=" * 80):
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
            elif ":" in line and not line.startswith("-"):
                key, value = line.split(":", 1)
                current_entry[key.strip()] = value.strip()
            elif line.startswith("-") or line.startswith(" "):
                if "Traceback" not in current_entry:
                    current_entry["Traceback"] = ""
                current_entry["Traceback"] += line + "\n"

        if current_entry:
            entries.append(current_entry)

        # Return last 50 entries
        return JsonResponse({"logs": entries[-50:], "total": len(entries)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
