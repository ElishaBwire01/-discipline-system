import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TeacherProfile

print('Testing profile picture URL...')
try:
    user = User.objects.get(username='cmcbangladesh')
    profile = user.teacher_profile
    
    if profile.profile_picture:
        print(f'? Image URL: {profile.profile_picture.url}')
    else:
        print('? No profile picture found')
except Exception as e:
    print(f'? Error: {e}')