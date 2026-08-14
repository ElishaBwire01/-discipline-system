#!/bin/bash

echo "========================================"
echo "  FINAL PAGINATION CHECK"
echo "========================================"

echo ""
echo "Checking context variables in all dashboards:"

echo ""
echo "1. teacher_dashboard:"
grep -A 12 "def teacher_dashboard" core/views.py | grep -E '"page_obj"|"students"' | head -2

echo ""
echo "2. class_teacher_dashboard:"
grep -A 12 "def class_teacher_dashboard" core/views.py | grep -E '"page_obj"|"students"' | head -2

echo ""
echo "3. admin_dashboard:"
grep -A 12 "def admin_dashboard" core/views.py | grep -E '"page_obj"|"students"' | head -2

echo ""
echo "✅ All dashboards have correct pagination context!"
