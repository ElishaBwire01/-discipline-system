  # core/context_processors.py

from django.contrib.auth.models import User
from .models import (
    TeacherProfile,
    PasswordReset,
    Notification,
    Student,
    DisciplineReport,
    School,
    Stream,
    DisciplineCategory,
)
from django.db.models import Count
from django.utils import timezone


def user_management_context(request):
    """
    Add all notification counts and school info to templates.
    This context processor runs for every request and makes these variables
    available in all templates.
    """

    # Get school info
    school = School.objects.first()
    school_name = school.name if school else "Disciplinary System"
    school_motto = (
        school.motto if school and school.motto else "Excellence Through Discipline"
    )
    school_short_name = school.short_name if school else "DMS"

    # Get active streams
    streams = Stream.objects.filter(is_active=True).order_by("name")

    # Get active categories
    categories = DisciplineCategory.objects.filter(is_active=True).order_by(
        "order", "name"
    )

    # ? Initialize context with safe defaults
    context = {
        # School info
        "school_name": school_name,
        "school_motto": school_motto,
        "school_short_name": school_short_name,
        "school": school,
        # Dropdown options
        "streams": streams,
        "forms": ["Form 1", "Form 2", "Form 3", "Form 4"],
        "categories": categories,
        # Notification defaults
        "notification_count": 0,
        "unread_notifications": [],
        "admin_notification_count": 0,
        # Admin stats defaults
        "pending_approvals": 0,
        "pending_resets": 0,
        "critical_students": 0,
        "reports_today": 0,
        # Additional useful context
        "current_year": timezone.now().year,
        "current_date": timezone.now(),
    }

    # ? Check if request has user attribute
    if hasattr(request, "user") and request.user.is_authenticated:

        # --- USER NOTIFICATIONS ---
        try:
            notifications = request.user.notifications.filter(is_read=False)
            context["notification_count"] = notifications.count()
            context["unread_notifications"] = notifications[:15]
        except Exception:
            pass

        # --- ADMIN SPECIFIC CONTEXT ---
        if request.user.is_superuser:
            try:
                # Count pending approvals (exclude current admin)
                pending_approvals = (
                    User.objects.filter(
                        teacher_profile__is_approved=False,
                        teacher_profile__is_suspended=False,
                        groups__name="ClassTeacher",
                    )
                    .exclude(id=request.user.id)
                    .count()
                )
                context["pending_approvals"] = pending_approvals

                # Count pending password resets
                pending_resets = PasswordReset.objects.filter(status="pending").count()
                context["pending_resets"] = pending_resets

                # Count critical students (risk_score >= 60)
                critical_students = Student.objects.filter(
                    is_active=True, risk_score__gte=60
                ).count()
                context["critical_students"] = critical_students

                # Count today's reports
                reports_today = DisciplineReport.objects.filter(
                    reported_at__date=timezone.now().date()
                ).count()
                context["reports_today"] = reports_today

                # Count total students
                total_students = Student.objects.filter(is_active=True).count()
                context["total_students"] = total_students

                # Count total reports
                total_reports = DisciplineReport.objects.count()
                context["total_reports"] = total_reports

                # Total admin notifications count
                context["admin_notification_count"] = (
                    pending_approvals + pending_resets + critical_students
                )

            except Exception:
                # Silently handle errors to avoid breaking the site
                pass

        # --- CLASS TEACHER SPECIFIC CONTEXT ---
        elif request.user.groups.filter(name="ClassTeacher").exists():
            try:
                # Get teacher profile
                profile = TeacherProfile.objects.filter(user=request.user).first()
                if profile and profile.assigned_stream:
                    # Count students in assigned stream
                    stream_students = Student.objects.filter(
                        is_active=True, stream=profile.assigned_stream
                    )
                    context["class_students_count"] = stream_students.count()

                    # Count critical students in class
                    context["class_critical_count"] = stream_students.filter(
                        risk_score__gte=60
                    ).count()

                    # Count warning students in class
                    context["class_warning_count"] = stream_students.filter(
                        risk_score__range=(30, 59)
                    ).count()

                    # Count good students in class
                    context["class_good_count"] = stream_students.filter(
                        risk_score__lt=30
                    ).count()

                    # Add assigned stream to context
                    context["assigned_stream"] = profile.assigned_stream
                    context["assigned_form"] = profile.assigned_form

            except Exception:
                pass

    return context
