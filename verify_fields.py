import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import TeacherProfile, Student

# Check TeacherProfile fields
teacher_fields = [f.name for f in TeacherProfile._meta.get_fields()]
if 'profile_picture' in teacher_fields:
    print("✓ TeacherProfile has profile_picture field")
else:
    print("✗ TeacherProfile MISSING profile_picture field")

# Check Student fields
student_fields = [f.name for f in Student._meta.get_fields()]
if 'profile_picture' in student_fields:
    print("✓ Student has profile_picture field")
else:
    print("✗ Student MISSING profile_picture field")
