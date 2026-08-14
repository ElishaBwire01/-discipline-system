#!/bin/bash

echo "========================================"
echo "  USER REGISTRATION FLOW TRACKER"
echo "========================================"
echo ""

cd ~/disciplinev12

echo "1. REGISTRATION FLOW"
echo "────────────────────"
echo ""
echo "FRONTEND: templates/register.html"
echo "  → User submits: first_name, last_name, username, email, password, role"
echo "  → JavaScript validates: password match, strength, required fields"
echo ""
echo "BACKEND: core/views.py → register()"
echo "  → Receives POST data"
echo "  → Validates: username unique, password match, email format"
echo "  → Creates User (is_active=True)"
echo "  → Adds to group: Teacher or ClassTeacher"
echo "  → Creates TeacherProfile (is_approved=False for ClassTeacher)"
echo "  → Sends notification to admin (if ClassTeacher)"
echo "  → Redirects to /login/"
echo ""

echo "2. TEACHER vs CLASS TEACHER"
echo "───────────────────────────"
echo ""
echo "TEACHER:"
echo "  → Group: Teacher"
echo "  → Profile: is_approved=True"
echo "  → Status: ACTIVE"
echo "  → Can login immediately"
echo "  → Can report students"
echo ""
echo "CLASS TEACHER:"
echo "  → Group: ClassTeacher"
echo "  → Profile: is_approved=False"
echo "  → Status: PENDING"
echo "  → Needs admin approval"
echo "  → Needs stream selection"
echo ""

echo "3. PENDING MODE - DATABASE STATE"
echo "────────────────────────────────"
python3 << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TeacherProfile

print()
print("DATABASE STATE:")
print("───────────────")

class_teachers = User.objects.filter(groups__name='ClassTeacher')
print(f"Class Teachers: {class_teachers.count()}")

for user in class_teachers:
    try:
        profile = TeacherProfile.objects.get(user=user)
        print(f"\nUser: {user.username}")
        print(f"  is_approved: {profile.is_approved}")
        print(f"  has_chosen_stream: {profile.has_chosen_stream}")
        if not profile.is_approved:
            print(f"  STATUS: PENDING APPROVAL - Cannot login")
        elif not profile.has_chosen_stream and profile.is_approved:
            print(f"  STATUS: NEEDS STREAM SELECTION")
        else:
            print(f"  STATUS: ACTIVE - Full access")
    except TeacherProfile.DoesNotExist:
        print(f"\nUser: {user.username} - No TeacherProfile")

teachers = User.objects.filter(groups__name='Teacher')
print(f"\nTeachers: {teachers.count()}")
for user in teachers:
    try:
        profile = TeacherProfile.objects.get(user=user)
        print(f"\nUser: {user.username}")
        print(f"  is_approved: {profile.is_approved}")
        print(f"  STATUS: ACTIVE - Can login immediately")
    except TeacherProfile.DoesNotExist:
        print(f"\nUser: {user.username} - No TeacherProfile")
PYEOF

echo ""
echo "4. LOGIN AUTHENTICATION CHECKS"
echo "──────────────────────────────"
echo ""
echo "custom_login() view checks in order:"
echo "  1. authenticate(username, password)"
echo "  2. Check if user exists and password is correct"
echo "  3. Check if user.is_active (not banned)"
echo "  4. Get TeacherProfile"
echo "  5. If ClassTeacher:"
echo "       ├─ Check is_approved → DENY if False"
echo "       ├─ Check is_suspended → DENY if True"
echo "       └─ Check has_chosen_stream → Redirect to /choose-stream/"
echo "  6. login(request, user) → SUCCESS"
echo "  7. Create UserSession"
echo "  8. Set is_online = True"
echo "  9. Redirect to /dashboard/"
echo ""

echo "5. CLASS TEACHER PENDING → ACTIVE FLOW"
echo "───────────────────────────────────────"
echo ""
echo "Step 1: Class Teacher Registers"
echo "  → role: class_teacher"
echo "  → User created: is_active=True"
echo "  → Group: ClassTeacher"
echo "  → TeacherProfile: is_approved=False (PENDING)"
echo "  → Notification sent to admins"
echo "  → Redirected to /login/"
echo ""
echo "Step 2: Class Teacher Tries to Login"
echo "  → POST /login/"
echo "  → authenticate() → SUCCESS"
echo "  → Check TeacherProfile.is_approved → False"
echo "  → ERROR: Account pending admin approval"
echo "  → Stays on login page"
echo ""
echo "Step 3: Admin Approves"
echo "  → Admin visits /manage-users/"
echo "  → Clicks Approve → POST /approve-user/<id>/"
echo "  → TeacherProfile.is_approved = True"
echo "  → Notification sent to teacher"
echo ""
echo "Step 4: Class Teacher Logs In Now"
echo "  → POST /login/"
echo "  → authenticate() → SUCCESS"
echo "  → Check TeacherProfile.is_approved → True"
echo "  → Check has_chosen_stream → False"
echo "  → Redirected to /choose-stream/"
echo ""
echo "Step 5: Class Teacher Chooses Stream"
echo "  → GET /choose-stream/"
echo "  → POST: stream_id=X, form=Form_1"
echo "  → TeacherProfile.assigned_stream = stream"
echo "  → TeacherProfile.assigned_form = form"
echo "  → TeacherProfile.has_chosen_stream = True"
echo "  → Redirect to /class-teacher-dashboard/"
echo ""

echo "6. WHERE DATA LIVES IN DATABASE"
echo "───────────────────────────────"
python3 << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TeacherProfile, Notification

print()
print("DATA LOCATIONS:")
print("───────────────")

pending = TeacherProfile.objects.filter(is_approved=False, is_suspended=False)
print(f"PENDING APPROVAL: {pending.count()} users")
for p in pending:
    print(f"  - {p.user.username}: TeacherProfile.is_approved=False")

stream_pending = TeacherProfile.objects.filter(is_approved=True, has_chosen_stream=False)
print(f"\nNEED STREAM SELECTION: {stream_pending.count()} users")
for p in stream_pending:
    print(f"  - {p.user.username}: TeacherProfile.has_chosen_stream=False")

active = TeacherProfile.objects.filter(is_approved=True, has_chosen_stream=True, is_suspended=False)
print(f"\nACTIVE: {active.count()} users")
for p in active[:3]:
    print(f"  - {p.user.username}: {p.assigned_stream} - {p.assigned_form}")

notifications = Notification.objects.filter(title__icontains='approval').count()
print(f"\nPENDING APPROVAL NOTIFICATIONS: {notifications}")
PYEOF

echo ""
echo "7. FILE LOCATIONS"
echo "─────────────────"
echo ""
echo "FRONTEND (Templates):"
echo "  templates/register.html - Registration form"
echo "  templates/login.html - Login form"
echo "  templates/choose_stream.html - Stream selection"
echo "  templates/admin_dashboard.html - Admin dashboard"
echo "  templates/class_teacher_dashboard.html - Class Teacher dashboard"
echo "  templates/teacher_dashboard.html - Teacher dashboard"
echo ""
echo "BACKEND (Views):"
echo "  core/views.py"
echo "    - register() - User registration"
echo "    - custom_login() - Login handler"
echo "    - dashboard_redirect() - Role-based redirect"
echo "    - choose_stream() - Stream selection"
echo "    - approve_user() - Admin approval"
echo "    - class_teacher_dashboard() - Class Teacher dashboard"
echo ""
echo "MODELS (Database):"
echo "  core/models.py"
echo "    - User (Django built-in) - is_active, groups"
echo "    - TeacherProfile - is_approved, has_chosen_stream, assigned_stream"
echo "    - UserSession - Login tracking"
echo "    - Notification - Admin alerts"
echo "    - PasswordReset - Reset flow"
echo ""

echo "8. COMPLETE SUMMARY"
echo "───────────────────"
echo ""
echo "USER STATES:"
echo "  1. PENDING APPROVAL (Class Teachers)"
echo "     → Database: TeacherProfile.is_approved = False"
echo "     → Login: ERROR - Account pending approval"
echo "     → Admin can approve via /manage-users/"
echo ""
echo "  2. PENDING STREAM (Approved Class Teachers)"
echo "     → Database: TeacherProfile.has_chosen_stream = False"
echo "     → Login: Redirected to /choose-stream/"
echo "     → Must select stream + form"
echo ""
echo "  3. FULLY ACTIVE (Teachers + Class Teachers)"
echo "     → Database: is_approved=True, has_chosen_stream=True"
echo "     → Login: Full dashboard access"
echo "     → Dashboard: Role-appropriate"
echo ""
echo "ROUTES:"
echo "  Register:     /register/"
echo "  Login:        /login/"
echo "  Admin:        /admin-dashboard/"
echo "  Manage Users: /manage-users/"
echo "  Choose Stream: /choose-stream/"
echo ""

echo "========================================"
echo "  TRACE COMPLETE"
echo "========================================"
