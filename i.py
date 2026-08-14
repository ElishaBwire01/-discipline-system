#!/usr/bin/env python
# ============================================
# FINAL FIX FOR VIEWS.PY
# ============================================

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent if '__file__' in globals() else Path.cwd()
VIEWS_FILE = PROJECT_ROOT / 'core' / 'views.py'

def fix_views_final():
    """Fix all remaining issues in views.py."""
    
    print("=" * 80)
    print("🔧 FINAL VIEWS.PY FIX")
    print("=" * 80)
    
    if not VIEWS_FILE.exists():
        print(f"❌ File not found: {VIEWS_FILE}")
        return False
    
    with open(VIEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace "unknown_key" with proper keys
    replacements = [
        # In student_recommendations
        (r'"unknown_key": getattr\(student, os\.environ\.get\("SECRET_KEY", "days_since_last_incident"\), None\)',
         '"days_since_last_incident": getattr(student, "days_since_last_incident", None)'),
        
        # In class_recommendations
        (r'"unknown_key": with_interventions,',
         '"students_with_interventions": with_interventions,'),
        
        # In ai_trend_analysis - first occurrence
        (r'"unknown_key": {',
         '"current_distribution": {'),
        
        # In ai_trend_analysis - second occurrence
        (r'"unknown_key": DisciplineReport\.objects\.filter',
         '"total_reports_period": DisciplineReport.objects.filter'),
        
        # In ai_risk_stats
        (r'"students": students,',
         '"students_with_interventions": students.filter(intervention_count__gt=0).count(),'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Fix 2: Fix the broken _class_teacher_scope function
    content = re.sub(
        r'def _class_teacher_scope\(profile\):\s+"""[^"]*""" """[^"]*"""\s+if request\.user\.is_authenticated:.*?return redirect\("/login/"\)',
        'def _class_teacher_scope(profile):\n    """\n    The single source of truth for "which students does this class teacher see".\n\n    A class teacher is assigned to exactly one (stream, form) pair. They must\n    see ONLY students in that exact pair — not the whole stream, and not other\n    forms/grades in that stream (those belong to a different class teacher).\n\n    Returns a Student queryset, or Student.objects.none() if the teacher has\n    not been fully set up yet.\n    """\n    if not profile or not profile.has_chosen_stream or not profile.assigned_stream_id or not profile.assigned_form:\n        return Student.objects.none()\n    return Student.objects.filter(\n        is_active=True,\n        stream_id=profile.assigned_stream_id,\n        form=profile.assigned_form,\n    )',
        content,
        flags=re.DOTALL
    )
    
    # Fix 3: Fix approve_reset docstring
    content = content.replace(
        '""" """Accepts client-side error reports',
        '"""\n\n    # Approve the reset\n    if request.method == "POST":\n        reset = get_object_or_404(PasswordReset, id=reset_id)'
    )
    
    # Fix 4: Fix dashboard_redirect docstring
    content = content.replace(
        '""" """\n    Subject/general teacher dashboard',
        '"""\n\n    if request.user.is_superuser:\n        return redirect("admin_dashboard")\n    elif request.user.groups.filter(name="ClassTeacher").exists():\n        return redirect("class_teacher_dashboard")\n    else:\n        return redirect("teacher_dashboard")\n\n\n@login_required\ndef teacher_dashboard(request):\n    """Subject/general teacher dashboard'
    )
    
    # Fix 5: Add cache import if missing
    if 'from django.core.cache import cache' not in content:
        content = content.replace(
            'from django.core.cache import cache',
            'from django.core.cache import cache'
        )
    
    # Write the fixed content
    with open(VIEWS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ views.py fixed successfully!")
    return True

if __name__ == '__main__':
    fix_views_final()
