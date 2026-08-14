#!/usr/bin/env python
# ============================================
# RESTORE MISSING VIEWS FUNCTIONS
# ============================================

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent if '__file__' in globals() else Path.cwd()
VIEWS_FILE = PROJECT_ROOT / 'core' / 'views.py'

def restore_missing_functions():
    """Restore the custom_login function and other missing functions."""

    print("=" * 80)
    print("🔧 RESTORING MISSING VIEWS FUNCTIONS")
    print("=" * 80)
    print()

    if not VIEWS_FILE.exists():
        print(f"❌ File not found: {VIEWS_FILE}")
        return False

    # Read the file
    with open(VIEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create backup
    backup_file = VIEWS_FILE.parent / f"{VIEWS_FILE.stem}_backup_restore_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📁 Backup created at: {backup_file}")

    # Check if custom_login exists
    if 'def custom_login' not in content:
        print("⚠️ custom_login function missing - adding it...")

        # Find where to insert the function
        # Look for the authentication section
        auth_section = """# ============================================
# AUTHENTICATION VIEWS
# ============================================

@never_cache
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Account permanently banned. Contact admin.')
                return render(request, 'login.html', {'error': 'Account permanently banned'})

            profile = get_teacher_profile(user)
            if profile:
                if not profile.is_approved and user.groups.filter(name='ClassTeacher').exists():
                    messages.error(request, 'Account pending admin approval.')
                    return render(request, 'login.html', {'error': 'Account pending approval'})
                if profile.is_suspended:
                    messages.error(request, f'Account suspended. Reason: {profile.suspension_reason}')
                    return render(request, 'login.html', {'error': 'Account suspended'})

            login(request, user)
            request.session.save()
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )

            if profile:
                profile.is_online = True
                profile.last_activity = timezone.now()
                profile.save(update_fields=['is_online', 'last_activity'])

            if user.groups.filter(name='ClassTeacher').exists():
                if not profile or not profile.has_chosen_stream:
                    return redirect('choose_stream')

            return redirect('/dashboard/')

        messages.error(request, 'Invalid username or password.')
        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')"""

        # Find where to insert - look for AUTHENTICATION VIEWS section
        if '# ============================================\n# AUTHENTICATION VIEWS' in content:
            # Find the end of the authentication section or insert after the header
            lines = content.split('\n')
            new_lines = []
            inserted = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                if '# ============================================\n# AUTHENTICATION VIEWS' in '\n'.join(lines[i:i+2]):
                    # Insert after the header
                    new_lines.append('')
                    new_lines.append(auth_section)
                    new_lines.append('')
                    inserted = True
                    # Skip the rest of the header
                    continue

            if not inserted:
                # Insert at the beginning of the file after imports
                content = auth_section + '\n' + content
        else:
            # Insert at the beginning
            content = auth_section + '\n' + content

        print("✅ Added custom_login function")

    # Check for other missing functions
    missing_functions = []
    for func in ['custom_logout', 'register', 'choose_stream', 'root_redirect', 'dashboard_redirect']:
        if f'def {func}' not in content:
            missing_functions.append(func)

    if missing_functions:
        print(f"⚠️ Missing functions: {', '.join(missing_functions)}")
        print("💡 These may need to be added manually from a backup.")

    # Write the fixed content
    with open(VIEWS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Functions restored successfully!")
    return True

def main():
    """Main function."""
    print("=" * 80)
    print("🔧 RESTORE MISSING VIEWS FUNCTIONS")
    print("=" * 80)
    print()

    if restore_missing_functions():
        print()
        print("=" * 80)
        print("✅ FUNCTIONS RESTORED SUCCESSFULLY!")
        print()
        print("📝 Next steps:")
        print("  1. Run: python manage.py check")
        print("  2. Run: python manage.py runserver")
        print("=" * 80)
    else:
        print()
        print("❌ Failed to restore functions")
        print("💡 Please check the file manually.")

if __name__ == '__main__':
    main()
