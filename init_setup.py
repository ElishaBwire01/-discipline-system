import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import Stream

# Create admin
if not User.objects.filter(is_superuser=True).exists():
    admin = User.objects.create_superuser('admin', 'admin@school.com', 'Admin@2025#')
    admin.first_name = 'System'
    admin.last_name = 'Administrator'
    admin.save()
    print("✓ Admin created: admin / Admin@2025#")

# Create groups
Group.objects.get_or_create(name='ClassTeacher')
Group.objects.get_or_create(name='Teacher')
print("✓ Groups created")

# Create streams
streams = ['MULUMBA', 'KIZZA', 'LUKA', 'GONZA', 'KAAGWA', 'MUKASA', 'WASWA', 'MUWANGA', 'KIZITO']
for stream_name in streams:
    Stream.objects.get_or_create(name=stream_name)
print(f"✓ {Stream.objects.count()} streams created")

print("\n✅ Setup complete!")
