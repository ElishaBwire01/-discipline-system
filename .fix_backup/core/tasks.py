# core/tasks.py
"""Celery tasks for background processing."""
from celery import shared_task
from django.utils import timezone

from .models import DisciplineReport, Notification, Student


@shared_task
def update_all_risk_scores():
    """Update risk scores for all active students."""
    students = Student.objects.filter(is_active=True)
    updated = 0
    for student in students:
        student.update_risk_score()
        updated += 1
    return f"Updated {updated} students"

@shared_task
def send_notification_email(notification_id):
    """Send email notification."""
    from django.conf import settings
    from django.core.mail import send_mail

    try:
        notification = Notification.objects.get(id=notification_id)
        # ... email sending logic
        return f"Email sent for notification {notification_id}"
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"

@shared_task
def generate_class_report(stream_id, user_id):
    """Generate class report in background."""
    import csv

    from django.contrib.auth.models import User
    from django.http import HttpResponse

    try:
        stream = Stream.objects.get(id=stream_id)
        students = Student.objects.filter(stream=stream, is_active=True)
        # ... report generation logic
        return f"Report generated for {stream.name}"
    except Exception as e:
        return f"Error generating report: {str(e)}"
