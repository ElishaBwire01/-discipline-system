#!/usr/bin/env python
"""
optimize_database.py
Run database optimizations and performance checks
Run: python optimize_database.py
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from datetime import timedelta

from django.db import connection
from django.db.models import Count
from django.utils import timezone

from core.models import DisciplineReport, Notification, Student


def run_optimizations():
    """Run database optimizations"""

    print("="*60)
    print("  🔧 DATABASE OPTIMIZATIONS")
    print("="*60)
    print("")

    # 1. Check for missing indexes
    print("📌 Checking indexes...")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexname LIKE '%stream_risk%'
        """)
        indexes = cursor.fetchall()

        if not indexes:
            print("  ⚠️ Composite index 'stream_risk_idx' not found, creating...")
            cursor.execute("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS stream_risk_idx
                ON core_student (stream_id, risk_level);
            """)
            print("  ✅ Created composite index: stream_risk_idx")
        else:
            print(f"  ✅ Composite index exists: {indexes[0][1]}")

    # 2. Update risk scores
    print("")
    print("📌 Updating risk scores...")

    students = Student.objects.filter(is_active=True)
    updated = 0
    for student in students:
        student.update_risk_score()
        updated += 1

    print(f"  ✅ Updated risk scores for {updated} students")

    # 3. Check for students without reports
    print("")
    print("📌 Checking for students with no reports...")

    no_reports = Student.objects.filter(
        is_active=True,
        reports__isnull=True
    ).count()

    print(f"  ℹ️ {no_reports} students have no reports")

    # 4. Clean up old notifications
    print("")
    print("📌 Cleaning up old notifications...")

    thirty_days_ago = timezone.now() - timedelta(days=30)
    old_notifications = Notification.objects.filter(
        is_read=True,
        created_at__lt=thirty_days_ago
    )
    count = old_notifications.count()
    old_notifications.delete()

    print(f"  ✅ Deleted {count} old notifications")

    # 5. Summary
    print("")
    print("="*60)
    print("  ✅ OPTIMIZATION COMPLETE!")
    print("="*60)
    print("")

    total_students = Student.objects.filter(is_active=True).count()
    total_reports = DisciplineReport.objects.count()
    critical = Student.objects.filter(risk_level='CRITICAL').count()
    warning = Student.objects.filter(risk_level='WARNING').count()
    good = Student.objects.filter(risk_level='GOOD').count()

    print("📊 Statistics:")
    print(f"  Total Students: {total_students}")
    print(f"  Total Reports: {total_reports}")
    print(f"  Critical: {critical}")
    print(f"  Warning: {warning}")
    print(f"  Good: {good}")
    print("")
    print("="*60)


if __name__ == "__main__":
    run_optimizations()
