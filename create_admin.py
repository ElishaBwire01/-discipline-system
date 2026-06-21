import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(is_superuser=True).exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@school.com',
        password='Admin@2025#'
    )
    admin.first_name = 'System'
    admin.last_name = 'Administrator'
    admin.save()
    print("✓ Admin created: admin / Admin@2025#")
else:
    print("✓ Admin already exists")
