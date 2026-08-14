#!/bin/bash

# Backup the template
cp templates/edit_student.html templates/edit_student.html.backup 2>/dev/null

# Update the template to use grade_level
sed -i 's/name="grade"/name="grade_level"/g' templates/edit_student.html
sed -i 's/student.grade/student.grade_level/g' templates/edit_student.html
sed -i 's/in grades %}/in grade_levels %}/g' templates/edit_student.html

echo "✅ Updated edit_student.html"
