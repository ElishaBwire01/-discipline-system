# ============================================
# PYTHON STANDARD LIBRARY
# ============================================
import csv
import difflib
import json
import logging
import os
import re
import secrets
from datetime import datetime, timedelta

# ============================================
# THIRD PARTY IMPORTS
# ============================================
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction

# ============================================
# DATABASE & QUERY IMPORTS
# ============================================
from django.db.models import Avg, Count, Max, Min, Q
from django.db.models.functions import ExtractWeekDay
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse

# DJANGO CORE IMPORTS
# ============================================
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from openpyxl import Workbook

# ============================================
# LOCAL MODELS
# ============================================
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

logger = logging.getLogger(__name__)


def safe_json_response(data, status=200):
    """Return a JSON response with proper (non-ASCII-escaped) encoding."""
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})


# ============================================
# RATE LIMITING (SECURITY ISSUE #2 FIX)
# ============================================
# Simple cache-backed rate limiter. No extra dependency (django-ratelimit)
# is assumed to be installed, so this uses Django's cache framework, which
# already backs the rest of the app (see OPTIMIZATION 3 / caching notes).


def _client_ip(request):
    """Best-effort client IP, tolerant of a trusted reverse proxy in front of
    the app (nginx/Cloudflare). Only trust X-Forwarded-For if
    settings.TRUST_PROXY_HEADERS is explicitly enabled in settings.py."""
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limited(key_prefix, limit, window_seconds):
    """
    Decorator: allow at most `limit` calls per `window_seconds` per
    (key_prefix, client_ip). Returns HTTP 429 once exceeded.

    Usage:
        @rate_limited("login", limit=10, window_seconds=300)
        def custom_login(request): ...
    """

    def decorator(view_func):
        def wrapped(request, *args, **kwargs):
            cache_key = f"ratelimit:{key_prefix}:{_client_ip(request)}"
            count = cache.get(cache_key, 0)
            if count >= limit:
                logger.warning(
                    "Rate limit exceeded | key=%s | ip=%s", key_prefix, _client_ip(request)
                )
                return JsonResponse(
                    {"error": "Too many requests. Please try again later."},
                    status=429,
                )
            try:
                cache.incr(cache_key)
            except ValueError:
                cache.set(cache_key, 1, timeout=window_seconds)
            else:
                if count == 0:
                    cache.set(cache_key, 1, timeout=window_seconds)
            return view_func(request, *args, **kwargs)

        wrapped.__name__ = getattr(view_func, "__name__", "wrapped")
        wrapped.__doc__ = view_func.__doc__
        return wrapped

    return decorator


# ============================================
# HELPERS
# ============================================


def admin_required(user):
    return user.is_superuser


def class_teacher_required(user):
    return user.is_superuser or user.groups.filter(name="ClassTeacher").exists()


def get_teacher_profile(user):
    try:
        return user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return None


def get_rating_label(rating):
    labels = {
        "VERY_MINOR": "Very Minor",
        "MINOR": "Minor",
        "MODERATE": "Moderate",
        "SERIOUS": "Serious",
        "VERY_SERIOUS": "Very Serious",
    }
    return labels.get(rating, "Moderate")


def get_rating_display(report):
    """Consistent rating-label lookup used across templates/exports."""
    if hasattr(report, "get_rating_display"):
        return report.get_rating_display()
    return dict(DisciplineReport.RATING_CHOICES).get(report.rating, report.rating)


def _paginate_per_page(request, allowed=(10, 20, 50, 100), default=20):
    """Shared, safe per_page parsing for every paginated view."""
    raw = request.GET.get("per_page", default)
    try:
        value = int(raw)
        if value not in allowed:
            value = default
    except (ValueError, TypeError):
        value = default
    return value


def _get_notification_context(request):
    """Shared unread-notification context used by nearly every dashboard/template
    view (CODE QUALITY IMPROVEMENT #2 / performance OPTIMIZATION #3: single
    query instead of re-filtering in every view)."""
    unread_notifications = request.user.notifications.filter(is_read=False)
    return {
        "notification_count": unread_notifications.count(),
        "unread_notifications": unread_notifications,
    }


def _get_active_streams():
    """Cached list of active streams (OPTIMIZATION #3 / IMPROVEMENT #5)."""
    streams = cache.get("active_streams")
    if streams is None:
        streams = list(Stream.objects.filter(is_active=True).order_by("name"))
        cache.set("active_streams", streams, timeout=300)
    return streams


def _get_active_categories():
    """Cached list of active discipline categories."""
    categories = cache.get("active_categories")
    if categories is None:
        categories = list(
            DisciplineCategory.objects.filter(is_active=True).order_by("order", "name")
        )
        cache.set("active_categories", categories, timeout=300)
    return categories


def invalidate_lookup_caches():
    """Call after creating/editing/deleting a Stream or DisciplineCategory."""
    cache.delete("active_streams")
    cache.delete("active_categories")


def _create_report(request, student, post):
    """
    Creates a DisciplineReport for the given student using POST data.
    Returns True on success, False on failure (messages already set).
    """
    category_id = post.get("category") or post.get("category_id")
    report_type = post.get("report_type", "standard")
    custom_case = post.get("custom_case", "").strip()
    comments = post.get("comments", "")
    rating = post.get("rating", "MODERATE")

    if report_type == "custom" or category_id == "custom":
        if not custom_case:
            messages.error(request, "Please describe the custom case.")
            return False
        try:
            category, _ = DisciplineCategory.objects.get_or_create(
                key="CUSTOM",
                defaults={
                    "name": "Custom Case",
                    "description": "User-defined custom offense",
                    "default_rating": "MODERATE",
                    "is_active": True,
                    "order": 999,
                },
            )
            category_name = custom_case
        except (ValueError, TypeError) as e:
            messages.error(request, f"Error creating custom category: {e}")
            return False
    else:
        if not category_id:
            messages.error(request, "Please select an offence category.")
            return False
        try:
            category = DisciplineCategory.objects.get(id=category_id, is_active=True)
            category_name = category.name
        except DisciplineCategory.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            return False

    valid_ratings = ["VERY_MINOR", "MINOR", "MODERATE", "SERIOUS", "VERY_SERIOUS"]
    if rating not in valid_ratings:
        rating = getattr(category, "default_rating", "MODERATE")

    report_comments = (
        f"{comments}\n[Custom: {custom_case}]" if custom_case else comments
    )

    report = DisciplineReport.objects.create(
        student=student,
        reported_by=request.user,
        category=category,
        comments=report_comments,
        rating=rating,
    )
    if custom_case:
        report.category_name = custom_case
        report.save(update_fields=["category_name"])

    rating_label = get_rating_label(rating)
    messages.success(
        request,
        f"Report submitted for {student.name}: {category_name} "
        f"(Points: +{report.points}, Rating: {rating_label})",
    )
    return True


def _get_form_choices():
    """Return form choices as tuples (key, value) for dropdowns."""
    from .models import Student
    return Student.FORM_CHOICES

def get_filtered_students(request, base_qs=None):
    """
    CODE QUALITY IMPROVEMENT #1: single reusable student-filtering helper.
    Applies the standard search/stream/form query-string filters used by
    teacher_dashboard, admin_dashboard, and class_teacher_dashboard alike.
    """
    students_qs = base_qs if base_qs is not None else Student.objects.filter(
        is_active=True
    )
    students_qs = students_qs.select_related("stream", "grade_level")

    search_query = request.GET.get("search", "").strip()
    stream_filter = request.GET.get("stream", "").strip()
    form_filter = request.GET.get("form", "").strip()

    if search_query:
        students_qs = students_qs.filter(
            Q(name__icontains=search_query)
            | Q(admission_number__icontains=search_query)
        )
    if stream_filter:
        students_qs = students_qs.filter(stream__name=stream_filter)
    if form_filter:
        students_qs = students_qs.filter(form=form_filter)

    return students_qs.order_by("name"), search_query, stream_filter, form_filter


def _class_teacher_scope(profile):
    """
    The single source of truth for "which students does this class teacher see".

    A class teacher is assigned to exactly one (stream, form) pair. They must
    see ONLY students in that exact pair - not the whole stream, and not other
    forms/grades in that stream (those belong to a different class teacher).

    Returns a Student queryset, or Student.objects.none() if the teacher has
    not been fully set up yet.

    FIX (CRITICAL ERROR 1 / audit item 1-3): this function's body had been
    overwritten with unrelated redirect logic that referenced an undefined
    `request` variable, guaranteeing a NameError for every class-teacher view
    that called it. Restored to its intended behavior below.
    """
    if (
        not profile
        or not profile.has_chosen_stream
        or not profile.assigned_stream_id
        or not profile.assigned_form
    ):
        return Student.objects.none()

    return Student.objects.filter(
        stream_id=profile.assigned_stream_id,
        form=profile.assigned_form,
        is_active=True,
    )


# ============================================
# ROOT / REDIRECT VIEWS
# ============================================


def root_redirect(request):
    """
    Redirect the site root ("/") to the login page or the role-appropriate
    dashboard, depending on authentication status.

    FIX (ERROR 11): this function was missing entirely - its logic had been
    accidentally pasted into the middle of `_class_teacher_scope` instead.
    """
    if request.user.is_authenticated:
        return redirect("dashboard_redirect")
    return redirect("/login/")


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role."""

    if request.user.is_superuser:
        return redirect("core:admin_dashboard")
    elif request.user.groups.filter(name="ClassTeacher").exists():
        return redirect("core:class_teacher_dashboard")
    else:
        return redirect("core:teacher_dashboard")


# ============================================
# AUTHENTICATION VIEWS
# ============================================


@never_cache
@rate_limited("login", limit=10, window_seconds=300)
def custom_login(request):
    if request.user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Account permanently banned. Contact admin.")
                return render(
                    request, "login.html", {"error": "Account permanently banned"}
                )

            profile = get_teacher_profile(user)
            if profile:
                if (
                    not profile.is_approved
                    and user.groups.filter(name="ClassTeacher").exists()
                ):
                    messages.error(request, "Account pending admin approval.")
                    return render(
                        request, "login.html", {"error": "Account pending approval"}
                    )
                if profile.is_suspended:
                    messages.error(
                        request,
                        f"Account suspended. Reason: {profile.suspension_reason}",
                    )
                    return render(request, "login.html", {"error": "Account suspended"})

            login(request, user)
            request.session.save()
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key,
                ip_address=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            )

            if profile:
                profile.is_online = True
                profile.last_activity = timezone.now()
                profile.save(update_fields=["is_online", "last_activity"])

            if user.groups.filter(name="ClassTeacher").exists():
                if not profile or not profile.has_chosen_stream:
                    return redirect("core:choose_stream")

            return redirect("/dashboard/")

        messages.error(request, "Invalid username or password.")
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


@login_required
def custom_logout(request):
    """
    Log the user out, cleaning up their online-status flag and closing out
    their UserSession record so "online teachers" and session history stay
    accurate.

    FIX (ERROR 6): missing entirely - sessions never got cleaned up and
    is_online never got cleared, so users stayed shown as "online" forever.
    """
    profile = get_teacher_profile(request.user)
    if profile:
        profile.is_online = False
        profile.last_activity = timezone.now()
        profile.save(update_fields=["is_online", "last_activity"])

    session_key = request.session.session_key
    if session_key:
        UserSession.objects.filter(session_key=session_key).update(
            logged_out_at=timezone.now()
        )

    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("/login/")


@never_cache
@rate_limited("register", limit=5, window_seconds=600)
def register(request):
    """
    New teacher self-registration. Whether registration is even allowed, and
    whether new teachers need admin approval before logging in, are both
    controlled by the School singleton (see school_setup()).

    FIX (ERROR 7): missing entirely - there was no way for a new teacher to
    create an account at all.
    """
    if request.user.is_authenticated:
        return redirect("/dashboard/")

    school, _ = School.objects.get_or_create(id=1)
    if not school.allow_teacher_registration:
        messages.error(request, "Teacher registration is currently disabled. Contact your administrator.")
        return render(request, "register.html", {"registration_disabled": True})

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "Teacher")

        errors = []
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username__iexact=username).exists():
            errors.append("That username is already taken.")
        if not first_name or not last_name:
            errors.append("First and last name are required.")
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Please enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if role not in ("Teacher", "ClassTeacher"):
            role = "Teacher"

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "register.html",
                {"form_data": request.POST, "registration_disabled": False},
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            needs_approval = role == "ClassTeacher" and school.require_teacher_approval
            TeacherProfile.objects.create(
                user=user,
                phone_number=phone,
                is_approved=not needs_approval,
            )

            if needs_approval:
                admins = User.objects.filter(is_superuser=True)
                if admins.exists():
                    notification = Notification.objects.create(
                        title="New Teacher Registration",
                        message=f"{user.get_full_name() or username} has registered and needs approval.",
                        notification_type="info",
                    )
                    notification.target_users.set(admins)

        if needs_approval:
            messages.success(
                request, "Account created! An admin must approve it before you can log in."
            )
            return redirect("/login/")

        messages.success(request, "Account created! You can now log in.")
        return redirect("/login/")

    return render(request, "register.html", {"registration_disabled": False})


@login_required
def choose_stream(request):
    """
    Let a newly-approved class teacher pick the (stream, form) pair they will
    be responsible for. Prevents choosing a pair that is already claimed by
    another active class teacher.

    FIX (ERROR 8): missing entirely - new class teachers had no way to select
    their assigned class, so _class_teacher_scope() always returned nothing
    for them even once fixed.
    """
    if not request.user.groups.filter(name="ClassTeacher").exists():
        return redirect("dashboard_redirect")

    profile = get_teacher_profile(request.user)
    if not profile:
        profile = TeacherProfile.objects.create(user=request.user)

    if profile.has_chosen_stream:
        return redirect("core:class_teacher_dashboard")

    streams = _get_active_streams()
    forms = _get_form_choices()

    if request.method == "POST":
        stream_id = request.POST.get("stream_id")
        form = request.POST.get("form", "").strip()

        if not stream_id or not form:
            messages.error(request, "Please select both a stream and a form.")
        else:
            try:
                stream = Stream.objects.get(id=stream_id, is_active=True)
            except Stream.DoesNotExist:
                messages.error(request, "Invalid stream selected.")
                stream = None

            if stream:
                conflict = User.objects.filter(
                    teacher_profile__assigned_stream=stream,
                    teacher_profile__assigned_form=form,
                    teacher_profile__has_chosen_stream=True,
                    groups__name="ClassTeacher",
                ).exclude(id=request.user.id)

                if conflict.exists():
                    messages.error(
                        request,
                        f"{stream.name} - {form} is already assigned to another class teacher. "
                        "Please choose a different class or contact an admin.",
                    )
                else:
                    profile.assigned_stream = stream
                    profile.assigned_form = form
                    profile.has_chosen_stream = True
                    profile.save()
                    messages.success(request, f"You are now the class teacher for {stream.name} - {form}.")
                    return redirect("core:class_teacher_dashboard")

    return render(
        request,
        "choose_stream.html",
        {"streams": streams, "forms": forms},
    )


# ============================================
# DASHBOARDS
# ============================================

@login_required
def teacher_dashboard(request):
    """Subject/general teacher dashboard: sees all students school-wide (unlike
    a ClassTeacher, who is restricted to their own stream+form).
    """
    per_page = _paginate_per_page(request)
    streams = _get_active_streams()

    students_qs, search_query, stream_filter, form_filter = get_filtered_students(request)

    paginator = Paginator(students_qs, per_page)
    students_page = paginator.get_page(request.GET.get("page"))

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "report_student":
            student_id = request.POST.get("student_id")
            if student_id:
                student = get_object_or_404(Student, id=student_id, is_active=True)
                _create_report(request, student, request.POST)
                return redirect("/teacher-dashboard/")

    context = {
        "page_obj": students_page,  # For pagination template
        "per_page": per_page,  # For pagination
        "streams": streams,
        "students": students_page,
        "categories": _get_active_categories(),
        "forms": _get_form_choices(),
        "search_query": search_query,
        "stream_filter": stream_filter,
        "form_filter": form_filter,
        "per_page": per_page,
        **_get_notification_context(request),
    }
    return render(request, "teacher_dashboard.html", context)


@login_required
@user_passes_test(class_teacher_required)
def class_teacher_dashboard(request):
    """
    Class teacher's own dashboard: restricted to exactly the (stream, form)
    pair they were assigned via choose_stream()/assign_class_teacher().
    """
    profile = get_teacher_profile(request.user)
    if not profile or not profile.has_chosen_stream:
        return redirect("core:choose_stream")

    per_page = _paginate_per_page(request)
    base_qs = _class_teacher_scope(profile)
    
    # Get filtered students with search support
    students_qs, search_query, _stream_filter, _form_filter = get_filtered_students(
        request, base_qs=base_qs
    )
    
    # Class teacher's own stream/form is fixed, only search term applies
    students_qs = base_qs.select_related("stream")
    if search_query:
        students_qs = students_qs.filter(
            Q(name__icontains=search_query)
            | Q(admission_number__icontains=search_query)
        )
    students_qs = students_qs.order_by("name")

    paginator = Paginator(students_qs, per_page)
    students_page = paginator.get_page(request.GET.get("page"))

    # Handle POST actions
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "report_student":
            student_id = request.POST.get("student_id")
            if student_id and base_qs.filter(id=student_id).exists():
                student = get_object_or_404(Student, id=student_id, is_active=True)
                _create_report(request, student, request.POST)
                return redirect("/class-teacher-dashboard/")
            messages.error(request, "That student is not in your class.")

    # Calculate class statistics
    total_in_class = base_qs.count()
    critical_count = base_qs.filter(risk_level="CRITICAL").count()
    warning_count = base_qs.filter(risk_level="WARNING").count()
    good_count = base_qs.filter(risk_level="GOOD").count()

    context = {
        "assigned_stream": profile.assigned_stream,
        "assigned_form": profile.assigned_form,
        "students": students_page,
        "total_students": total_in_class,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "good_count": good_count,
        "categories": _get_active_categories(),
        "search_query": search_query,
        "per_page": per_page,
        **_get_notification_context(request),
    }
    return render(request, "class_teacher_dashboard.html", context)


@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    """
    Main admin landing page: school-wide stats plus pending-approval counts
    so an admin can see at a glance what needs attention.
    """
    # Get all active students
        # Get all students for display with pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    students_list = Student.objects.filter(is_active=True).select_related('stream', 'grade_level')
    total_students = students_list.count()
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    paginator = Paginator(students_list, per_page)
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    total_students = students_list.count()
    critical_count = students_list.filter(risk_level="CRITICAL").count()
    warning_count = students_list.filter(risk_level="WARNING").count()
    good_count = students_list.filter(risk_level="GOOD").count()

    # Admin specific counts
    pending_approvals = TeacherProfile.objects.filter(
        is_approved=False, is_suspended=False
    ).count()
    pending_resets = PasswordReset.objects.filter(status="pending").count()
    # Get all students for display
    students_list = Student.objects.filter(is_active=True).select_related('stream', 'grade_level')
    total_students = students_list.count()
    
    online_teachers = TeacherProfile.objects.filter(is_online=True).count()

    # Get recent reports
    recent_reports = DisciplineReport.objects.select_related(
        "student", "category", "reported_by"
    ).order_by("-reported_at")[:10]

    # Build context
    context = {
        "page_obj": students,  # For pagination
        "students": students,
        "total_students": total_students,
        "grade_levels": GradeLevel.objects.filter(is_active=True).order_by("order"),
        "streams": _get_active_streams(),
        "total_students": total_students,
        "critical_students": critical_count,
        "warning_students": warning_count,
        "good_students": good_count,
        "total_reports": DisciplineReport.objects.count(),
        "categories": _get_active_categories(),
        "pending_approvals": pending_approvals,
        "pending_resets": pending_resets,
        "online_teachers": online_teachers,
        "recent_reports": recent_reports,
        "avg_risk_score": students_list.aggregate(Avg("risk_score"))["risk_score__avg"] or 0,
        "forms": _get_form_choices(),
        "forms": _get_form_choices(),
        **_get_notification_context(request),
    }
    return render(request, "admin_dashboard.html", context)

# ============================================
# STUDENT PROFILE / EDITING
# ============================================


@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id, is_active=True)

    # If the viewer is a class teacher, they may only view students in their
    # own stream+form (admins and general teachers are unrestricted).
    if not request.user.is_superuser:
        profile = get_teacher_profile(request.user)
        if (
            profile
            and profile.has_chosen_stream
            and request.user.groups.filter(name="ClassTeacher").exists()
        ):
            if not _class_teacher_scope(profile).filter(id=student.id).exists():
                messages.error(
                    request, "You do not have permission to view this student."
                )
                return redirect("/class-teacher-dashboard/")

    reports = student.reports.select_related("reported_by", "category").order_by(
        "-reported_at"
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "report_student":
            _create_report(request, student, request.POST)
            return redirect("student_profile", student_id=student_id)

    category_breakdown = (
        reports.values("category__name").annotate(count=Count("id")).order_by("-count")
    )

    context = {
        "streams": _get_active_streams(),
        "student": student,
        "reports": reports,
        "categories": _get_active_categories(),
        "category_breakdown": category_breakdown,
        "total_reports": reports.count(),
        **_get_notification_context(request),
    }
    return render(request, "student_profile.html", context)


@login_required
def edit_student(request, student_id):
    """
    Edit a student's core details. Admins and general teachers can edit any
    student; class teachers may only edit students within their own scope.

    FIX (ERROR 14): missing entirely.
    """
    student = get_object_or_404(Student, id=student_id, is_active=True)

    if not request.user.is_superuser:
        profile = get_teacher_profile(request.user)
        is_class_teacher = request.user.groups.filter(name="ClassTeacher").exists()
        if is_class_teacher:
            if not profile or not _class_teacher_scope(profile).filter(id=student.id).exists():
                messages.error(request, "You do not have permission to edit this student.")
                return redirect("/class-teacher-dashboard/")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        admission_number = request.POST.get("admission_number", "").strip()
        stream_id = request.POST.get("stream_id")
        form = request.POST.get("form", "").strip()
        optional_notes = request.POST.get("optional_notes", "").strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not admission_number:
            errors.append("Admission number is required.")
        elif (
            Student.objects.filter(admission_number=admission_number)
            .exclude(id=student.id)
            .exists()
        ):
            errors.append("Another student already has that admission number.")

        stream = None
        if stream_id:
            try:
                stream = Stream.objects.get(id=stream_id, is_active=True)
            except Stream.DoesNotExist:
                errors.append("Invalid stream selected.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            student.name = name
            student.admission_number = admission_number
            if stream:
                student.stream = stream
            if form:
                student.form = form
            student.optional_notes = optional_notes
            student.save()
            messages.success(request, f"{student.name} updated successfully.")
            return redirect("student_profile", student_id=student.id)

    context = {
        "student": student,
        "streams": _get_active_streams(),
        "forms": _get_form_choices(),
        **_get_notification_context(request),
    }
    return render(request, "edit_student.html", context)


# ============================================
# USER PROFILE / SETTINGS
# ============================================


@login_required
def user_profile_settings(request):
    """
    Let the logged-in user update their own username/email/password/picture.

    FIX (ERROR 12): missing entirely.
    """
    profile = get_teacher_profile(request.user)
    if not profile:
        profile = TeacherProfile.objects.create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            email = request.POST.get("email", "").strip()
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            phone = request.POST.get("phone", "").strip()

            if email:
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, "Please enter a valid email address.")
                    return redirect("core:user_profile_settings")

            request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save(update_fields=["email", "first_name", "last_name"])
            profile.phone_number = phone
            profile.save(update_fields=["phone_number"])
            messages.success(request, "Profile updated successfully.")
            return redirect("core:user_profile_settings")

        elif action == "change_password":
            current_password = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif len(new_password) < 8:
                messages.error(request, "New password must be at least 8 characters.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully.")
            return redirect("core:user_profile_settings")

    context = {
        "profile": profile,
        **_get_notification_context(request),
    }
    return render(request, "user_profile_settings.html", context)


@login_required
def view_user_profile(request, user_id):
    """
    View another teacher's profile (admins can view anyone; teachers can view
    other teachers but not sensitive admin-only fields).

    FIX (ERROR 13): missing entirely.
    """
    target_user = get_object_or_404(User, id=user_id)
    profile = get_teacher_profile(target_user)

    if not request.user.is_superuser and target_user.id != request.user.id:
        # Non-admins may view basic info about other teachers, but let's make
        # sure the target is actually a teacher/class-teacher, not some
        # unrelated account.
        if not target_user.groups.filter(name__in=["Teacher", "ClassTeacher"]).exists():
            return HttpResponseForbidden("You do not have permission to view this profile.")

    context = {
        "profile_user": target_user,
        "profile": profile,
        "is_own_profile": target_user.id == request.user.id,
        **_get_notification_context(request),
    }
    return render(request, "view_user_profile.html", context)


@login_required
def upload_profile_picture(request):
    """
    Upload/replace the current user's profile picture.

    FIX (ERROR 15): missing entirely.

    SECURITY (ISSUE 3): validates file size and extension before saving,
    since this endpoint accepts arbitrary uploads.
    """
    if request.method != "POST":
        return redirect("core:user_profile_settings")

    upload = request.FILES.get("profile_picture")
    if not upload:
        messages.error(request, "Please choose an image to upload.")
        return redirect("core:user_profile_settings")

    max_size_bytes = 5 * 1024 * 1024  # 5MB
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(upload.name)[1].lower()

    if upload.size > max_size_bytes:
        messages.error(request, "Image must be smaller than 5MB.")
        return redirect("core:user_profile_settings")
    if ext not in allowed_extensions:
        messages.error(request, "Only JPG, PNG, and WEBP images are allowed.")
        return redirect("core:user_profile_settings")

    profile = get_teacher_profile(request.user)
    if not profile:
        profile = TeacherProfile.objects.create(user=request.user)

    profile.profile_picture = upload
    profile.save(update_fields=["profile_picture"])
    messages.success(request, "Profile picture updated.")
    return redirect("core:user_profile_settings")


@login_required
@user_passes_test(admin_required)
def admin_profile(request):
    """
    Admin's own profile - just reuses the shared profile settings page.

    FIX (ERROR 16): missing entirely.
    """
    return redirect("core:user_profile_settings")


# ============================================
# TEACHER PROFILE API
# ============================================


@login_required
def teacher_profile_api(request, user_id):
    """API endpoint to get teacher profile data for the quick-view modal."""
    try:
        user = get_object_or_404(User, id=user_id)
        profile = get_teacher_profile(user)

        groups = user.groups.values_list("name", flat=True)
        is_class_teacher = "ClassTeacher" in groups
        is_teacher = "Teacher" in groups

        profile_picture_url = None
        if profile and profile.profile_picture:
            try:
                profile_picture_url = request.build_absolute_uri(
                    profile.profile_picture.url
                )
            except (ValueError, AttributeError):
                profile_picture_url = None

        data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.get_full_name() or user.username,
            "email": user.email or "",
            "profile_picture": profile_picture_url,
            "is_online": profile.is_online if profile else False,
            "is_approved": profile.is_approved if profile else False,
            "is_suspended": profile.is_suspended if profile else False,
            "assigned_stream": (
                profile.assigned_stream.name
                if profile and profile.assigned_stream
                else "Not Assigned"
            ),
            "assigned_form": profile.assigned_form if profile else None,
            "phone": profile.phone_number if profile else "",
            "role": (
                "Class Teacher"
                if is_class_teacher
                else "Teacher" if is_teacher else "Admin"
            ),
            "is_superuser": user.is_superuser,
            "suspension_reason": (
                profile.suspension_reason if profile and profile.is_suspended else None
            ),
            "has_chosen_stream": profile.has_chosen_stream if profile else False,
            "last_activity": (
                profile.last_activity.strftime("%Y-%m-%d %H:%M")
                if profile and profile.last_activity
                else None
            ),
        }
        return JsonResponse(data)
    except Http404:
        return JsonResponse({"error": "User not found"}, status=404)
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============================================
# API ENDPOINTS
# ============================================


@login_required
@rate_limited("search_api", limit=60, window_seconds=60)
def search_students_api(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"students": []})

    students_qs = Student.objects.filter(
        Q(name__icontains=query) | Q(admission_number__icontains=query), is_active=True
    ).select_related("stream")

    # Class teachers only search within their own stream+form.
    profile = get_teacher_profile(request.user)
    if (
        profile
        and not request.user.is_superuser
        and request.user.groups.filter(name="ClassTeacher").exists()
    ):
        students_qs = students_qs.filter(
            stream_id=profile.assigned_stream_id, form=profile.assigned_form
        )

    students_qs = students_qs[:20]

    if not students_qs.exists() and query.isdigit():
        try:
            pk_student = Student.objects.get(id=int(query), is_active=True)
            students_qs = [pk_student]
        except Student.DoesNotExist:
            pass

    data = [
        {
            "id": s.id,
            "name": s.name,
            "admission_number": s.admission_number,
            "stream": s.stream.name if s.stream else "N/A",
            "form": s.form,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "is_critical": s.is_critical,
            "total_reports": s.total_reports,
        }
        for s in students_qs
    ]
    return JsonResponse({"students": data})


@login_required
def mark_notification_read(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id)
        notification.mark_read(request.user)
        return JsonResponse({"status": "success"})
    return JsonResponse(
        {"status": "error", "message": "Method not allowed."}, status=405
    )


@login_required
def get_notifications_api(request):
    notifications = request.user.notifications.filter(is_read=False).order_by(
        "-created_at"
    )[:10]
    data = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message[:100],
            "type": n.notification_type,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
            "student_id": n.student.id if hasattr(n, "student") and n.student else None,
        }
        for n in notifications
    ]
    return JsonResponse({"notifications": data, "count": len(data)})


@login_required
@user_passes_test(admin_required)
def get_admin_notifications(request):
    """
    Admin-specific notification summary: pending teacher approvals, pending
    password resets, and unread general notifications, so admin templates
    can show badge counts without each doing their own separate queries.

    FIX (ERROR 17): missing entirely.
    """
    pending_approvals = TeacherProfile.objects.filter(
        is_approved=False, is_suspended=False
    ).count()
    pending_resets = PasswordReset.objects.filter(status="pending").count()
    unread_notifications = request.user.notifications.filter(is_read=False)

    data = {
        "pending_approvals": pending_approvals,
        "pending_resets": pending_resets,
        "unread_count": unread_notifications.count(),
        "total_badge_count": pending_approvals + pending_resets + unread_notifications.count(),
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message[:100],
                "type": n.notification_type,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for n in unread_notifications.order_by("-created_at")[:10]
        ],
    }
    return JsonResponse({"status": "success", "data": data})


@login_required
def online_teachers_api(request):
    online = TeacherProfile.objects.filter(is_online=True).select_related(
        "user", "assigned_stream"
    )
    data = [
        {
            "username": t.user.username,
            "full_name": t.user.get_full_name() or t.user.username,
            "assigned_stream": (
                t.assigned_stream.name if t.assigned_stream else "Not Assigned"
            ),
            "last_activity": (
                t.last_activity.strftime("%Y-%m-%d %H:%M") if t.last_activity else "N/A"
            ),
        }
        for t in online
    ]
    return JsonResponse({"online_teachers": data})


# ============================================
# AI VIEWS
# ============================================


@login_required
def ai_dashboard(request):
    students_list = Student.objects.filter(is_active=True)

    total_students = students_list.count()
    critical_count = students_list.filter(risk_level="CRITICAL").count()
    warning_count = students_list.filter(risk_level="WARNING").count()
    good_count = students_list.filter(risk_level="GOOD").count()

    students_with_interventions = students_list.filter(intervention_count__gt=0).count()
    recent_incidents = DisciplineReport.objects.filter(
        reported_at__date=timezone.now().date()
    ).count()

    context = {
        "streams": _get_active_streams(),
        "total_students": total_students,
        "critical_students": critical_count,
        "warning_students": warning_count,
        "good_students": good_count,
        "total_reports": DisciplineReport.objects.count(),
        "categories": _get_active_categories(),
        "students_with_interventions": students_with_interventions,
        "recent_incidents": recent_incidents,
        "avg_risk_score": students_list.aggregate(Avg("risk_score"))["risk_score__avg"] or 0,
        "forms": _get_form_choices(),
        "forms": _get_form_choices(),
        "critical_percentage": round(
            (critical_count / total_students * 100) if total_students > 0 else 0, 1
        ),
        "warning_percentage": round(
            (warning_count / total_students * 100) if total_students > 0 else 0, 1
        ),
        "good_percentage": round(
            (good_count / total_students * 100) if total_students > 0 else 0, 1
        ),
        **_get_notification_context(request),
    }
    return render(request, "ai_dashboard.html", context)


@login_required
def student_recommendations(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id, is_active=True)
        reports = student.reports.select_related("category")
        total_reports = reports.count()

        category_breakdown = (
            reports.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        student_data = {
            "id": student.id,
            "name": student.name,
            "admission_number": student.admission_number,
            "risk_score": student.risk_score,
            "risk_level": student.risk_level,
            "form": student.form,
            "stream": student.stream.name if student.stream else "N/A",
            "total_reports": total_reports,
            "intervention_count": student.intervention_count,
            # FIX (ERROR 4): was the literal key "unknown_key", populated via
            # an unrelated (and unsafe) getattr(..., os.environ["SECRET_KEY"])
            # lookup. Replaced with the intended field name.
            "days_since_last_incident": getattr(
                student, "days_since_last_incident", None
            ),
            "risk_trend": getattr(student, "risk_trend", "stable"),
        }

        recommendations = []
        if student.risk_level == "CRITICAL":
            recommendations.append(
                {
                    "type": "critical",
                    "title": "CRITICAL - Immediate Action Required",
                    "description": f"{student.name} has reached {student.risk_score}% risk level with {total_reports} total reports.",
                    "steps": [
                        "Schedule emergency parent-teacher conference TODAY",
                        "Refer to school counselor immediately",
                        "Create comprehensive behavior intervention plan",
                        "Schedule weekly progress review meetings",
                        "Document all interventions",
                    ],
                }
            )
        elif student.risk_level == "WARNING":
            recommendations.append(
                {
                    "type": "warning",
                    "title": "Warning - Monitor Closely",
                    "description": f"{student.name} has {student.risk_score}% risk with {total_reports} reports.",
                    "steps": [
                        "Schedule parent meeting within 1 week",
                        "Implement behavior tracking system",
                        "Assign mentor or buddy system",
                        "Increase classroom monitoring",
                        "Document all incidents",
                    ],
                }
            )
        else:
            recommendations.append(
                {
                    "type": "success",
                    "title": "Student Status: Good",
                    "description": f"{student.name} is doing well with {student.risk_score}% risk level.",
                    "steps": [
                        "Continue positive reinforcement",
                        "Maintain regular monitoring",
                        "Encourage leadership opportunities",
                        "Document positive achievements",
                    ],
                }
            )

        for cat in category_breakdown:
            if cat["count"] >= 3:
                recommendations.append(
                    {
                        "type": "pattern",
                        "title": f'Pattern Detected: {cat["category__name"]}',
                        "description": f'{cat["count"]} reports in this category. Address this pattern.',
                        "steps": [
                            f'Discuss {cat["category__name"]} pattern with student',
                            "Develop specific strategies to address this issue",
                            "Monitor for improvement in this area",
                            "Document progress or setbacks",
                        ],
                    }
                )
            elif cat["count"] >= 2:
                recommendations.append(
                    {
                        "type": "pattern",
                        "title": f'Emerging Pattern: {cat["category__name"]}',
                        "description": f'{cat["count"]} reports in this category. Monitor closely.',
                        "steps": [
                            f'Address {cat["category__name"]} with student',
                            "Track future incidents in this category",
                            "Consider preventive measures",
                        ],
                    }
                )

        if student.intervention_count == 0 and student.risk_level in [
            "WARNING",
            "CRITICAL",
        ]:
            recommendations.append(
                {
                    "type": "critical",
                    "title": "No Interventions Recorded",
                    "description": "This student needs interventions but none have been recorded.",
                    "steps": [
                        "Create intervention plan immediately",
                        "Schedule meeting with student and parents",
                        "Assign counselor or mentor",
                        "Document all interventions",
                    ],
                }
            )

        return JsonResponse(
            {
                "student": student_data,
                "recommendations": recommendations,
                "total_reports": total_reports,
                "category_breakdown": list(category_breakdown),
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def class_recommendations(request, stream_id):
    try:
        stream = get_object_or_404(Stream, id=stream_id)
        students_list = Student.objects.filter(stream=stream, is_active=True)

        if not students_list.exists():
            return JsonResponse(
                {
                    "stream": stream.name,
                    "statistics": {
                        "total_students": 0,
                        "critical_count": 0,
                        "warning_count": 0,
                        "good_count": 0,
                        "average_risk": 0,
                        # FIX (ERROR 5): was the literal key "unknown_key".
                        "students_with_interventions": 0,
                    },
                    "recommendations": [
                        {
                            "type": "INFO",
                            "action": "No students in this stream",
                            "details": "Add students to this stream to get analysis.",
                        }
                    ],
                    "top_offenders": [],
                }
            )

        total = students_list.count()
        critical = students_list.filter(risk_level="CRITICAL").count()
        warning = students_list.filter(risk_level="WARNING").count()
        good = students_list.filter(risk_level="GOOD").count()
        avg_risk = students_list.aggregate(avg=Avg("risk_score"))["avg"] or 0
        with_interventions = students_list.filter(intervention_count__gt=0).count()

        top_offenders = (
            students_list.annotate(report_count=Count("reports"))
            .filter(report_count__gt=0)
            .order_by("-report_count", "-risk_score")[:5]
        )

        top_offenders_data = [
            {
                "name": s.name,
                "admission": s.admission_number,
                "risk_score": s.risk_score,
                "risk_level": s.risk_level,
                "reports": s.report_count,
                "interventions": s.intervention_count,
            }
            for s in top_offenders
        ]

        recommendations = []
        if critical > 0:
            critical_names = ", ".join(
                students_list.filter(risk_level="CRITICAL").values_list("name", flat=True)[
                    :5
                ]
            )
            recommendations.append(
                {
                    "type": "URGENT",
                    "action": f"{critical} students at CRITICAL risk in {stream.name}",
                    "details": f"Students: {critical_names}. Immediate intervention needed for these students.",
                    "steps": [
                        "Schedule individual meetings for each critical student",
                        "Create personalized intervention plans",
                        "Assign counselors to each student",
                        "Hold emergency parent-teacher conferences",
                        "Track progress weekly",
                    ],
                }
            )

        if warning > 3:
            recommendations.append(
                {
                    "type": "WARNING",
                    "action": f"{warning} students at WARNING level in {stream.name}",
                    "details": "Multiple students need monitoring to prevent escalation.",
                    "steps": [
                        "Implement whole-class behavior monitoring",
                        "Contact parents of warning-level students",
                        "Increase teacher supervision",
                        "Create group intervention activities",
                        "Document all incidents and interventions",
                    ],
                }
            )
        elif warning > 0:
            warning_names = ", ".join(
                students_list.filter(risk_level="WARNING").values_list("name", flat=True)[:3]
            )
            recommendations.append(
                {
                    "type": "WARNING",
                    "action": f"{warning} student(s) at WARNING level",
                    "details": f"Students: {warning_names}. Monitor these students closely.",
                    "steps": [
                        "Schedule individual meetings with each student",
                        "Create behavior tracking sheets",
                        "Contact parents for awareness",
                        "Document all interventions",
                    ],
                }
            )

        no_intervention_risk = students_list.filter(
            Q(risk_level="WARNING") | Q(risk_level="CRITICAL"), intervention_count=0
        ).count()
        if no_intervention_risk > 0:
            recommendations.append(
                {
                    "type": "URGENT",
                    "action": f"{no_intervention_risk} at-risk students without interventions",
                    "details": "These students need interventions but none have been recorded.",
                    "steps": [
                        "Create intervention plans immediately",
                        "Schedule meetings with each student",
                        "Assign mentors or counselors",
                        "Document all interventions",
                    ],
                }
            )

        if good == total and total > 0:
            recommendations.append(
                {
                    "type": "SUCCESS",
                    "action": f"{stream.name} is performing excellently",
                    "details": f"All {total} students have good risk levels.",
                    "steps": [
                        "Maintain current positive practices",
                        "Recognize and celebrate class achievements",
                        "Document successful strategies",
                        "Share best practices with other streams",
                    ],
                }
            )

        if not recommendations:
            recommendations.append(
                {
                    "type": "INFO",
                    "action": f"{stream.name} Status: Stable",
                    "details": f"{total} students with an average risk of {round(avg_risk, 1)}%. Continue monitoring.",
                    "steps": [
                        "Maintain regular monitoring",
                        "Continue positive reinforcement",
                        "Document any incidents promptly",
                        "Keep communication channels open with parents",
                    ],
                }
            )

        return JsonResponse(
            {
                "stream": stream.name,
                "statistics": {
                    "total_students": total,
                    "critical_count": critical,
                    "warning_count": warning,
                    "good_count": good,
                    "average_risk": round(avg_risk, 1),
                    "students_with_interventions": with_interventions,
                    "total_interventions": students_list.aggregate(
                        total=Count("intervention_count")
                    )["total"]
                    or sum(s.intervention_count for s in students),
                },
                "top_offenders": top_offenders_data,
                "recommendations": recommendations,
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def ai_all_students(request):
    try:
        students_list = Student.objects.filter(is_active=True).select_related("stream")
        total_reports = DisciplineReport.objects.count()

        all_students_data = [
            {
                "id": student.id,
                "name": student.name,
                "admission": student.admission_number,
                "stream": student.stream.name if student.stream else "N/A",
                "form": student.form,
                "risk_score": student.risk_score,
                "risk_level": student.risk_level,
                "total_reports": student.reports.count(),
                "is_critical": student.risk_level == "CRITICAL",
                "intervention_count": student.intervention_count,
                "days_since_incident": getattr(
                    student, "days_since_last_incident", None
                ),
            }
            for student in students
        ]

        total = len(all_students_data)
        critical = sum(1 for s in all_students_data if s["risk_level"] == "CRITICAL")
        warning = sum(1 for s in all_students_data if s["risk_level"] == "WARNING")
        good = sum(1 for s in all_students_data if s["risk_level"] == "GOOD")
        avg_risk = (
            sum(s["risk_score"] for s in all_students_data) / total if total else 0
        )
        with_interventions = sum(
            1 for s in all_students_data if s["intervention_count"] > 0
        )

        insights = []
        if critical > 0:
            critical_students = [
                s["name"] for s in all_students_data if s["risk_level"] == "CRITICAL"
            ][:5]
            insights.append(
                {
                    "type": "warning",
                    "title": f"{critical} Students Need Immediate Attention",
                    "students": critical_students,
                    "action": "Schedule parent meetings and counseling immediately",
                    "priority": "HIGH",
                }
            )
        if warning > 0:
            warning_students = [
                s["name"] for s in all_students_data if s["risk_level"] == "WARNING"
            ][:5]
            insights.append(
                {
                    "type": "info",
                    "title": f"{warning} Students at Warning Level",
                    "students": warning_students,
                    "action": "Increase monitoring and teacher attention",
                    "priority": "MEDIUM",
                }
            )
        if with_interventions > 0:
            insights.append(
                {
                    "type": "success",
                    "title": f"{with_interventions} Students Have Interventions",
                    "students": [],
                    "action": "Continue monitoring intervention effectiveness",
                    "priority": "LOW",
                }
            )

        return JsonResponse(
            {
                "all_students": all_students_data,
                "total_reports": total_reports,
                "stats": {
                    "total": total,
                    "critical": critical,
                    "warning": warning,
                    "good": good,
                    "avg_risk": round(avg_risk, 1),
                    "with_interventions": with_interventions,
                },
                "insights": insights,
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def student_by_name(request):
    try:
        name = request.GET.get("name", "").strip()
        if not name:
            return JsonResponse({"error": "No name provided."}, status=400)

        student = Student.objects.filter(name__icontains=name, is_active=True).first()
        if not student:
            return JsonResponse({"error": "Student not found."}, status=404)

        reports = student.reports.select_related("category")
        category_breakdown = (
            reports.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return JsonResponse(
            {
                "id": student.id,
                "name": student.name,
                "admission_number": student.admission_number,
                "stream": student.stream.name if student.stream else "N/A",
                "form": student.form,
                "risk_score": student.risk_score,
                "risk_level": student.risk_level,
                "total_reports": student.total_reports,
                "intervention_count": student.intervention_count,
                "days_since_incident": getattr(
                    student, "days_since_last_incident", None
                ),
                "category_breakdown": list(category_breakdown),
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def ai_risk_stats(request):
    """Get overall risk statistics for the AI dashboard."""
    try:
        students_list = Student.objects.filter(is_active=True)
        total = students_list.count()

        stats = {
            "total_students": total,
            "critical_count": students_list.filter(risk_level="CRITICAL").count(),
            "warning_count": students_list.filter(risk_level="WARNING").count(),
            "good_count": students_list.filter(risk_level="GOOD").count(),
            "avg_risk_score": students_list.aggregate(Avg("risk_score"))["risk_score__avg"]
            or 0,
            "max_risk_score": students_list.aggregate(Max("risk_score"))["risk_score__max"]
            or 0,
            "min_risk_score": students_list.aggregate(Min("risk_score"))["risk_score__min"]
            or 0,
            "total_reports": DisciplineReport.objects.count(),
            "reports_today": DisciplineReport.objects.filter(
                reported_at__date=timezone.now().date()
            ).count(),
            "reports_this_week": DisciplineReport.objects.filter(
                reported_at__week=timezone.now().isocalendar()[1]
            ).count(),
            "total_interventions": sum(s.intervention_count for s in students),
            "students_with_interventions": students_list.filter(intervention_count__gt=0).count(),
        }

        category_breakdown = (
            DisciplineReport.objects.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        stats["top_categories"] = list(category_breakdown)

        return JsonResponse({"status": "success", "data": stats})
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def ai_trend_analysis(request):
    """Get trend analysis for students."""
    try:
        days = int(request.GET.get("days", 30))
        start_date = timezone.now() - timedelta(days=days)

        reports = (
            DisciplineReport.objects.filter(reported_at__gte=start_date)
            .values("reported_at__date")
            .annotate(count=Count("id"))
            .order_by("reported_at__date")
        )

        total_students_list = Student.objects.filter(is_active=True).count()
        current_critical = Student.objects.filter(
            is_active=True, risk_level="CRITICAL"
        ).count()
        current_warning = Student.objects.filter(
            is_active=True, risk_level="WARNING"
        ).count()
        current_good = Student.objects.filter(is_active=True, risk_level="GOOD").count()

        improving_students_list = Student.objects.filter(
            is_active=True, risk_level="WARNING", intervention_count__gt=0
        ).count()

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "daily_reports": list(reports),
                    "current_distribution": {
                        "critical": current_critical,
                        "warning": current_warning,
                        "good": current_good,
                        "total": total_students,
                    },
                    "improving_students": improving_students,
                    "period_days": days,
                    "total_reports_period": DisciplineReport.objects.filter(
                        reported_at__gte=start_date
                    ).count(),
                },
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def ai_intervention_suggestions(request, student_id):
    """Get AI-powered intervention suggestions for a student."""
    try:
        student = get_object_or_404(Student, id=student_id, is_active=True)
        suggestions = []
        reports = student.reports.select_related("category")

        category_patterns = (
            reports.values("category__name")
            .annotate(count=Count("id"))
            .filter(count__gte=2)
            .order_by("-count")
        )

        if student.risk_level == "CRITICAL":
            suggestions.append(
                {
                    "priority": "URGENT",
                    "action": "Immediate Crisis Intervention",
                    "description": f"Student has {student.risk_score}% risk. Requires immediate attention.",
                    "steps": [
                        "Contact parents/guardians within 24 hours",
                        "Schedule emergency counseling session",
                        "Create behavior intervention plan",
                        "Document all interventions",
                        "Schedule weekly review meetings",
                    ],
                }
            )

        if student.risk_level == "WARNING":
            suggestions.append(
                {
                    "priority": "HIGH",
                    "action": "Preventive Intervention",
                    "description": f"Student at {student.risk_score}% risk. Implement support systems.",
                    "steps": [
                        "Schedule parent meeting within 1 week",
                        "Assign mentor or peer buddy",
                        "Create behavior tracking sheet",
                        "Monitor daily for 2 weeks",
                        "Document progress or setbacks",
                    ],
                }
            )

        for pattern in category_patterns:
            if pattern["count"] >= 3:
                suggestions.append(
                    {
                        "priority": "HIGH",
                        "action": f'Address {pattern["category__name"]} Pattern',
                        "description": f'{pattern["count"]} incidents in this category. Needs targeted intervention.',
                        "steps": [
                            f'Discuss {pattern["category__name"]} pattern with student',
                            "Create specific strategies for this area",
                            "Monitor for improvement weekly",
                            "Document progress",
                        ],
                    }
                )
            elif pattern["count"] >= 2:
                suggestions.append(
                    {
                        "priority": "MEDIUM",
                        "action": f'Monitor {pattern["category__name"]} Pattern',
                        "description": f'{pattern["count"]} incidents. Watch for escalation.',
                        "steps": [
                            f'Address {pattern["category__name"]} with student',
                            "Track future incidents",
                            "Consider preventive measures",
                        ],
                    }
                )

        if student.intervention_count == 0 and student.risk_level in [
            "WARNING",
            "CRITICAL",
        ]:
            suggestions.append(
                {
                    "priority": "URGENT",
                    "action": "Create Intervention Plan",
                    "description": "No interventions recorded. Plan needed immediately.",
                    "steps": [
                        "Schedule student meeting",
                        "Create intervention plan",
                        "Assign counselor or mentor",
                        "Document interventions",
                        "Review progress weekly",
                    ],
                }
            )

        return JsonResponse(
            {
                "status": "success",
                "student": {
                    "id": student.id,
                    "name": student.name,
                    "risk_level": student.risk_level,
                    "risk_score": student.risk_score,
                    "intervention_count": student.intervention_count,
                },
                "suggestions": suggestions,
                "total_suggestions": len(suggestions),
                "category_patterns": list(category_patterns),
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@user_passes_test(admin_required)
def ai_bulk_risk_update(request):
    """Bulk update risk scores for all students."""
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "POST method required"}, status=405
        )
    try:
        students_list = Student.objects.filter(is_active=True)
        updated_count = 0
        for student in students:
            student.update_risk_score()
            updated_count += 1

        return JsonResponse(
            {
                "status": "success",
                "message": f"Updated {updated_count} students",
                "updated_count": updated_count,
                "total_interventions": sum(s.intervention_count for s in students),
                "timestamp": timezone.now().isoformat(),
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ============================================
# SCHOOL SETUP
# ============================================


@login_required
@user_passes_test(admin_required)
@transaction.atomic
def school_setup(request):
    school, _ = School.objects.get_or_create(id=1)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save_school":
            school.name = request.POST.get("name", "My School").strip()
            school.short_name = request.POST.get("short_name", "").strip()
            school.motto = request.POST.get("motto", "").strip()
            school.address = request.POST.get("address", "").strip()
            school.phone = request.POST.get("phone", "").strip()
            school.email = request.POST.get("email", "").strip()
            school.website = request.POST.get("website", "").strip()

            # FIX (ERROR 7 / logic error 6-8): validate int() conversions
            # instead of letting a bad value raise an uncaught ValueError.
            try:
                school.current_year = int(
                    request.POST.get("current_year", timezone.now().year)
                )
            except (ValueError, TypeError):
                messages.error(request, "Current year must be a whole number.")
                return redirect("core:school_setup")

            try:
                school.terms_per_year = int(request.POST.get("terms_per_year", 3))
            except (ValueError, TypeError):
                messages.error(request, "Terms per year must be a whole number.")
                return redirect("core:school_setup")

            # FIX (CRITICAL ERROR 3): request.POST.get() with no key name
            # always returns the *default* argument you pass it (or None),
            # so these settings could never actually be toggled on.
            school.allow_teacher_registration = (
                request.POST.get("allow_teacher_registration") == "on"
            )
            school.require_teacher_approval = (
                request.POST.get("require_teacher_approval") == "on"
            )
            school.save()
            messages.success(request, "School details saved!")
            return redirect("core:school_setup")

        elif action == "add_grade":
            # Auto-assign order: next available number
            next_order = GradeLevel.objects.filter(school=school).count() + 1
            try:
                GradeLevel.objects.create(
                    school=school,
                    name=request.POST.get("grade_name", "").strip(),
                    code=request.POST.get("grade_code", "").strip(),
                    order=next_order,
                    is_active=True,
                )
                messages.success(request, f"Grade level added with order {next_order}!")
            except (ValueError, TypeError) as e:
                messages.error(request, f"Error adding grade: {e}")
            return redirect("core:school_setup")

        elif action == "delete_grade":
            grade = get_object_or_404(GradeLevel, id=request.POST.get("grade_id"))
            grade_name = grade.name
            student_count = Student.objects.filter(grade_level=grade).count()
            if student_count > 0:
                Student.objects.filter(grade_level=grade).update(grade_level=None)
                messages.warning(
                    request,
                    f'{student_count} students had "{grade_name}" grade removed from their records.',
                )
            grade.delete()
            messages.success(request, f'Grade "{grade_name}" deleted.')
            return redirect("core:school_setup")

        elif action == "add_stream":
            stream_name = request.POST.get("stream_name", "").strip()
            if not stream_name:
                messages.error(request, "Stream name is required.")
            elif Stream.objects.filter(school=school, name=stream_name).exists():
                messages.error(request, f'Stream "{stream_name}" already exists!')
            else:
                Stream.objects.create(
                    school=school,
                    name=stream_name,
                    code=request.POST.get("stream_code", stream_name[:3].upper()),
                    is_active=True,
                )
                invalidate_lookup_caches()
                messages.success(request, f'Stream "{stream_name}" added!')
            return redirect("core:school_setup")

        elif action == "delete_stream":
            # FIX (SECURITY/DATA-LOSS ISSUE 5): deleting a stream used to
            # cascade-delete every student in it with no confirmation step.
            # Now it *blocks* deletion if students are still assigned, and
            # requires an explicit `reassign_to` stream id to move them first.
            stream = get_object_or_404(Stream, id=request.POST.get("stream_id"))
            stream_name = stream.name
            student_count = Student.objects.filter(stream=stream).count()

            if student_count > 0:
                reassign_to_id = request.POST.get("reassign_to")
                if not reassign_to_id:
                    messages.error(
                        request,
                        f'"{stream_name}" has {student_count} students. Choose a stream to move '
                        "them to before deleting, or deactivate the stream instead.",
                    )
                    return redirect("core:school_setup")
                try:
                    reassign_to = Stream.objects.get(
                        id=reassign_to_id, is_active=True
                    )
                except Stream.DoesNotExist:
                    messages.error(request, "Invalid reassignment stream.")
                    return redirect("core:school_setup")
                Student.objects.filter(stream=stream).update(stream=reassign_to)
                messages.warning(
                    request,
                    f'{student_count} students moved from "{stream_name}" to "{reassign_to.name}".',
                )

            stream.delete()
            invalidate_lookup_caches()
            messages.success(request, f'Stream "{stream_name}" deleted.')
            return redirect("core:school_setup")

        elif action == "add_term":
            try:
                term_number = int(request.POST.get("term_number", 1))
                term_year = int(request.POST.get("term_year", timezone.now().year))
            except (ValueError, TypeError):
                messages.error(request, "Term number and year must be whole numbers.")
                return redirect("core:school_setup")

            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")

            # FIX (logic error 6): validate start_date < end_date.
            if start_date and end_date and start_date >= end_date:
                messages.error(request, "Start date must be before end date.")
                return redirect("core:school_setup")

            try:
                term = AcademicTerm.objects.create(
                    school=school,
                    name=request.POST.get("term_name", "").strip(),
                    term_number=term_number,
                    year=term_year,
                    start_date=start_date,
                    end_date=end_date,
                    is_current=request.POST.get("is_current") == "on",
                )
                if term.is_current:
                    AcademicTerm.objects.filter(school=school).exclude(
                        id=term.id
                    ).update(is_current=False)
                messages.success(request, "Term added!")
            except (ValueError, TypeError) as e:
                messages.error(request, f"Error adding term: {e}")
            return redirect("core:school_setup")

        elif action == "delete_term":
            term = get_object_or_404(AcademicTerm, id=request.POST.get("term_id"))
            term.delete()
            messages.success(request, "Term deleted!")
            return redirect("core:school_setup")

    context = {
        "school": school,
        "grades": GradeLevel.objects.filter(school=school).order_by("order", "name"),
        "streams": Stream.objects.filter(school=school, is_active=True).order_by(
            "name"
        ),
        "terms": AcademicTerm.objects.filter(school=school).order_by(
            "-year", "-term_number"
        ),
        **_get_notification_context(request),
    }
    return render(request, "school_setup.html", context)


# ============================================================================
# BULK UPLOAD - ROBUST UNIVERSAL EXTRACTOR
#
# Accepts .xlsx / .xls / .csv / .txt files where the layout may be messy:
# columns in any order, extra blank/junk columns, multiple sheets, headers
# with typos, or no headers at all. Streams/grades are resolved against
# what the school actually has configured, not a hardcoded list, and any
# new stream/grade name found in the file is auto-created so nothing silently
# gets lost into a generic bucket.
# ============================================================================

_HEADER_ALIASES = {
    "name": [
        "name",
        "student",
        "student name",
        "full name",
        "fullname",
        "names",
        "pupil",
        "learner",
    ],
    "admission": [
        "admission",
        "admission number",
        "admission_no",
        "adm",
        "adm no",
        "admno",
        "reg",
        "reg no",
        "reg number",
        "registration",
        "registration number",
        "id",
        "student id",
        "index number",
        "index no",
    ],
    "grade": ["grade", "form", "class", "level", "grade level", "year group"],
    "stream": ["stream", "section", "house", "class stream"],
    "year": ["year", "academic year", "intake year"],
    "notes": ["notes", "note", "comment", "comments", "remarks"],
}

# SECURITY (ISSUE 3): explicit allow-list of upload types + a hard size cap,
# enforced in bulk_upload_students() before any parsing is attempted.
_ALLOWED_UPLOAD_EXTENSIONS = (".xlsx", ".xls", ".csv", ".txt")
_MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def _best_header_match(column_name, min_ratio=0.72):
    """Fuzzy-match a spreadsheet column header against known field aliases."""
    col = str(column_name).strip().lower()
    best_field, best_score = None, 0.0
    for field, aliases in _HEADER_ALIASES.items():
        for alias in aliases:
            if col == alias:
                return field
            score = difflib.SequenceMatcher(None, col, alias).ratio()
            if score > best_score:
                best_field, best_score = field, score
    return best_field if best_score >= min_ratio else None


def _normalize_admission(raw):
    """Normalize an admission/registration number: trim, drop stray spaces, uppercase letters."""
    if raw is None:
        return ""
    value = str(raw).strip()
    # Excel sometimes turns "8896" into "8896.0" when the column is numeric-typed.
    if re.match(r"^\d+\.0$", value):
        value = value[:-2]
    return value.upper()


def _match_known_token(token, known_values):
    """Case-insensitive exact/substring match of `token` against known DB values (streams/grades)."""
    token_lower = token.strip().lower()
    for value in known_values:
        if value.lower() == token_lower:
            return value
    for value in known_values:
        if value.lower() in token_lower or token_lower in value.lower():
            return value
    return None


def _detect_grade_in_text(text, known_grades):
    match = _match_known_token(text, known_grades)
    if match:
        return match
    patterns = {
        "Form 1": [
            r"form\s*1\b",
            r"\bf1\b",
            r"grade\s*1\b",
            r"1st\s*form",
            r"form\s+one",
        ],
        "Form 2": [
            r"form\s*2\b",
            r"\bf2\b",
            r"grade\s*2\b",
            r"2nd\s*form",
            r"form\s+two",
        ],
        "Form 3": [
            r"form\s*3\b",
            r"\bf3\b",
            r"grade\s*3\b",
            r"3rd\s*form",
            r"form\s+three",
        ],
        "Form 4": [
            r"form\s*4\b",
            r"\bf4\b",
            r"grade\s*4\b",
            r"4th\s*form",
            r"form\s+four",
        ],
    }
    for grade, pats in patterns.items():
        if any(re.search(p, text.lower()) for p in pats):
            return grade
    return None


def bulk_extract_student_rows(
    raw_rows, known_streams, known_grades, default_stream, default_grade
):
    """
    Core row-level extractor shared by the Excel and text pipelines.

    `raw_rows` is a list of lists of raw string tokens (one list per source
    row/line, already split on whatever separator was found). For each row,
    tries to identify an admission number, a name, and optionally a
    stream/grade/year, tolerating tokens appearing in any order.
    """
    results = []
    for tokens in raw_rows:
        tokens = [t.strip() for t in tokens if t and t.strip()]
        if not tokens:
            continue

        admission = None
        stream = None
        grade = None
        year = None
        name_parts = []

        for tok in tokens:
            if (
                admission is None
                and re.match(r"^[A-Za-z]*\d{3,8}[A-Za-z]?$", tok)
                and any(c.isdigit() for c in tok)
            ):
                admission = _normalize_admission(tok)
                continue
            stream_match = _match_known_token(tok, known_streams)
            if stream is None and stream_match:
                stream = stream_match
                continue
            grade_match = _detect_grade_in_text(tok, known_grades)
            if grade is None and grade_match:
                grade = grade_match
                continue
            if year is None and re.match(r"^(19|20)\d{2}$", tok):
                year = tok
                continue
            # Otherwise, treat as part of the student's name.
            name_parts.append(tok)

        name = " ".join(name_parts).strip()
        # Clean stray leftover separators from name fragments.
        name = re.sub(r"\s+", " ", name).strip(" -|,;")

        if admission and name and len(name) >= 2:
            row = {
                "admission": admission,
                "name": name,
                "stream": stream or default_stream,
                "grade": grade or default_grade,
            }
            if year:
                row["year"] = year
            results.append(row)

    return results


def extract_from_excel(df, known_streams=None, known_grades=None):
    """
    Extract student rows from a DataFrame (one Excel/CSV sheet).

    Tries, in order:
      1. Fuzzy header-name matching (handles "Adm No", "Reg Number", etc).
      2. Positional fallback (col0=name, col1=admission, col2=grade, col3=stream)
         if headers can't be confidently identified.
      3. Whole-row token scanning (handles scattered/disorganized sheets where
         neither of the above works cleanly).
    """
    known_streams = known_streams or []
    known_grades = known_grades or []
    default_stream = known_streams[0] if known_streams else "Unassigned"
    default_grade = known_grades[0] if known_grades else "Form 1"

    students = []

    field_to_col = {}
    for col in df.columns:
        field = _best_header_match(col)
        if field and field not in field_to_col:
            field_to_col[field] = col

    has_confident_headers = "name" in field_to_col and "admission" in field_to_col

    if has_confident_headers:
        for _, row in df.iterrows():

            def cell(field):
                col = field_to_col.get(field)
                if col is None or pd.isna(row[col]):
                    return ""
                return str(row[col]).strip()

            name = cell("name")
            admission = _normalize_admission(cell("admission"))
            if not name or not admission:
                continue
            grade_raw = cell("grade")
            stream_raw = cell("stream")
            year_raw = cell("year")
            notes_raw = cell("notes")

            grade = (
                _detect_grade_in_text(grade_raw, known_grades) if grade_raw else None
            )
            stream = (
                _match_known_token(stream_raw, known_streams) if stream_raw else None
            )

            student_data = {
                "name": name,
                "admission": admission,
                "grade": grade or grade_raw or default_grade,
                "stream": stream or stream_raw or default_stream,
            }
            if year_raw:
                student_data["year"] = year_raw
            if notes_raw:
                student_data["notes"] = notes_raw
            students.append(student_data)

        if students:
            return students
        # Headers looked right but nothing extracted (e.g. all rows blank) -
        # fall through to the scanning strategy below as a safety net.

    # Positional / scanning fallback for headerless or badly-labelled sheets.
    raw_rows = []
    for _, row in df.iterrows():
        tokens = [
            str(v).strip() for v in row.tolist() if pd.notna(v) and str(v).strip()
        ]
        if tokens:
            raw_rows.append(tokens)

    return bulk_extract_student_rows(
        raw_rows, known_streams, known_grades, default_stream, default_grade
    )


def extract_from_text(content, known_streams=None, known_grades=None):
    """
    Intelligently extract student data from a plain-text / notepad upload.
    Supports pipe/comma/tab/semicolon/dash-separated lines, "Name (Admission)"
    style lines, and free-form lines where tokens appear in any order.
    """
    known_streams = known_streams or []
    known_grades = known_grades or []
    default_stream = known_streams[0] if known_streams else "Unassigned"
    default_grade = known_grades[0] if known_grades else "Form 1"

    raw_rows = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # "Name (Admission)" shorthand -> pull admission out explicitly, then
        # treat the remainder of the line as ordinary tokens too.
        paren_match = re.search(r"([^(]+)\(([A-Za-z0-9]+)\)", line)
        if paren_match:
            name_guess = paren_match.group(1).strip()
            adm_guess = paren_match.group(2).strip()
            remainder = line[paren_match.end() :]
            tokens = [name_guess, adm_guess] + re.split(r"[|\t,;]|(?:\s-\s)", remainder)
            raw_rows.append([t for t in tokens if t and t.strip()])
            continue

        sep_found = next((s for s in ["|", "\t", ",", ";", " - "] if s in line), None)
        if sep_found:
            raw_rows.append(line.split(sep_found))
        else:
            # No clear separator - split on whitespace but keep multi-word
            # names together isn't possible without more structure, so hand
            # the whole line as individual whitespace tokens to the row
            # extractor, which is tolerant of name fragments arriving as
            # separate tokens.
            raw_rows.append(re.split(r"\s+", line))

    return bulk_extract_student_rows(
        raw_rows, known_streams, known_grades, default_stream, default_grade
    )


def _read_uploaded_text(upload_file):
    """Decode an uploaded text file, tolerating common Windows encodings."""
    raw = upload_file.read()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    # Last resort: replace undecodable bytes rather than crash the upload.
    return raw.decode("utf-8", errors="replace")


@login_required
@user_passes_test(admin_required)
@transaction.atomic
def bulk_upload_students(request):
    if request.method != "POST" or not request.FILES.get("upload_file"):
        return redirect("/admin-dashboard/")

    upload_file = request.FILES["upload_file"]
    file_name = upload_file.name.lower()
    ext = os.path.splitext(file_name)[1]

    # FIX (SECURITY ISSUE 3): validate size and extension BEFORE parsing.
    if ext not in _ALLOWED_UPLOAD_EXTENSIONS:
        messages.error(
            request,
            f"Unsupported file type '{ext}'. Please upload .xlsx, .xls, .csv, or .txt.",
        )
        return redirect("/admin-dashboard/")
    if upload_file.size > _MAX_UPLOAD_SIZE_BYTES:
        messages.error(request, "File is too large. Maximum upload size is 10MB.")
        return redirect("/admin-dashboard/")

    try:
        school = School.objects.first()
        if not school:
            messages.error(request, "Please set up your school first.")
            return redirect("core:school_setup")

        known_streams = list(
            Stream.objects.filter(is_active=True).values_list("name", flat=True)
        )
        known_grades = list(
            GradeLevel.objects.filter(is_active=True).values_list("name", flat=True)
        ) or [choice[0] for choice in Student.FORM_CHOICES]

        students_data = []

        if file_name.endswith((".xlsx", ".xls")):
            # Read every sheet, not just the first - scattered data sometimes
            # lands on "Sheet2" or a renamed tab.
            sheets = pd.read_excel(upload_file, sheet_name=None, dtype=str)
            for _sheet_name, df in sheets.items():
                if df.empty:
                    continue
                students_data.extend(
                    extract_from_excel(df, known_streams, known_grades)
                )
        elif file_name.endswith(".csv"):
            df = pd.read_csv(upload_file, dtype=str)
            students_data.extend(extract_from_excel(df, known_streams, known_grades))
        else:
            content = _read_uploaded_text(upload_file)
            students_data.extend(
                extract_from_text(content, known_streams, known_grades)
            )

        if not students_data:
            messages.error(
                request,
                "No valid student data could be found in that file. Make sure each row/line "
                "has at least a name and an admission number.",
            )
            return redirect("/admin-dashboard/")

        # De-duplicate admission numbers *within this batch* before touching the DB.
        deduped = {}
        batch_duplicates = 0
        for row in students_data:
            key = row["admission"]
            if key in deduped:
                batch_duplicates += 1
                continue
            deduped[key] = row
        students_data = list(deduped.values())

        # FIX (OPTIMIZATION 4 / IMPROVEMENT via bulk_create): resolve/create
        # grades and streams first, then batch-create the new students in a
        # single query instead of one INSERT per row.
        grade_cache = {}
        stream_cache = {}

        def get_or_create_grade(name):
            if name not in grade_cache:
                grade_cache[name], _ = GradeLevel.objects.get_or_create(
                    school=school,
                    name=name,
                    defaults={"code": name[:3].upper(), "order": 0, "is_active": True},
                )
            return grade_cache[name]

        def get_or_create_stream(name):
            if name not in stream_cache:
                stream_cache[name], _ = Stream.objects.get_or_create(
                    school=school,
                    name=name,
                    defaults={"code": name[:3].upper(), "is_active": True},
                )
            return stream_cache[name]

        existing_admissions = set(
            Student.objects.filter(
                admission_number__in=[row["admission"] for row in students_data]
            ).values_list("admission_number", flat=True)
        )

        new_students = []
        errors = []
        already_existed = len(existing_admissions)

        for student_data in students_data:
            if student_data["admission"] in existing_admissions:
                continue
            try:
                grade_name = student_data.get("grade") or "Form 1"
                grade = get_or_create_grade(grade_name)
                stream_name = student_data.get("stream") or "Unassigned"
                stream = get_or_create_stream(stream_name)

                year_value = student_data.get("year")
                try:
                    year_value = int(year_value) if year_value else timezone.now().year
                except (ValueError, TypeError):
                    year_value = timezone.now().year

                new_students.append(
                    Student(
                        admission_number=student_data["admission"],
                        name=student_data["name"],
                        stream=stream,
                        grade_level=grade,
                        form=grade_name,
                        year=year_value,
                        optional_notes=student_data.get("notes", ""),
                        created_by=request.user,
                        is_active=True,
                    )
                )
            except (ValueError, TypeError, KeyError) as row_error:
                errors.append(f'{student_data.get("admission", "?")}: {row_error}')

        Student.objects.bulk_create(new_students, batch_size=500)
        added = len(new_students)
        invalidate_lookup_caches()

        if added:
            messages.success(request, f"Successfully added {added} students.")
        if already_existed:
            messages.info(
                request,
                f"{already_existed} rows matched an admission number already in the system and were skipped.",
            )
        if batch_duplicates:
            messages.info(
                request,
                f"{batch_duplicates} duplicate rows within the file itself were skipped.",
            )
        if errors:
            for error in errors[:5]:
                messages.warning(request, error)
            if len(errors) > 5:
                messages.warning(request, f"and {len(errors) - 5} more row errors.")
        if not added and not already_existed and not errors:
            messages.warning(
                request, "The file was read but no new students were identified."
            )

    except (ValueError, TypeError) as e:
        messages.error(request, f"Error processing file: {e}")

    return redirect("/admin-dashboard/")


def generate_excel_template(request):
    """Generate an Excel template for bulk upload."""
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="student_upload_template.xlsx"'
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"
    ws.append(["name", "admission_number", "grade", "stream", "year", "notes"])
    for row in [
        ["John Doe", "8896", "Form 1", "Gonza", "2026", ""],
        ["Jane Smith", "8902", "Form 2", "Kizza", "2026", ""],
        ["Bob Johnson", "8916", "Form 3", "Lwanga", "2026", ""],
        ["Alice Williams", "8938", "Form 4", "Mulumba", "2026", ""],
    ]:
        ws.append(row)
    wb.save(response)
    return response


def download_text_template(request):
    """Generate a text-file template for bulk upload."""
    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = (
        'attachment; filename="student_upload_template.txt"'
    )
    response.write(
        "# Student Bulk Upload Template\n"
        "# Any of these layouts work - columns can even appear in any order:\n"
        "# admission - name - stream - grade\n"
        "# admission, name, stream, grade\n"
        "# name (admission) stream grade\n"
        "8896 - John Doe - Gonza - Form 1\n"
        "8902, Jane Smith, Kizza, Form 2\n"
        "Bob Johnson (8916) Lwanga Form 3\n"
        "Alice Williams 8938 Mulumba Form 4\n"
        "# Loosely formatted lines also work:\n"
        "8896 John Doe Gonza Form 1\n"
        "8896 | John Doe | Gonza | Form 1\n"
    )
    return response


# ============================================
# AI CHAT VIEWS
# ============================================


@login_required
def ai_chat_page(request):
    """Render the AI Chat page."""
    students_list = Student.objects.filter(is_active=True).select_related("stream")
    context = {
        "streams": _get_active_streams(),
        "total_students": students_list.count(),
    }
    return render(request, "ai_chat.html", context)


@login_required
@rate_limited("ai_chat", limit=30, window_seconds=60)
def ai_chat_api(request):
    """API endpoint for AI chat. Requires a valid CSRF token (standard Django POST protection)."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        student_id = data.get("student_id")
        conversation_history = data.get("history", [])
        use_ai = data.get("use_ai", True)

        if not user_message:
            return JsonResponse({"error": "Please enter a message"}, status=400)

        if not use_ai:
            return JsonResponse(
                {
                    "success": True,
                    "response": "Fallback mode is enabled. Switch to AI mode for intelligent responses.",
                    "mode": "fallback",
                }
            )

        try:
            from .ai_chat import PollinationAIChat

            ai = PollinationAIChat()
            result = ai.chat(
                user_message=user_message,
                student_id=student_id,
                conversation_history=conversation_history,
            )
            if result["success"]:
                return JsonResponse(
                    {
                        "success": True,
                        "response": result["response"],
                        "usage": result.get("usage", {}),
                        "mode": "ai",
                        "provider": result.get("provider"),
                        "model_used": result.get("model_used"),
                    }
                )
            return JsonResponse(
                {
                    "success": False,
                    "error": result.get(
                        "error", "AI service unavailable. Please try again."
                    ),
                    "mode": "error",
                },
                status=503,
            )
        except ImportError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "AI service not configured. Please contact administrator.",
                    "mode": "error",
                },
                status=500,
            )
        except (ValueError, TypeError) as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"AI service error: {str(e)}",
                    "mode": "error",
                },
                status=500,
            )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def ai_chat_student_context(request):
    """Get student context for AI chat - real data from the database."""
    student_id = request.GET.get("student_id")
    if not student_id:
        return JsonResponse({"error": "Student ID required"}, status=400)
    try:
        student = Student.objects.get(id=student_id, is_active=True)
        reports = student.reports.select_related("category")
        data = {
            "id": student.id,
            "name": student.name,
            "admission_number": student.admission_number,
            "stream": student.stream.name if student.stream else "N/A",
            "form": student.form,
            "risk_score": student.risk_score,
            "risk_level": student.risk_level,
            "total_reports": reports.count(),
            "recent_reports": [],
        }
        for report in reports.order_by("-reported_at")[:5]:
            data["recent_reports"].append(
                {
                    "date": report.reported_at.strftime("%Y-%m-%d %H:%M"),
                    "category": report.category.name,
                    "rating": get_rating_display(report),
                    "points": report.points,
                }
            )
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)


# ============================================
# ADDITIONAL AI VIEWS
# ============================================


@login_required
def ai_predictive_analysis(request):
    """Predict future risk based on current patterns."""
    try:
        students_list = Student.objects.filter(is_active=True)
        predictions = []

        for student in students:
            reports = student.reports.order_by("reported_at")
            total_reports = reports.count()
            if total_reports == 0:
                continue

            if total_reports >= 2:
                first_report = reports.first()
                last_report = reports.last()
                days_diff = (last_report.reported_at - first_report.reported_at).days
                reports_per_month = (
                    (total_reports / days_diff) * 30 if days_diff > 0 else total_reports
                )
            else:
                reports_per_month = total_reports

            severity_scores = [r.points for r in reports]
            if len(severity_scores) >= 2:
                severity_trend = severity_scores[-1] - severity_scores[0]
                trend = (
                    "WORSENING"
                    if severity_trend > 10
                    else "IMPROVING" if severity_trend < -10 else "STABLE"
                )
            else:
                trend = "STABLE"

            days_since = (
                max(0, (timezone.now() - student.last_incident_date).days)
                if student.last_incident_date
                else None
            )

            predicted_risk = student.risk_score
            if reports_per_month > 2 and trend == "WORSENING":
                predicted_risk = min(100, predicted_risk + 20)
            elif reports_per_month > 1 and trend == "WORSENING":
                predicted_risk = min(100, predicted_risk + 10)
            elif trend == "IMPROVING" and student.intervention_count > 0:
                predicted_risk = max(0, predicted_risk - 10)
            if days_since and days_since > 30 and student.risk_level == "WARNING":
                predicted_risk = max(0, predicted_risk - 5)

            predicted_level = (
                "CRITICAL"
                if predicted_risk >= 60
                else "WARNING" if predicted_risk >= 30 else "GOOD"
            )

            predictions.append(
                {
                    "student_id": student.id,
                    "name": student.name,
                    "admission_number": student.admission_number,
                    "stream": student.stream.name if student.stream else "N/A",
                    "current_risk": student.risk_score,
                    "current_level": student.risk_level,
                    "predicted_risk": round(predicted_risk, 1),
                    "predicted_level": predicted_level,
                    "reports_per_month": round(reports_per_month, 2),
                    "severity_trend": trend,
                    "days_since_incident": days_since,
                    "intervention_count": student.intervention_count,
                    "needs_attention": predicted_risk >= 60
                    or (predicted_risk >= 30 and trend == "WORSENING"),
                    "urgency": (
                        "HIGH"
                        if predicted_risk >= 60
                        else "MEDIUM" if predicted_risk >= 30 else "LOW"
                    ),
                }
            )

        urgency_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        predictions.sort(key=lambda x: urgency_order.get(x["urgency"], 3))

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "predictions": predictions,
                    "summary": {
                        "total_analyzed": len(predictions),
                        "high_risk_count": sum(
                            1 for p in predictions if p["urgency"] == "HIGH"
                        ),
                        "medium_risk_count": sum(
                            1 for p in predictions if p["urgency"] == "MEDIUM"
                        ),
                        "low_risk_count": sum(
                            1 for p in predictions if p["urgency"] == "LOW"
                        ),
                        "timestamp": timezone.now().isoformat(),
                    },
                },
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def ai_behavior_patterns(request):
    """Identify behavior patterns across the school."""
    try:
        days = int(request.GET.get("days", 90))
        start_date = timezone.now() - timedelta(days=days)

        reports = DisciplineReport.objects.filter(
            reported_at__gte=start_date
        ).select_related("student", "category", "reported_by")
        total_reports = reports.count()
        if total_reports == 0:
            return JsonResponse(
                {
                    "status": "success",
                    "data": {
                        "message": "No reports in the selected time period",
                        "patterns": [],
                    },
                }
            )

        top_categories = list(
            reports.values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        day_patterns = (
            reports.annotate(day=ExtractWeekDay("reported_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        day_names = {
            1: "Sunday",
            2: "Monday",
            3: "Tuesday",
            4: "Wednesday",
            5: "Thursday",
            6: "Friday",
            7: "Saturday",
        }
        weekday_patterns = [
            {
                "day": day_names.get(p["day"], "Unknown"),
                "count": p["count"],
                "percentage": round((p["count"] / total_reports) * 100, 1),
            }
            for p in day_patterns
        ]

        student_patterns = (
            reports.values(
                "student__name",
                "student__stream__name",
            )
            .annotate(count=Count("id"))
            .filter(count__gte=3)
            .order_by("-count")[:10]
        )
        top_students = [
            {
                "name": p["student__name"],
                "stream": p["student__stream__name"],
                "report_count": p["count"],
            }
            for p in student_patterns
        ]

        teacher_patterns = (
            reports.values("reported_by__username")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        top_reporters = [
            {
                "teacher": p["reported_by__username"],
                "report_count": p["count"],
                "percentage": round((p["count"] / total_reports) * 100, 1),
            }
            for p in teacher_patterns
        ]

        multi_report_students = (
            Student.objects.filter(is_active=True)
            .annotate(report_count=Count("reports"))
            .filter(report_count__gte=2)
        )
        co_occurrence = []
        for student in multi_report_students[:20]:
            categories = list(
                student.reports.values_list("category__name", flat=True).distinct()
            )
            if len(categories) >= 2:
                co_occurrence.append(
                    {
                        "student": student.name,
                        "categories": categories,
                        "total_reports": student.reports.count(),
                    }
                )

        # Flag students whose severity clearly shifted between their earliest
        # and latest report (a proxy for risk transitions, since we don't
        # keep historical risk-level snapshots).
        risk_transitions = []
        for student in Student.objects.filter(is_active=True):
            reports_qs = student.reports.order_by("reported_at")
            if reports_qs.count() >= 2:
                first_points = reports_qs.first().points
                last_points = reports_qs.last().points
                if last_points - first_points >= 15:
                    risk_transitions.append(
                        {
                            "student": student.name,
                            "from_risk": "lower severity",
                            "to_risk": student.risk_level,
                            "improved": False,
                        }
                    )
                elif first_points - last_points >= 15:
                    risk_transitions.append(
                        {
                            "student": student.name,
                            "from_risk": "higher severity",
                            "to_risk": student.risk_level,
                            "improved": True,
                        }
                    )

        insights = []
        if top_categories and top_categories[0]["count"] > total_reports * 0.3:
            top_cat = top_categories[0]
            insights.append(
                {
                    "type": "category_dominance",
                    "title": f'Dominant Category: {top_cat["category__name"]}',
                    "description": f'{top_cat["count"]} reports ({round((top_cat["count"] / total_reports) * 100, 1)}%) in this category',
                    "recommendation": "Consider targeted interventions for this category",
                }
            )

        if weekday_patterns:
            peak_day = max(weekday_patterns, key=lambda x: x["count"])
            if peak_day["percentage"] > 20:
                insights.append(
                    {
                        "type": "peak_day",
                        "title": f'Peak Day: {peak_day["day"]}',
                        "description": f'{peak_day["count"]} reports ({peak_day["percentage"]}%) occur on {peak_day["day"]}',
                        "recommendation": "Consider increased monitoring on this day",
                    }
                )

        if top_students and top_students[0]["report_count"] > 3:
            insights.append(
                {
                    "type": "frequent_offenders",
                    "title": f"Frequent Offenders: {len(top_students)} students with 3+ reports",
                    "description": f'Top: {top_students[0]["name"]} ({top_students[0]["report_count"]} reports)',
                    "recommendation": "Implement individual behavior plans for these students",
                }
            )

        worsening = sum(1 for t in risk_transitions if not t["improved"])
        improving = sum(1 for t in risk_transitions if t["improved"])
        if worsening > improving:
            insights.append(
                {
                    "type": "risk_trend",
                    "title": f"Risk Trend: Worsening ({worsening} students)",
                    "description": f"More students are getting worse than improving ({improving})",
                    "recommendation": "Review school-wide intervention strategies",
                }
            )
        elif improving > worsening:
            insights.append(
                {
                    "type": "risk_trend",
                    "title": f"Risk Trend: Improving ({improving} students)",
                    "description": f"More students are improving than getting worse ({worsening})",
                    "recommendation": "Continue current effective practices",
                }
            )

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "period_days": days,
                    "total_reports": total_reports,
                    "category_patterns": top_categories,
                    "weekday_patterns": weekday_patterns,
                    "top_students": top_students,
                    "top_reporters": top_reporters,
                    "co_occurrence": co_occurrence[:10],
                    "risk_transitions": risk_transitions[:10],
                    "insights": insights,
                },
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def ai_intervention_effectiveness(request):
    """Measure effectiveness of interventions by comparing early vs. later report severity."""
    try:
        students_with_interventions = Student.objects.filter(
            intervention_count__gt=0, is_active=True
        ).select_related("stream")
        if not students_with_interventions.exists():
            return JsonResponse(
                {
                    "status": "success",
                    "data": {
                        "message": "No students with interventions recorded",
                        "effectiveness": [],
                    },
                }
            )

        effectiveness_data = []
        improved_count = worsened_count = stable_count = 0

        for student in students_with_interventions:
            reports = list(student.reports.order_by("reported_at"))
            total_reports = len(reports)
            if total_reports < 2:
                continue

            midpoint = total_reports // 2
            before_reports = reports[:midpoint] or reports[:1]
            after_reports = reports[midpoint:]

            before_avg = sum(r.points for r in before_reports) / len(before_reports)
            after_avg = sum(r.points for r in after_reports) / len(after_reports)
            risk_change = after_avg - before_avg

            if risk_change < -5:
                status, effectiveness = "IMPROVED", "High"
                improved_count += 1
            elif risk_change < 0:
                status, effectiveness = "SLIGHTLY_IMPROVED", "Medium"
                improved_count += 1
            elif risk_change == 0:
                status, effectiveness = "STABLE", "Moderate"
                stable_count += 1
            elif risk_change < 10:
                status, effectiveness = "SLIGHTLY_WORSENED", "Low"
                worsened_count += 1
            else:
                status, effectiveness = "WORSENED", "Needs Review"
                worsened_count += 1

            effectiveness_data.append(
                {
                    "student_id": student.id,
                    "name": student.name,
                    "admission_number": student.admission_number,
                    "stream": student.stream.name if student.stream else "N/A",
                    "current_risk": student.risk_score,
                    "risk_level": student.risk_level,
                    "intervention_count": student.intervention_count,
                    "before_avg_risk": round(before_avg, 1),
                    "after_avg_risk": round(after_avg, 1),
                    "risk_change": round(risk_change, 1),
                    "status": status,
                    "effectiveness": effectiveness,
                    "total_reports": total_reports,
                }
            )

        effectiveness_order = {
            "High": 0,
            "Medium": 1,
            "Moderate": 2,
            "Low": 3,
            "Needs Review": 4,
        }
        effectiveness_data.sort(
            key=lambda x: effectiveness_order.get(x["effectiveness"], 5)
        )

        total_analyzed = len(effectiveness_data)
        effectiveness_rate = (
            round((improved_count / total_analyzed) * 100, 1) if total_analyzed else 0
        )

        recommendations = []
        if improved_count > worsened_count:
            recommendations.append(
                {
                    "type": "success",
                    "title": f"Interventions are working ({improved_count} students improved)",
                    "description": f"Effectiveness rate: {effectiveness_rate}%",
                    "action": "Continue current intervention strategies",
                }
            )
        elif worsened_count > improved_count:
            recommendations.append(
                {
                    "type": "warning",
                    "title": f"Interventions need review ({worsened_count} students worsened)",
                    "description": f"Only {effectiveness_rate}% of interventions are effective",
                    "action": "Review and revise intervention strategies",
                }
            )
        else:
            recommendations.append(
                {
                    "type": "info",
                    "title": f"Mixed results ({improved_count} improved, {worsened_count} worsened)",
                    "description": f"Effectiveness rate: {effectiveness_rate}%",
                    "action": "Analyze what works and scale successful interventions",
                }
            )

        for student_data in effectiveness_data[:5]:
            if student_data["effectiveness"] == "Needs Review":
                recommendations.append(
                    {
                        "type": "urgent",
                        "title": f'Review: {student_data["name"]}',
                        "description": f'Risk increased by {student_data["risk_change"]} points despite {student_data["intervention_count"]} interventions',
                        "action": "Create new intervention plan and escalate to counselor",
                    }
                )
            elif student_data["effectiveness"] == "Low":
                recommendations.append(
                    {
                        "type": "warning",
                        "title": f'Monitor: {student_data["name"]}',
                        "description": f'Risk increased slightly (+{student_data["risk_change"]} points)',
                        "action": "Review current intervention and adjust strategy",
                    }
                )

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "effectiveness_data": effectiveness_data,
                    "summary": {
                        "total_analyzed": total_analyzed,
                        "improved_count": improved_count,
                        "worsened_count": worsened_count,
                        "stable_count": stable_count,
                        "effectiveness_rate": effectiveness_rate,
                    },
                    "recommendations": recommendations,
                    "timestamp": timezone.now().isoformat(),
                },
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ============================================
# USER MANAGEMENT
# ============================================


@login_required
@user_passes_test(admin_required)
def manage_users(request):
    teacher_users = (
        User.objects.filter(groups__name__in=["ClassTeacher", "Teacher"])
        .select_related("teacher_profile")
        .prefetch_related("groups")
        .distinct()
    )

    status_filter = request.GET.get("status", "").strip()
    if status_filter == "pending":
        teacher_users = teacher_users.filter(
            teacher_profile__is_approved=False, teacher_profile__is_suspended=False
        )
    elif status_filter == "approved":
        teacher_users = teacher_users.filter(
            teacher_profile__is_approved=True, teacher_profile__is_suspended=False
        )
    elif status_filter == "suspended":
        teacher_users = teacher_users.filter(teacher_profile__is_suspended=True)

    context = {
        "teacher_users": teacher_users,
        "status_filter": status_filter,
        **_get_notification_context(request),
    }
    return render(request, "manage_users.html", context)


@login_required
@user_passes_test(admin_required)
@require_POST
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_teacher_profile(user)
    if profile:
        profile.is_approved = True
        profile.approved_at = timezone.now()
        profile.approved_by = request.user
        profile.save()
        notification = Notification.objects.create(
            title="Account Approved",
            message=f"Your account has been approved by {request.user.get_full_name() or request.user.username}.",
            notification_type="info",
        )
        notification.target_users.add(user)
        messages.success(request, f"User {user.username} approved.")
    else:
        messages.error(request, "Teacher profile not found.")
    return redirect("core:manage_users")


@login_required
@user_passes_test(admin_required)
@require_POST
def suspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot suspend an admin account.")
        return redirect("core:manage_users")
    reason = request.POST.get("reason", "No reason provided.").strip()
    profile = get_teacher_profile(user)
    if profile:
        profile.is_suspended = True
        profile.suspension_reason = reason
        profile.suspended_at = timezone.now()
        profile.save()
        messages.success(request, f"User {user.username} suspended.")
    else:
        messages.error(request, "Teacher profile not found.")
    return redirect("core:manage_users")


@login_required
@user_passes_test(admin_required)
@require_POST
def unsuspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_teacher_profile(user)
    if profile:
        profile.is_suspended = False
        profile.suspension_reason = ""
        profile.suspended_at = None
        profile.save()
        messages.success(request, f"User {user.username} reinstated.")
    else:
        messages.error(request, "Teacher profile not found.")
    return redirect("core:manage_users")


@login_required
@user_passes_test(admin_required)
@require_POST
def delete_user_permanent(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete an admin account.")
        return redirect("core:manage_users")
    username = user.username
    user.delete()
    messages.success(request, f"User {username} permanently deleted.")
    return redirect("core:manage_users")


@login_required
@user_passes_test(admin_required)
@require_POST
def ban_user_permanent(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot ban an admin account.")
        return redirect("core:manage_users")
    reason = request.POST.get("reason", "Permanent ban").strip()
    profile = get_teacher_profile(user)
    if profile:
        profile.is_suspended = True
        profile.suspension_reason = f"PERMANENT BAN: {reason}"
        profile.suspended_at = timezone.now()
        profile.save()
    user.is_active = False
    user.save()
    messages.success(request, f"User {user.username} permanently banned.")
    return redirect("core:manage_users")


# ============================================
# PASSWORD RESET
# ============================================


@never_cache
@rate_limited("password_reset_request", limit=5, window_seconds=600)
def request_password_reset(request):
    if request.user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        if not username:
            messages.error(request, "Please enter your username.")
            return render(request, "request_reset.html", {"error": "Username required"})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Don't reveal whether the username exists - respond identically
            # either way to avoid username enumeration.
            messages.success(request, "If that account exists, a reset request has been submitted.")
            return redirect("/login/")

        if PasswordReset.objects.filter(user=user, status="pending").exists():
            messages.warning(request, "You already have a pending reset request.")
            return render(
                request, "request_reset.html", {"warning": "Pending request exists"}
            )

        reset = PasswordReset.objects.create(user=user, status="pending")
        admins = User.objects.filter(is_superuser=True)
        if admins.exists():
            notification = Notification.objects.create(
                title=f"Password Reset Request: {user.username}",
                message=(
                    f"Teacher: {user.get_full_name() or user.username}\n"
                    f"Username: {user.username}\n"
                    f'Requested at: {reset.requested_at.strftime("%Y-%m-%d %H:%M")}'
                ),
                notification_type="warning",
            )
            notification.target_users.set(admins)

        messages.success(request, "Reset request submitted! Admin will review it.")
        return redirect("/login/")

    return render(request, "request_reset.html")


@login_required
@user_passes_test(admin_required)
def admin_reset_requests(request):
    pending_resets = (
        PasswordReset.objects.filter(status="pending")
        .select_related("user")
        .order_by("-requested_at")
    )
    context = {
        "pending_resets": pending_resets,
        **_get_notification_context(request),
    }
    return render(request, "admin_reset_requests.html", context)


@login_required
@user_passes_test(admin_required)
@require_POST
def approve_reset(request, reset_id):
    """
    Approve a pending password reset: generate a new random password and
    hand it to the user via an in-app notification.

    NOTE (SECURITY ISSUE 5): delivering a plaintext password through the
    in-app notification system means anyone who can read that user's
    notifications also learns their new password. This is preserved as the
    existing behavior (no email backend is assumed to be configured) but is
    flagged here - the safer long-term fix is a single-use, time-limited
    reset link emailed directly to the user instead.

    FIX (CRITICAL ERROR 2): the function body here had been overwritten with
    code that belonged to a completely different view (the client-side
    error-reporting endpoint below), which meant approving a reset never
    actually generated or delivered a new password at all.
    """
    reset = get_object_or_404(PasswordReset, id=reset_id, status="pending")
    user = reset.user

    new_password = get_random_string(
        length=12, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789"
    )
    user.set_password(new_password)
    user.save()

    reset.status = "approved"
    reset.approved_at = timezone.now()
    reset.approved_by = request.user
    reset.save()

    notification = Notification.objects.create(
        title="Password Reset Approved",
        message=(
            f"Your password has been reset by an administrator.\n"
            f"Your new temporary password is: {new_password}\n"
            "Please log in and change it immediately from your profile settings."
        ),
        notification_type="warning",
    )
    notification.target_users.add(user)

    messages.success(
        request, f"Password reset for {user.username} approved and delivered via notification."
    )
    return redirect("core:admin_reset_requests")


@login_required
@user_passes_test(admin_required)
@require_POST
def deny_reset(request, reset_id):
    """Deny a pending password-reset request."""
    reset = get_object_or_404(PasswordReset, id=reset_id, status="pending")
    reset.status = "denied"
    reset.approved_by = request.user
    reset.approved_at = timezone.now()
    reset.save()
    messages.success(request, f"Reset request for {reset.user.username} denied.")
    return redirect("core:admin_reset_requests")


@login_required
def report_error(request):
    """
    Client-side error reporting endpoint: logs JS/frontend errors reported by
    the browser to the server log (rather than stdout) so they are captured
    by whatever logging backend is configured in production (Sentry, file
    handler, etc).

    FIX: this function's body had been merged into approve_reset() above due
    to a corrupted/overlapping edit; split back out into its own view.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logger.error(
                "Client error report | user=%s | url=%s | time=%s\n%s",
                request.user.username,
                data.get("url", "Unknown"),
                timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get("error", "No details provided"),
            )
            return JsonResponse({"status": "success", "message": "Error reported."})
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse(
        {"status": "error", "message": "Method not allowed."}, status=405
    )


# ============================================
# EXPORT FUNCTIONS - ADMIN
# ============================================


@login_required
@user_passes_test(admin_required)
def export_summary_report(request):
    """Export a school-wide summary report (CSV) with headline statistics,
    a stream breakdown, a form breakdown, and the ten most recent reports."""
    try:
        total_students_list = Student.objects.filter(is_active=True).count()
        total_reports = DisciplineReport.objects.count()
        critical = Student.objects.filter(is_active=True, risk_level="CRITICAL").count()
        warning = Student.objects.filter(is_active=True, risk_level="WARNING").count()
        good = Student.objects.filter(is_active=True, risk_level="GOOD").count()
        avg_risk = (
            Student.objects.filter(is_active=True).aggregate(avg=Avg("risk_score"))[
                "avg"
            ]
            or 0
        )

        stream_data = []
        for stream in Stream.objects.filter(is_active=True):
            count = Student.objects.filter(stream=stream, is_active=True).count()
            if count > 0:
                stream_data.append([stream.name, count])

        form_data = []
        for form_name, _label in _get_form_choices():
            count = Student.objects.filter(form=form_name, is_active=True).count()
            if count > 0:
                form_data.append([form_name, count])

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="school_summary_{datetime.now().strftime("%Y%m%d")}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["SCHOOL DISCIPLINE SUMMARY REPORT"])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
        writer.writerow([])
        writer.writerow(["STATISTICS"])
        writer.writerow(["Total Students", total_students])
        writer.writerow(["Total Reports", total_reports])
        writer.writerow(["Critical Cases", critical])
        writer.writerow(["Warning Cases", warning])
        writer.writerow(["Good Status", good])
        writer.writerow(["Average Risk", f"{round(avg_risk, 1)}%"])
        writer.writerow([])

        if stream_data:
            writer.writerow(["STREAM BREAKDOWN"])
            writer.writerow(["Stream", "Students"])
            writer.writerows(stream_data)
            writer.writerow([])

        if form_data:
            writer.writerow(["FORM BREAKDOWN"])
            writer.writerow(["Form", "Students"])
            writer.writerows(form_data)
            writer.writerow([])

        recent_reports = DisciplineReport.objects.select_related(
            "student", "category"
        ).order_by("-reported_at")[:10]
        writer.writerow(["RECENT REPORTS (Last 10)"])
        writer.writerow(["Date", "Student", "Category", "Rating", "Points"])
        for report in recent_reports:
            writer.writerow(
                [
                    report.reported_at.strftime("%Y-%m-%d %H:%M"),
                    report.student.name,
                    report.category_name,
                    get_rating_display(report),
                    report.points,
                ]
            )

        return response
    except Exception as e:  # noqa: BLE001 - export must never 500 without a message
        logger.exception("export_summary_report failed")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@user_passes_test(admin_required)
def export_pdf_report(request):
    """Export a printable HTML-based report (served with a PDF content-type
    for direct download; browsers will offer to save/print it as a PDF)."""
    try:
        students_list = Student.objects.filter(is_active=True)
        total_students = students_list.count()
        total_reports = DisciplineReport.objects.count()
        critical = students_list.filter(risk_level="CRITICAL").count()
        warning = students_list.filter(risk_level="WARNING").count()
        good = students_list.filter(risk_level="GOOD").count()
        avg_risk = students_list.aggregate(avg=Avg("risk_score"))["avg"] or 0

        recent_reports = DisciplineReport.objects.select_related(
            "student", "category", "reported_by"
        ).order_by("-reported_at")[:20]

        rows_html = "".join(f"""<tr>
                <td>{report.reported_at.strftime('%Y-%m-%d %H:%M')}</td>
                <td>{report.student.name}</td>
                <td>{report.category_name}</td>
                <td>{get_rating_display(report)}</td>
                <td>{report.reported_by.username}</td>
            </tr>""" for report in recent_reports)

        critical_pct = (
            round(critical / total_students * 100, 1) if total_students > 0 else 0
        )
        warning_pct = (
            round(warning / total_students * 100, 1) if total_students > 0 else 0
        )
        good_pct = round(good / total_students * 100, 1) if total_students > 0 else 0

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>School Discipline Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                h1 {{ color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
                h2 {{ color: #0f172a; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f1f5f9; padding: 10px; text-align: left; border: 1px solid #e2e8f0; }}
                td {{ padding: 8px 10px; border: 1px solid #e2e8f0; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
                .stat-box {{ background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #0f172a; }}
                .stat-label {{ color: #64748b; font-size: 12px; }}
                .footer {{ margin-top: 50px; text-align: center; color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>School Discipline Report</h1>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

            <h2>Statistics</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-number">{total_students}</div>
                    <div class="stat-label">Total Students</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{total_reports}</div>
                    <div class="stat-label">Total Reports</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{critical}</div>
                    <div class="stat-label">Critical Cases</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{round(avg_risk, 1)}%</div>
                    <div class="stat-label">Average Risk</div>
                </div>
            </div>

            <h2>Risk Distribution</h2>
            <table>
                <tr><th>Level</th><th>Count</th><th>Percentage</th></tr>
                <tr><td>Critical</td><td>{critical}</td><td>{critical_pct}%</td></tr>
                <tr><td>Warning</td><td>{warning}</td><td>{warning_pct}%</td></tr>
                <tr><td>Good</td><td>{good}</td><td>{good_pct}%</td></tr>
            </table>

            <h2>Recent Reports</h2>
            <table>
                <tr><th>Date</th><th>Student</th><th>Category</th><th>Rating</th><th>Reported By</th></tr>
                {rows_html}
            </table>
            <div class="footer">
                Disciplinary Management System v3.0<br>
                Powered by Pollination AI &bull; Kenyan Education Act 2013 Compliant
            </div>
        </body>
        </html>
        """

        response = HttpResponse(html_content, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="school_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
        )
        return response
    except Exception as e:  # noqa: BLE001
        logger.exception("export_pdf_report failed")
        return JsonResponse({"error": str(e)}, status=500)


# ============================================
# CLASS TEACHER EXPORT FUNCTIONS
# ============================================


@login_required
@user_passes_test(class_teacher_required)
def export_class_reports(request):
    """Export a CSV roster (with risk stats) for the class teacher's entire class."""
    try:
        profile = get_teacher_profile(request.user)

        if (
            not profile
            or not profile.has_chosen_stream
            or not profile.assigned_stream_id
        ):
            messages.error(request, "You are not assigned to a class.")
            return redirect("/class-teacher-dashboard/")

        assigned_stream = profile.assigned_stream
        assigned_form = profile.assigned_form

        students = (
            _class_teacher_scope(profile).select_related("stream").order_by("name")
        )

        if not students_list.exists():
            messages.warning(request, "No students found in your class.")
            return redirect("/class-teacher-dashboard/")

        response = HttpResponse(content_type="text/csv")
        filename = f"{assigned_stream.name}_{assigned_form}_class_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([f"CLASS REPORT - {assigned_stream.name} - {assigned_form}"])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
        writer.writerow([f"Total Students: {students_list.count()}"])
        writer.writerow([])
        writer.writerow(
            [
                "Admission",
                "Name",
                "Stream",
                "Form",
                "Risk Score",
                "Risk Level",
                "Total Reports",
                "Interventions",
                "Days Since Last Incident",
            ]
        )

        for student in students:
            writer.writerow(
                [
                    student.admission_number,
                    student.name,
                    student.stream.name if student.stream else "N/A",
                    student.form,
                    student.risk_score,
                    student.risk_level,
                    student.reports.count(),
                    student.intervention_count,
                    student.days_since_last_incident or "N/A",
                ]
            )

        return response
    except Exception as e:  # noqa: BLE001
        logger.exception("export_class_reports failed")
        messages.error(request, f"Error exporting class report: {e}")
        return redirect("/class-teacher-dashboard/")


@login_required
@user_passes_test(class_teacher_required)
def export_class_student_reports(request, student_id):
    """Export a CSV report history for a specific student in the class teacher's class."""
    try:
        profile = get_teacher_profile(request.user)

        if (
            not profile
            or not profile.has_chosen_stream
            or not profile.assigned_stream_id
        ):
            messages.error(request, "You are not assigned to a class.")
            return redirect("/class-teacher-dashboard/")

        student = get_object_or_404(Student, id=student_id, is_active=True)

        # Scoping check - only allow if student is in the teacher's class.
        if (
            student.stream_id != profile.assigned_stream_id
            or student.form != profile.assigned_form
        ):
            messages.error(request, "This student is not in your class.")
            return redirect("/class-teacher-dashboard/")

        reports = student.reports.select_related("category", "reported_by").order_by(
            "-reported_at"
        )

        response = HttpResponse(content_type="text/csv")
        filename = (
            f"{student.name}_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([f"STUDENT REPORT - {student.name}"])
        writer.writerow([f"Admission: {student.admission_number}"])
        writer.writerow([f'Stream: {student.stream.name if student.stream else "N/A"}'])
        writer.writerow([f"Form: {student.form}"])
        writer.writerow([f"Risk Score: {student.risk_score}%"])
        writer.writerow([f"Risk Level: {student.risk_level}"])
        writer.writerow([f"Total Reports: {reports.count()}"])
        writer.writerow([f"Interventions: {student.intervention_count}"])
        writer.writerow(
            [f'Days Since Last Incident: {student.days_since_last_incident or "N/A"}']
        )
        writer.writerow([])
        writer.writerow(["DISCIPLINE REPORTS"])
        writer.writerow(
            ["Date", "Category", "Rating", "Points", "Reported By", "Comments"]
        )

        for report in reports:
            writer.writerow(
                [
                    report.reported_at.strftime("%Y-%m-%d %H:%M"),
                    report.category_name,
                    get_rating_display(report),
                    report.points,
                    report.reported_by.username,
                    report.comments,
                ]
            )

        return response
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect("/class-teacher-dashboard/")
    except Exception as e:  # noqa: BLE001
        logger.exception("export_class_student_reports failed")
        messages.error(request, f"Error exporting report: {e}")
        return redirect("/class-teacher-dashboard/")


# ============================================
# DEBUG / TEST VIEWS (admin-only, dev helpers)
# ============================================


@login_required
@user_passes_test(admin_required)
def debug_streams(request):
    """Returns a JSON snapshot of streams, grades, and school - useful for debugging."""
    return JsonResponse(
        {
            "school": School.objects.values("id", "name").first(),
            "streams": list(Stream.objects.values("id", "name", "is_active")),
            "grades": list(GradeLevel.objects.values("id", "name", "is_active")),
            "total_streams": Stream.objects.count(),
            "total_grades": GradeLevel.objects.count(),
        }
    )


@login_required
def global_recommendations(request):
    """Get global AI recommendations for all students."""
    try:
        students_list = Student.objects.filter(is_active=True)
        total_students = students_list.count()

        if total_students == 0:
            return JsonResponse(
                {
                    "recommendations": [
                        {
                            "action": "No Students Found",
                            "details": "Add students to get AI recommendations.",
                            "priority": "LOW",
                            "steps": [
                                'Add students using the "Add Student" form',
                                "Or use bulk upload from School Setup",
                            ],
                        }
                    ],
                    "global_stats": {
                        "total_students": 0,
                        "critical_count": 0,
                        "warning_count": 0,
                        "good_count": 0,
                        "total_reports": 0,
                        "avg_risk": 0,
                    },
                }
            )

        critical_count = students_list.filter(risk_level="CRITICAL").count()
        warning_count = students_list.filter(risk_level="WARNING").count()
        good_count = students_list.filter(risk_level="GOOD").count()
        avg_risk = students_list.aggregate(avg=Avg("risk_score"))["avg"] or 0
        total_reports = DisciplineReport.objects.count()

        recommendations = []
        if critical_count > 0:
            student_names = ", ".join(
                s.name for s in students_list.filter(risk_level="CRITICAL")[:5]
            )
            recommendations.append(
                {
                    "action": f"{critical_count} Critical Risk Students Detected",
                    "details": f"Students: {student_names}. Immediate intervention needed.",
                    "priority": "HIGH",
                    "steps": [
                        "Schedule parent-teacher meetings immediately",
                        "Assign school counselor for assessment",
                        "Implement behavior modification plan",
                        "Track intervention progress weekly",
                        "Document all interventions",
                    ],
                }
            )

        if warning_count > 0:
            warning_names = ", ".join(
                s.name for s in students_list.filter(risk_level="WARNING")[:3]
            )
            recommendations.append(
                {
                    "action": f"{warning_count} Students at Warning Level",
                    "details": f"Students: {warning_names}. Monitor closely to prevent escalation.",
                    "priority": "MEDIUM",
                    "steps": [
                        "Increase monitoring and teacher attention",
                        "Contact parents for awareness",
                        "Document all incidents",
                        "Create individual improvement plans",
                        "Review progress weekly",
                    ],
                }
            )

        if good_count == total_students and total_students > 0:
            recommendations.append(
                {
                    "action": "All Students Doing Well",
                    "details": f"All {total_students} students have good risk levels.",
                    "priority": "LOW",
                    "steps": [
                        "Continue positive reinforcement",
                        "Maintain regular monitoring",
                        "Celebrate student achievements",
                        "Document successful strategies",
                    ],
                }
            )

        no_intervention = students_list.filter(intervention_count=0).count()
        if no_intervention > 0 and (critical_count > 0 or warning_count > 0):
            recommendations.append(
                {
                    "action": f"{no_intervention} Students Without Interventions",
                    "details": "These students need intervention plans.",
                    "priority": "MEDIUM" if critical_count > 0 else "LOW",
                    "steps": [
                        "Schedule individual student meetings",
                        "Create intervention plans",
                        "Assign mentors or counselors",
                        "Document all interventions",
                        "Track progress weekly",
                    ],
                }
            )

        if not recommendations:
            recommendations.append(
                {
                    "action": "School Status: Stable",
                    "details": f"{total_students} students with average risk of {round(avg_risk, 1)}%.",
                    "priority": "LOW",
                    "steps": [
                        "Continue current positive practices",
                        "Maintain monitoring systems",
                        "Document successful strategies",
                        "Share best practices with staff",
                    ],
                }
            )

        return JsonResponse(
            {
                "recommendations": recommendations,
                "global_stats": {
                    "total_students": total_students,
                    "critical_count": critical_count,
                    "warning_count": warning_count,
                    "good_count": good_count,
                    "total_reports": total_reports,
                    "avg_risk": round(avg_risk, 1),
                    "students_with_interventions": students_list.filter(intervention_count__gt=0).count(),
                },
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse(
            {
                "error": str(e),
                "recommendations": [
                    {
                        "action": "Error Loading Recommendations",
                        "details": f"Error: {str(e)}",
                        "priority": "HIGH",
                        "steps": [
                            "Check database connection",
                            "Verify student data exists",
                            "Contact system administrator",
                        ],
                    }
                ],
                "global_stats": {
                    "total_students": 0,
                    "critical_count": 0,
                    "warning_count": 0,
                    "good_count": 0,
                    "total_reports": 0,
                    "avg_risk": 0,
                },
            },
            status=500,
        )


@login_required
def test_ai(request):
    """Test AI recommendations endpoint."""
    return JsonResponse(
        {
            "status": "success",
            "message": "AI recommendations endpoint is working!",
            "timestamp": timezone.now().isoformat(),
        }
    )


@login_required
@user_passes_test(admin_required)
def assign_class_teacher(request):
    """
    Assign a class teacher to a specific (stream, form) pair.
    A (stream, form) pair can have only one approved class teacher at a time
    - assigning a new one automatically clears the previous holder, so two
    class teachers can never both claim the same class.
    """
    if request.method == "POST":
        teacher_id = request.POST.get("teacher_id")
        stream_id = request.POST.get("stream_id")
        form = request.POST.get("form")

        if not all([teacher_id, stream_id, form]):
            messages.error(request, "Please select a teacher, stream, and form.")
            return redirect("/manage-users/")

        try:
            teacher = User.objects.get(id=teacher_id)
            stream = Stream.objects.get(id=stream_id, is_active=True)

            existing = User.objects.filter(
                teacher_profile__assigned_stream=stream,
                teacher_profile__assigned_form=form,
                groups__name="ClassTeacher",
            ).exclude(id=teacher_id)

            if existing.exists():
                messages.warning(
                    request,
                    f"{stream.name} - {form} already has a class teacher. Reassigning will remove the previous teacher.",
                )
                for prev_teacher in existing:
                    prev_profile = get_teacher_profile(prev_teacher)
                    if prev_profile:
                        prev_profile.assigned_stream = None
                        prev_profile.assigned_form = None
                        prev_profile.has_chosen_stream = False
                        prev_profile.save()

            profile = get_teacher_profile(teacher)
            if not profile:
                profile = TeacherProfile.objects.create(user=teacher)
            profile.assigned_stream = stream
            profile.assigned_form = form
            profile.has_chosen_stream = True
            profile.is_approved = True
            profile.save()

            class_teacher_group, _ = Group.objects.get_or_create(name="ClassTeacher")
            if not teacher.groups.filter(name="ClassTeacher").exists():
                teacher.groups.add(class_teacher_group)

            messages.success(
                request,
                f"{teacher.get_full_name() or teacher.username} assigned to {stream.name} - {form}",
            )
        except User.DoesNotExist:
            messages.error(request, "Selected teacher not found.")
        except Stream.DoesNotExist:
            messages.error(request, "Selected stream not found.")
        except (ValueError, TypeError) as e:
            messages.error(request, f"Error assigning class teacher: {e}")

    return redirect("/manage-users/")


@login_required
def test_streams(request):
    """Renders test_streams.html with stream and grade data for template debugging."""
    context = {
        "streams": _get_active_streams(),
        "grades": GradeLevel.objects.filter(is_active=True).order_by("order", "name"),
        **_get_notification_context(request),
    }
    return render(request, "test_streams.html", context)


@login_required
def export_student_reports(request, student_id):
    """Export CSV reports for a specific student."""
    try:
        student = get_object_or_404(Student, id=student_id, is_active=True)

        # Same class-teacher scoping rule as viewing/editing the student.
        if (
            not request.user.is_superuser
            and request.user.groups.filter(name="ClassTeacher").exists()
        ):
            profile = get_teacher_profile(request.user)
            if not _class_teacher_scope(profile).filter(id=student.id).exists():
                return JsonResponse({"error": "Permission denied."}, status=403)

        reports = student.reports.select_related("reported_by", "category").order_by(
            "-reported_at"
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{student.name}_reports.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            ["Date", "Category", "Rating", "Points", "Reported By", "Comments"]
        )
        for report in reports:
            writer.writerow(
                [
                    report.reported_at.strftime("%Y-%m-%d %H:%M"),
                    report.category_name,
                    get_rating_display(report),
                    report.points,
                    report.reported_by.username,
                    report.comments,
                ]
            )
        return response
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@user_passes_test(admin_required)
def export_reports(request, format):
    """Export all reports school-wide in CSV or Excel format (admin only)."""
    if format not in ["csv", "excel"]:
        return JsonResponse({"error": "Invalid format"}, status=400)
    try:
        reports = DisciplineReport.objects.select_related(
            "student", "reported_by", "category"
        ).order_by("-reported_at")

        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="reports.csv"'
            writer = csv.writer(response)
            writer.writerow(
                [
                    "Date",
                    "Student",
                    "Admission",
                    "Category",
                    "Rating",
                    "Points",
                    "Reported By",
                    "Comments",
                ]
            )
            for report in reports:
                comments = (
                    report.comments[:100] + "..."
                    if len(report.comments) > 100
                    else report.comments
                )
                writer.writerow(
                    [
                        report.reported_at.strftime("%Y-%m-%d %H:%M"),
                        report.student.name,
                        report.student.admission_number,
                        report.category_name,
                        get_rating_display(report),
                        report.points,
                        report.reported_by.username,
                        comments,
                    ]
                )
            return response

        wb = Workbook()
        ws = wb.active
        ws.title = "Reports"
        ws.append(
            [
                "Date",
                "Student",
                "Admission",
                "Category",
                "Rating",
                "Points",
                "Reported By",
                "Comments",
            ]
        )
        for report in reports:
            comments = (
                report.comments[:100] + "..."
                if len(report.comments) > 100
                else report.comments
            )
            ws.append(
                [
                    report.reported_at.strftime("%Y-%m-%d %H:%M"),
                    report.student.name,
                    report.student.admission_number,
                    report.category_name,
                    get_rating_display(report),
                    report.points,
                    report.reported_by.username,
                    comments,
                ]
            )
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="reports.xlsx"'
        wb.save(response)
        return response
    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_categories_api(request):
    """Get all discipline categories."""
    try:
        categories = DisciplineCategory.objects.filter(is_active=True).values(
            "id", "name", "key", "default_rating", "risk_weight", "severity_level"
        )
        return JsonResponse({"status": "success", "categories": list(categories)})
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def get_streams_api(request):
    """Get all streams."""
    try:
        streams = Stream.objects.filter(is_active=True).values("id", "name", "code")
        return JsonResponse({"status": "success", "streams": list(streams)})
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def dashboard_stats_api(request):
    """Get dashboard statistics for API consumers."""
    try:
        students_list = Student.objects.filter(is_active=True)
        stats = {
            "total_students": students_list.count(),
            "critical_count": students_list.filter(risk_level="CRITICAL").count(),
            "warning_count": students_list.filter(risk_level="WARNING").count(),
            "good_count": students_list.filter(risk_level="GOOD").count(),
            "total_reports": DisciplineReport.objects.count(),
            "reports_today": DisciplineReport.objects.filter(
                reported_at__date=timezone.now().date()
            ).count(),
            "online_teachers": TeacherProfile.objects.filter(is_online=True).count(),
            "pending_approvals": TeacherProfile.objects.filter(
                is_approved=False, is_suspended=False
            ).count(),
            "pending_resets": PasswordReset.objects.filter(status="pending").count(),
        }
        return JsonResponse({"status": "success", "data": stats})
    except (ValueError, TypeError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user."""
    if request.method == "POST":
        notifications = request.user.notifications.filter(is_read=False)
        count = notifications.count()
        for notification in notifications:
            notification.mark_read(request.user)
        return JsonResponse(
            {
                "status": "success",
                "message": f"Marked {count} notifications as read",
                "count": count,
            }
        )
    return JsonResponse(
        {"status": "error", "message": "Method not allowed"}, status=405
    )


def student_by_admission(request, admission_number):
    """Get student by admission number."""
    try:
        student = get_object_or_404(
            Student, admission_number=admission_number, is_active=True
        )
        return JsonResponse(
            {
                "id": student.id,
                "name": student.name,
                "admission_number": student.admission_number,
                "stream": student.stream.name if student.stream else "N/A",
                "form": student.form,
                "risk_score": student.risk_score,
                "risk_level": student.risk_level,
                "total_reports": student.total_reports,
            }
        )
    except Http404:
        return JsonResponse({"error": "Student not found"}, status=404)


@login_required
@user_passes_test(admin_required)
def media_test(request):
    """Test if media files are accessible. Admin-only: lists filesystem paths."""
    media_path = settings.MEDIA_ROOT
    files = []
    if os.path.exists(media_path):
        for root, _dirs, filenames in os.walk(media_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))

    return JsonResponse(
        {
            "media_root": str(media_path),
            "exists": os.path.exists(media_path),
            "files": files[:20],
            "media_url": settings.MEDIA_URL,
            "debug": settings.DEBUG,
            "message": "Media serving is working!",
        }
    )
@login_required
def add_student(request):
    """Add a new student to the system."""
    # Check permissions
    if not request.user.is_superuser and not request.user.groups.filter(name__in=['Admin', 'Teacher']).exists():
        messages.error(request, "You don't have permission to add students.")
        return redirect('core:dashboard')

    # Get data for dropdowns
    school = School.objects.first()
    streams = Stream.objects.filter(school=school, is_active=True).order_by('name') if school else Stream.objects.filter(is_active=True).order_by('name')
    grade_levels = GradeLevel.objects.filter(is_active=True).order_by('order')
    forms = Student.FORM_CHOICES

    if request.method == 'POST':
        # Create student
        try:
            admission_number = request.POST.get('admission_number', '').strip()
            name = request.POST.get('name', '').strip()
            stream_id = request.POST.get('stream')
            grade_level_id = request.POST.get('grade_level')
            form = request.POST.get('form')
            year = request.POST.get('year', timezone.now().year)
            optional_notes = request.POST.get('optional_notes', '').strip()

            # Validate
            if not admission_number or not name:
                messages.error(request, "Admission number and name are required.")
                return render(request, 'add_student.html', {
                    'streams': streams,
                    'grade_levels': grade_levels,
                    'forms': forms,
                })

            # Get stream
            stream = Stream.objects.get(id=stream_id) if stream_id else None
            grade_level = GradeLevel.objects.get(id=grade_level_id) if grade_level_id else None

            # Create student
            student = Student.objects.create(
                admission_number=admission_number,
                name=name,
                stream=stream,
                grade_level=grade_level,
                form=form,
                year=year,
                optional_notes=optional_notes,
                created_by=request.user
            )

            messages.success(request, f"Student '{student.name}' added successfully!")
            return redirect('core:student_profile', student_id=student.id)

        except Exception as e:
            messages.error(request, f"Error adding student: {e}")
            return render(request, 'add_student.html', {
                'streams': streams,
                'grade_levels': grade_levels,
                'forms': forms,
            })

    # GET request - render the form with all dropdown data
    return render(request, 'add_student.html', {
        'streams': streams,
        'grade_levels': grade_levels,
        'forms': forms,
    })

# ============================================
# UPDATED: Password Reset Request with Redirect
# ============================================

@never_cache
@rate_limited("password_reset_request", limit=5, window_seconds=600)
# ============================================
# RESET SENT PAGE
# ============================================
def reset_sent(request):
    """Show pending approval page with auto-redirect."""
    return render(request, "reset_request_sent.html")

# ============================================
# UPDATED: Approve Reset with Auto-Redirect
# ============================================

@login_required
@user_passes_test(admin_required)
@require_POST
# ============================================
# RESET SENT PAGE
# ============================================
# ============================================
# RESET STATUS API (for auto-refresh)
# ============================================
@login_required
def reset_status_api(request):
    """Check if a password reset has been approved for the current user."""
    try:
        # Check for the most recent pending reset for the user
        reset = PasswordReset.objects.filter(
            user=request.user,
            status__in=['pending', 'approved']
        ).order_by('-requested_at').first()
        
        if reset:
            return JsonResponse({
                'status': reset.status,
                'reset_id': reset.id,
                'requested_at': reset.requested_at.isoformat(),
                'approved_at': reset.approved_at.isoformat() if reset.approved_at else None
            })
        return JsonResponse({'status': 'none'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
