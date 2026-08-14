#!/bin/bash

echo "========================================"
echo "  SCHOOL SETUP ANALYSIS"
echo "========================================"

echo -e "\n📁 Template File:"
echo "------------------"
ls -la templates/school_setup.html 2>/dev/null || echo "File not found"

echo -e "\n📄 Template Content (first 100 lines):"
echo "----------------------------------------"
head -100 templates/school_setup.html

echo -e "\n🔍 Grade/Form References in Template:"
echo "--------------------------------------"
grep -n "Form\|Grade\|grade\|form" templates/school_setup.html | head -20

echo -e "\n🔍 View Function:"
echo "-----------------"
grep -A 30 "def school_setup" core/views.py

echo -e "\n🔍 Model Definitions:"
echo "---------------------"
grep -A 15 "class GradeLevel" core/models.py
grep -A 15 "class Stream" core/models.py

echo -e "\n🔍 Form Definitions:"
echo "-------------------"
grep -A 20 "class.*Form.*school" core/forms.py

echo -e "\n✅ Analysis Complete!"
