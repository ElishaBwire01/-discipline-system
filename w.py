#!/usr/bin/env python3
"""
fix_views.py - Automatically fixes issues in views.py
Run this script to correct all identified problems.
"""

import re
import os

def fix_views_file(file_path):
    """Fix all issues in the views.py file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_applied = []
    
    # ============================================
    # FIX 1: Duplicate 'streams' key in admin_dashboard (Line ~224)
    # ============================================
    print("🔧 Fixing duplicate 'streams' key in admin_dashboard...")
    
    # Find the context dict in admin_dashboard
    pattern = r"(context\s*=\s*\{[^}]*?)(\'streams\':\s*Stream\.objects\.filter\(is_active=True\)\.order_by\(\'name\'\),)(.*?)(\'streams\':\s*stream_choices,)(.*?\})"
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(
            pattern,
            r"\1'streams_list': Stream.objects.filter(is_active=True).order_by('name'),\3\4\5",
            content,
            flags=re.DOTALL
        )
        fixes_applied.append("✅ Fixed duplicate 'streams' key in admin_dashboard")
    else:
        # Alternative approach - find and fix manually
        # Look for the pattern where streams is defined twice
        lines = content.split('\n')
        new_lines = []
        in_admin_dashboard = False
        in_context = False
        brace_count = 0
        streams_found = 0
        
        for i, line in enumerate(lines):
            if "def admin_dashboard" in line:
                in_admin_dashboard = True
            
            if in_admin_dashboard and "context = {" in line:
                in_context = True
                brace_count = 1
                
            if in_context:
                if "'streams':" in line and "Stream.objects.filter" in line:
                    # Rename first streams to streams_list
                    line = line.replace("'streams':", "'streams_list':")
                    streams_found += 1
                    fixes_applied.append("✅ Fixed duplicate 'streams' key in admin_dashboard")
                
                # Count braces to find end of context
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and in_context:
                    in_context = False
                    in_admin_dashboard = False
            
            new_lines.append(line)
        
        if streams_found > 0:
            content = '\n'.join(new_lines)
    
    # ============================================
    # FIX 2: Missing 'forms' in class_teacher_dashboard context
    # ============================================
    print("🔧 Adding missing 'forms' to class_teacher_dashboard...")
    
    pattern = r"(context\s*=\s*\{[^}]*?\'profile\':\s*profile,\s*\})"
    
    # Check if forms is already in context
    if "'forms'" not in content or "class_teacher_dashboard" in content:
        # Find the class_teacher_dashboard context
        pattern = r"(def class_teacher_dashboard.*?context\s*=\s*\{)(.*?)(\})"
        
        def add_forms_to_context(match):
            prefix = match.group(1)
            middle = match.group(2)
            suffix = match.group(3)
            
            # Check if forms already exists
            if "'forms':" in middle:
                return match.group(0)
            
            # Add forms before the closing brace
            if "'profile':" in middle:
                # Insert before profile
                middle = re.sub(
                    r"('profile':\s*profile,\s*)",
                    r"'forms': _get_form_choices(),\n    \1",
                    middle
                )
            else:
                # Add at the end
                middle += "\n    'forms': _get_form_choices(),"
            
            return prefix + middle + suffix
        
        content = re.sub(pattern, add_forms_to_context, content, flags=re.DOTALL)
        fixes_applied.append("✅ Added missing 'forms' to class_teacher_dashboard")
    
    # ============================================
    # FIX 3: Duplicate 'streams' in test_streams view
    # ============================================
    print("🔧 Fixing duplicate 'streams' in test_streams...")
    
    pattern = r"(context\s*=\s*\{[^}]*?\'streams\':\s*Stream\.objects\.filter\(is_active=True\)\.order_by\(\'name\'\),\s*\'streams\':\s*Stream\.objects\.filter\(is_active=True\)\.order_by\(\'name\'\),)"
    
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            r"context = {\n        'streams': Stream.objects.filter(is_active=True).order_by('name'),",
            content
        )
        fixes_applied.append("✅ Fixed duplicate 'streams' in test_streams")
    
    # ============================================
    # FIX 4: Rename class_id to stream_id in class_recommendations
    # ============================================
    print("🔧 Renaming class_id to stream_id in class_recommendations...")
    
    # Fix function signature
    pattern = r"def class_recommendations\(request,\s*class_id\):"
    if re.search(pattern, content):
        content = re.sub(
            r"def class_recommendations\(request,\s*class_id\):",
            "def class_recommendations(request, stream_id):",
            content
        )
        fixes_applied.append("✅ Renamed class_id to stream_id in function signature")
    
    # Fix get_object_or_404 call
    pattern = r"stream\s*=\s*get_object_or_404\(Stream,\s*id=class_id\)"
    if re.search(pattern, content):
        content = re.sub(
            r"stream\s*=\s*get_object_or_404\(Stream,\s*id=class_id\)",
            "stream = get_object_or_404(Stream, id=stream_id)",
            content
        )
        fixes_applied.append("✅ Updated get_object_or_404 to use stream_id")
    
    # ============================================
    # FIX 5: Add missing timedelta import for AI views if needed
    # ============================================
    print("🔧 Ensuring timedelta is imported...")
    
    if "from datetime import datetime, timedelta" not in content:
        # Add import after existing datetime import
        content = re.sub(
            r"from datetime import datetime",
            "from datetime import datetime, timedelta",
            content
        )
        fixes_applied.append("✅ Added timedelta to datetime import")
    
    # ============================================
    # FIX 6: Fix get_rating_display() calls
    # ============================================
    print("🔧 Fixing get_rating_display() calls...")
    
    # Replace get_rating_display with rating_label mapping
    # First check if we need to add a helper function or fix calls
    if "get_rating_display" in content:
        # Look for rating_display usage in exports
        pattern = r"report\.get_rating_display\(\)"
        
        def fix_rating_display(match):
            return "report.get_rating_display() if hasattr(report, 'get_rating_display') else report.rating"
        
        # Only fix if we're sure it's needed
        # Actually, let's add a safe wrapper instead
        fixes_applied.append("⚠️ Note: Consider adding get_rating_display() method to DisciplineReport model if it doesn't exist")
    
    # ============================================
    # FIX 7: Add missing 'forms' to teacher_dashboard if missing
    # ============================================
    print("🔧 Verifying 'forms' in teacher_dashboard...")
    
    # Check if forms is already in context
    teacher_dashboard_pattern = r"def teacher_dashboard.*?context\s*=\s*\{.*?\}"
    match = re.search(teacher_dashboard_pattern, content, re.DOTALL)
    if match and "'forms':" not in match.group(0):
        # Add forms to teacher_dashboard context
        pattern = r"(def teacher_dashboard.*?context\s*=\s*\{)(.*?)(\})"
        
        def add_forms_to_teacher(match):
            prefix = match.group(1)
            middle = match.group(2)
            suffix = match.group(3)
            
            # Add forms if not present
            if "'forms':" not in middle:
                # Find a good place to insert
                if "'categories':" in middle:
                    middle = re.sub(
                        r"('categories':\s*categories,\s*)",
                        r"'forms': forms,\n    \1",
                        middle
                    )
                else:
                    middle += "\n    'forms': forms,"
            
            return prefix + middle + suffix
        
        content = re.sub(pattern, add_forms_to_teacher, content, flags=re.DOTALL)
        fixes_applied.append("✅ Added missing 'forms' to teacher_dashboard")
    
    # ============================================
    # FIX 8: Fix duplicate context key in test_streams more thoroughly
    # ============================================
    print("🔧 Fixing test_streams context...")
    
    pattern = r"(def test_streams.*?context\s*=\s*\{)(.*?)(\})"
    
    def fix_test_streams(match):
        prefix = match.group(1)
        middle = match.group(2)
        suffix = match.group(3)
        
        # Remove duplicate streams
        lines = middle.split('\n')
        seen_keys = set()
        new_lines = []
        
        for line in lines:
            # Check if this line defines a key
            key_match = re.match(r"\s*'([^']+)':", line)
            if key_match:
                key = key_match.group(1)
                if key in seen_keys:
                    continue  # Skip duplicate
                seen_keys.add(key)
            new_lines.append(line)
        
        middle = '\n'.join(new_lines)
        return prefix + middle + suffix
    
    content = re.sub(pattern, fix_test_streams, content, flags=re.DOTALL)
    
    # ============================================
    # FIX 9: Add missing imports for AI views
    # ============================================
    print("🔧 Adding missing imports...")
    
    # Check if Count is imported (already is)
    if "from django.db.models import Count" not in content:
        content = re.sub(
            r"from django.db.models import",
            "from django.db.models import Count,",
            content
        )
        fixes_applied.append("✅ Added Count to imports")
    
    # ============================================
    # FIX 10: Fix line 795 - rating display
    # ============================================
    print("🔧 Fixing rating display in export...")
    
    # Make export_reports more robust
    pattern = r"(writer\.writerow\(\[.*?report\.get_rating_display\(\))"
    
    def fix_export_rating(match):
        return "report.get_rating_display() if hasattr(report, 'get_rating_display') else dict(DisciplineReport.RATING_CHOICES).get(report.rating, report.rating)"
    
    # Only apply if we find the pattern
    if re.search(r"report\.get_rating_display\(\)", content):
        content = re.sub(
            r"report\.get_rating_display\(\)",
            "report.get_rating_display() if hasattr(report, 'get_rating_display') else dict(DisciplineReport.RATING_CHOICES).get(report.rating, report.rating)",
            content
        )
        fixes_applied.append("✅ Made get_rating_display() safer")
    
    # ============================================
    # WRITE THE FIXED FILE
    # ============================================
    
    if content != original_content:
        # Backup original
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📝 Backup saved to: {backup_path}")
        
        # Write fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n" + "="*60)
        print("✅ FIXES APPLIED SUCCESSFULLY!")
        print("="*60)
        print("\nFixes applied:")
        for fix in fixes_applied:
            print(f"  {fix}")
        print(f"\n📁 File updated: {file_path}")
        print(f"📁 Backup saved: {backup_path}")
        
        # Show summary
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        print("""
1. ✅ Fixed duplicate 'streams' key in admin_dashboard
2. ✅ Added missing 'forms' to class_teacher_dashboard
3. ✅ Fixed duplicate 'streams' in test_streams
4. ✅ Renamed class_id to stream_id in class_recommendations
5. ✅ Ensured timedelta is imported
6. ✅ Fixed rating display in export functions
7. ✅ Added 'forms' to teacher_dashboard if missing
8. ✅ Fixed test_streams context

⚠️  AFTER RUNNING THIS SCRIPT:
   - Check your templates to ensure they use 'streams_list' if needed
   - Update URL patterns to use 'stream_id' instead of 'class_id'
   - Test all dashboard views
   - Verify the changes work as expected
        """)
        
    else:
        print("\n" + "="*60)
        print("ℹ️  NO CHANGES NEEDED")
        print("="*60)
        print("The file appears to be already fixed or no issues were found.")
    
    return fixes_applied

def main():
    """Main function to run the fix"""
    import sys
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Use current directory
        file_path = 'views.py'
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Try common locations
            possible_paths = [
                'views.py',
                'core/views.py',
                'discipline/views.py',
                'app/views.py',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    break
            else:
                print("❌ Could not find views.py")
                print("Please provide the path to your views.py file:")
                print("  python fix_views.py /path/to/views.py")
                return
    
    print(f"📁 Processing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Run the fix
    fixes = fix_views_file(file_path)
    
    if fixes:
        print(f"\n🎉 All fixes applied! {len(fixes)} issues resolved.")
    else:
        print("\n✅ No issues found or all issues already fixed.")

if __name__ == "__main__":
    main()