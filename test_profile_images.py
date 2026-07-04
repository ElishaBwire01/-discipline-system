# test_profile_images.py
# Run this to test profile image functionality

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TeacherProfile

print("Checking profile images...")
print("=" * 50)

users = User.objects.all()
for user in users:
    try:
        profile = user.teacher_profile
        if profile.profile_picture:
            print(f"? {user.username}: {profile.profile_picture.url}")
        else:
            print(f"? {user.username}: No profile picture")
    except:
        print(f"?? {user.username}: No teacher profile")
