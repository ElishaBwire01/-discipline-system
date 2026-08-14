#!/bin/bash

echo "========================================"
echo "  REGISTRATION FLOW - ACTUAL CODE"
echo "========================================"
echo ""

cd ~/disciplinev12

echo "1. REGISTER VIEW (core/views.py)"
echo "────────────────────────────────"
grep -A 80 "def register(request):" core/views.py | head -85
echo ""

echo "2. LOGIN VIEW (core/views.py)"
echo "─────────────────────────────"
grep -A 60 "def custom_login(request):" core/views.py | head -65
echo ""

echo "3. DASHBOARD REDIRECT (core/views.py)"
echo "─────────────────────────────────────"
grep -A 15 "def dashboard_redirect(request):" core/views.py
echo ""

echo "4. CHOOSE STREAM VIEW (core/views.py)"
echo "─────────────────────────────────────"
grep -A 40 "def choose_stream(request):" core/views.py | head -45
echo ""

echo "5. APPROVE USER VIEW (core/views.py)"
echo "────────────────────────────────────"
grep -A 20 "def approve_user(request, user_id):" core/views.py
echo ""

echo "6. REGISTER TEMPLATE (templates/register.html)"
echo "───────────────────────────────────────────────"
grep -A 30 '<form method="post"' templates/register.html | head -35
echo ""

echo "7. LOGIN TEMPLATE (templates/login.html)"
echo "─────────────────────────────────────────"
grep -A 20 '<form method="post"' templates/login.html | head -25
echo ""

echo "8. CHOOSE STREAM TEMPLATE (templates/choose_stream.html)"
echo "─────────────────────────────────────────────────────────"
grep -A 20 '<form method="post"' templates/choose_stream.html | head -25
echo ""

echo "9. TEACHERPROFILE MODEL (core/models.py)"
echo "────────────────────────────────────────"
grep -A 30 "class TeacherProfile(models.Model):" core/models.py | head -35
echo ""

echo "10. USER MODEL REFERENCE (core/models.py)"
echo "─────────────────────────────────────────"
grep -A 10 "class Student(models.Model):" core/models.py | head -15
echo ""

echo "11. NOTIFICATION MODEL (core/models.py)"
echo "───────────────────────────────────────"
grep -A 20 "class Notification(models.Model):" core/models.py | head -25
echo ""

echo "12. URL PATTERNS (core/urls.py)"
echo "───────────────────────────────"
grep -E "register/|login/|dashboard/|choose-stream/|approve-user/" core/urls.py
echo ""

echo "========================================"
echo "  CODE DISPLAY COMPLETE"
echo "========================================"
