import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import Stream, DisciplineCategory

# Create admin
if not User.objects.filter(is_superuser=True).exists():
    admin = User.objects.create_superuser('admin', 'admin@school.com', 'Admin@2025#')
    admin.first_name = 'System'
    admin.last_name = 'Administrator'
    admin.save()
    print("✓ Admin created")

# Create groups
Group.objects.get_or_create(name='ClassTeacher')
Group.objects.get_or_create(name='Teacher')

# Create streams
streams = ['MULUMBA', 'KIZZA', 'LUKA', 'GONZA', 'KAAGWA', 'MUKASA', 'WASWA', 'MUWANGA', 'KIZITO']
for s in streams:
    Stream.objects.get_or_create(name=s)
print("✓ Streams created")

# Create categories
categories = [
    ('GUIDANCE', 'Personal Stress Issues', 15),
    ('INDISCIPLINE', 'Bad Replying / Indiscipline', 20),
    ('CARELESS', 'Lazy / Not Finishing Notes', 10),
    ('FIGHTING', 'Fighting', 30),
    ('COUPLING', 'Coupling', 40),
]
for key, name, points in categories:
    DisciplineCategory.objects.get_or_create(key=key, defaults={'name': name, 'points': points})
print("✓ Categories created")
