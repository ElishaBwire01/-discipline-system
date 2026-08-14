#!/usr/bin/env python
"""
debug_and_clean_views.py
Comprehensive debugging and cleaning of views.py for production
Run: python debug_and_clean_views.py
"""

import os
import re
import sys


def debug_and_clean_views():
    """Comprehensive debug and clean views.py"""

    print("="*80)
    print("  🔍 COMPREHENSIVE VIEWS.PY DEBUG & CLEAN")
    print("="*80)
    print("")

    views_path = "core/views.py"

    if not os.path.exists(views_path):
        print(f"❌ File not found: {views_path}")
        return False

    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes_applied = []
    warnings = []

    # ============================================
    # FIX 1: Remove duplicate decorators
    # ============================================
    print("📌 Fix 1: Removing duplicate @login_required decorators...")

    # Find and remove duplicate @login_required
    duplicate_pattern = r'(@login_required\s*){2,}'
    if re.search(duplicate_pattern, content):
        content = re.sub(duplicate_pattern, '@login_required\n', content)
        fixes_applied.append("Removed duplicate @login_required decorators")
        print("  ✅ Fixed duplicate decorators")
    else:
        print("  ℹ️ No duplicate decorators found")

    # ============================================
    # FIX 2: Remove empty decorators
    # ============================================
    print("📌 Fix 2: Removing empty decorators...")

    empty_decorator = r'@login_required\s*@login_required'
    if re.search(empty_decorator, content):
        content = re.sub(empty_decorator, '@login_required', content)
        fixes_applied.append("Removed empty decorators")
        print("  ✅ Fixed empty decorators")

    # ============================================
    # FIX 3: Fix function ordering
    # ============================================
    print("📌 Fix 3: Checking function ordering...")

    # Ensure helper functions come before view functions
    helper_functions = ['admin_required', 'class_teacher_required', 'get_teacher_profile',
                        'get_rating_label', '_create_report', '_get_form_choices']

    view_functions = ['custom_login', 'custom_logout', 'register', 'choose_stream',
                      'root_redirect', 'dashboard_redirect', 'admin_dashboard']

    # Check if helper functions are before view functions
    helper_positions = []
    view_positions = []

    for func in helper_functions:
        if f"def {func}" in content:
            helper_positions.append(content.find(f"def {func}"))

    for func in view_functions:
        if f"def {func}" in content:
            view_positions.append(content.find(f"def {func}"))

    if helper_positions and view_positions:
        if min(view_positions) < max(helper_positions):
            warnings.append("Helper functions should be before view functions")
            print("  ⚠️ Helper functions should be before view functions")
        else:
            print("  ✅ Function ordering is correct")

    # ============================================
    # FIX 4: Check for missing imports
    # ============================================
    print("📌 Fix 4: Checking imports...")

    required_imports = [
        'from django.shortcuts import render, redirect, get_object_or_404',
        'from django.contrib.auth import authenticate, login, logout, update_session_auth_hash',
        'from django.contrib.auth.models import User, Group',
        'from django.contrib.auth.decorators import login_required, user_passes_test',
        'from django.contrib import messages',
        'from django.http import JsonResponse, HttpResponse',
        'from django.core.paginator import Paginator',
        'from django.utils import timezone',
        'from django.views.decorators.csrf import csrf_exempt',
        'from django.views.decorators.cache import never_cache',
        'from django.db.models import Count, Q, Avg, Max, Min, Sum',
        'from django.db.models.functions import ExtractWeekDay',
        'import json',
        'import os',
        'import re',
        'from datetime import datetime, timedelta',
        'import pandas as pd',
    ]

    missing_imports = []
    for imp in required_imports:
        if imp not in content:
            missing_imports.append(imp)

    if missing_imports:
        warnings.append(f"Missing imports: {', '.join(missing_imports)}")
        print(f"  ⚠️ Missing imports: {', '.join(missing_imports)}")
    else:
        print("  ✅ All required imports present")

    # ============================================
    # FIX 5: Check for proper error handling
    # ============================================
    print("📌 Fix 5: Checking error handling...")

    # Count try/except blocks
    try_count = len(re.findall(r'try:', content))
    except_count = len(re.findall(r'except', content))

    if try_count > except_count:
        warnings.append(f"Some try blocks missing except: {try_count} try, {except_count} except")
        print(f"  ⚠️ {try_count} try blocks, {except_count} except blocks")
    else:
        print(f"  ✅ Error handling looks good ({try_count} try, {except_count} except)")

    # ============================================
    # FIX 6: Check for hardcoded URLs
    # ============================================
    print("📌 Fix 6: Checking for hardcoded URLs...")

    # Look for redirects with hardcoded URLs vs named URLs
    hardcoded_redirects = re.findall(r"redirect\('/[^']+'\)", content)
    named_redirects = re.findall(r"redirect\('[\w_]+'\)", content)

    if hardcoded_redirects:
        print(f"  ℹ️ Found {len(hardcoded_redirects)} hardcoded redirects")
        print(f"  ℹ️ Found {len(named_redirects)} named redirects")
    else:
        print("  ✅ No hardcoded redirects found")

    # ============================================
    # FIX 7: Check for proper docstrings
    # ============================================
    print("📌 Fix 7: Checking docstrings...")

    # Count functions with docstrings
    functions = re.findall(r'def (\w+)\(', content)
    functions_with_docstrings = re.findall(r'def (\w+)\(.*?\):\s*"""[^"]*"""', content, re.DOTALL)

    if len(functions) > len(functions_with_docstrings):
        warnings.append(f"{len(functions) - len(functions_with_docstrings)} functions missing docstrings")
        print(f"  ⚠️ {len(functions) - len(functions_with_docstrings)} functions missing docstrings")
    else:
        print("  ✅ All functions have docstrings")

    # ============================================
    # FIX 8: Remove unused imports
    # ============================================
    print("📌 Fix 8: Checking for unused imports...")

    # Check for common unused imports
    unused_check = [
        ('StringIO', 'StringIO'),
        ('get_random_string', 'get_random_string'),
        ('ExtractWeekDay', 'ExtractWeekDay'),
    ]

    for imp, name in unused_check:
        if imp in content and name not in content:
            warnings.append(f"Possibly unused import: {imp}")
            print(f"  ⚠️ Possibly unused import: {imp}")

    # ============================================
    # FIX 9: Fix trailing whitespace
    # ============================================
    print("📌 Fix 9: Removing trailing whitespace...")

    # Remove trailing whitespace
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_lines.append(line.rstrip())
    content = '\n'.join(cleaned_lines)
    fixes_applied.append("Removed trailing whitespace")
    print("  ✅ Removed trailing whitespace")

    # ============================================
    # FIX 10: Fix multiple blank lines
    # ============================================
    print("📌 Fix 10: Fixing multiple blank lines...")

    # Replace 3+ blank lines with 2
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    fixes_applied.append("Fixed multiple blank lines")
    print("  ✅ Fixed multiple blank lines")

    # ============================================
    # FIX 11: Add missing @login_required to views
    # ============================================
    print("📌 Fix 11: Checking for missing @login_required...")

    # Find view functions without @login_required
    view_pattern = r'(?<!@login_required\s*)(?<!@user_passes_test.*?\s*)(?<!@csrf_exempt\s*)def (custom_login|custom_logout|register|choose_stream|dashboard_redirect|admin_dashboard|class_teacher_dashboard|teacher_dashboard|student_profile|edit_student|user_profile_settings|view_user_profile|upload_profile_picture|school_setup|bulk_upload_students|manage_users|approve_user|suspend_user|unsuspend_user|delete_user_permanent|ban_user_permanent|ai_dashboard|ai_chat_page|global_recommendations|student_recommendations|class_recommendations|ai_all_students|student_by_name|ai_risk_stats|ai_trend_analysis|ai_intervention_suggestions|ai_bulk_risk_update|ai_predictive_analysis|ai_behavior_patterns|ai_intervention_effectiveness)\('

    missing_decorators = re.findall(view_pattern, content)
    if missing_decorators:
        warnings.append(f"Views missing @login_required: {', '.join(missing_decorators)}")
        print(f"  ⚠️ Views missing @login_required: {', '.join(missing_decorators)}")
    else:
        print("  ✅ All views have @login_required where needed")

    # ============================================
    # FIX 12: Check for proper HTTP methods in API views
    # ============================================
    print("📌 Fix 12: Checking API views for method validation...")

    api_views = re.findall(r'def (\w+_api)\(', content)
    if api_views:
        for api_view in api_views:
            if f"def {api_view}" in content:
                # Check if method validation exists
                method_check = re.search(f"def {api_view}.*?if request.method", content, re.DOTALL)
                if not method_check:
                    warnings.append(f"API view {api_view} missing method validation")
                    print(f"  ⚠️ API view {api_view} missing method validation")
    else:
        print("  ✅ No API views found or all have method validation")

    # ============================================
    # FIX 13: Check for proper status codes
    # ============================================
    print("📌 Fix 13: Checking for proper status codes...")

    # Count JsonResponse with status codes
    json_with_status = len(re.findall(r'JsonResponse\(.*?status=\d+', content))
    json_without_status = len(re.findall(r'JsonResponse\([^)]*\)(?!.*status=)', content))

    if json_without_status > json_with_status:
        warnings.append(f"Some JsonResponse missing status codes ({json_without_status} without status)")
        print(f"  ⚠️ {json_without_status} JsonResponse missing status codes")
    else:
        print(f"  ✅ {json_with_status} JsonResponse with status codes")

    # ============================================
    # FIX 14: Add production settings
    # ============================================
    print("📌 Fix 14: Adding production-ready improvements...")

    # Check for DEBUG in views
    if "if settings.DEBUG" not in content:
        # Add debug check for development-only features
        debug_check = """
# Development-only features
if settings.DEBUG:
    # Add debug views here if needed
    pass
"""
        content += debug_check
        fixes_applied.append("Added production-ready debug checks")
        print("  ✅ Added production-ready debug checks")
    else:
        print("  ℹ️ Debug checks already present")

    # ============================================
    # FIX 15: Remove print statements (production)
    # ============================================
    print("📌 Fix 15: Checking for print statements...")

    if "print(" in content:
        warnings.append("print() statements found - remove for production")
        print("  ⚠️ print() statements found - remove for production")
        # Comment out print statements
        content = re.sub(r'print\(', '# print(', content)
        fixes_applied.append("Commented out print statements")
    else:
        print("  ✅ No print statements found")

    # ============================================
    # SAVE CHANGES
    # ============================================
    print("")
    print("="*80)
    print("  📝 SAVING CHANGES")
    print("="*80)
    print("")

    if content != original_content:
        backup_path = views_path + ".backup_debug"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📝 Backup saved: {backup_path}")

        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ views.py updated")
    else:
        print("ℹ️ No changes needed")

    # ============================================
    # SUMMARY
    # ============================================
    print("")
    print("="*80)
    print("  ✅ DEBUG & CLEAN COMPLETE!")
    print("="*80)
    print("")

    print("📋 Summary:")
    print("-"*40)

    if fixes_applied:
        print("✅ Fixes applied:")
        for fix in fixes_applied:
            print(f"  • {fix}")
    else:
        print("ℹ️ No fixes applied")

    print("")

    if warnings:
        print("⚠️ Warnings (manual review recommended):")
        for warning in warnings:
            print(f"  • {warning}")
    else:
        print("✅ No warnings found")

    print("")
    print("="*80)
    print("  🚀 NEXT STEPS")
    print("="*80)
    print("")
    print("1. Review the changes:")
    print("   diff core/views.py.backup_debug core/views.py")
    print("")
    print("2. Test the application:")
    print("   python manage.py check")
    print("   python manage.py runserver")
    print("")
    print("3. If everything works, commit:")
    print("   git add core/views.py")
    print("   git commit -m 'Clean and debug views.py for production'")
    print("")
    print("4. If you need to rollback:")
    print("   Copy-Item core/views.py.backup_debug core/views.py -Force")
    print("")
    print("="*80)

def main():
    """Main function"""
    try:
        debug_and_clean_views()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
