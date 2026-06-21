from django.contrib.auth.models import User
from .models import TeacherProfile, PasswordReset, Notification, Student, DisciplineReport
from django.db.models import Count
from django.utils import timezone

def user_management_context(request):
    """Add all notification counts to templates"""
    context = {
        'notification_count': 0,
        'unread_notifications': [],
        'pending_approvals': 0,
        'pending_resets': 0,
        'admin_notification_count': 0,
        'critical_students': 0,
        'reports_today': 0,
    }
    
    if request.user.is_authenticated:
        # User notifications
        notifications = request.user.notifications.filter(is_read=False)
        context['notification_count'] = notifications.count()
        context['unread_notifications'] = notifications[:15]
        
        # Admin specific - but exclude self from pending approvals
        if request.user.is_superuser:
            try:
                # Count pending approvals - exclude the current admin
                pending_approvals = User.objects.filter(
                    teacher_profile__is_approved=False,
                    teacher_profile__is_suspended=False,
                    groups__name='ClassTeacher'
                ).exclude(id=request.user.id).count()  # Exclude current user
                context['pending_approvals'] = pending_approvals
                
                # Count pending resets
                pending_resets = PasswordReset.objects.filter(status='pending').count()
                context['pending_resets'] = pending_resets
                
                # Count critical students
                critical_students = Student.objects.filter(
                    is_active=True,
                    risk_score__gte=60
                ).count()
                context['critical_students'] = critical_students
                
                # Count today's reports
                reports_today = DisciplineReport.objects.filter(
                    reported_at__date=timezone.now().date()
                ).count()
                context['reports_today'] = reports_today
                
                # Total admin notifications
                context['admin_notification_count'] = pending_approvals + pending_resets + critical_students
                
            except Exception as e:
                pass
    
    return context
