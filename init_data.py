#!/usr/bin/env python
"""Initialize disciplinary program with system data only - no demo users"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import Stream, DisciplineCategory, TeacherProfile

def init():
    print("Initializing Disciplinary Program System Data...")
    
    # Create streams (school data)
    streams = ['MULUMBA', 'KIZZA', 'LUKA', 'GONZA', 'KAAGWA', 'MUKASA', 'WASWA', 'MUWANGA', 'KIZITO']
    for stream_name in streams:
        Stream.objects.get_or_create(name=stream_name)
    print(f"✓ Created {Stream.objects.count()} streams")
    
    # Create discipline categories
    categories = [
        ('GUIDANCE', 'Personal Stress Issues', 15),
        ('INDISCIPLINE', 'Bad Replying / Indiscipline', 20),
        ('CARELESS', 'Lazy / Not Finishing Notes', 10),
        ('FIGHTING', 'Fighting', 30),
        ('COUPLING', 'Coupling', 40),
    ]
    for key, name, points in categories:
        DisciplineCategory.objects.get_or_create(key=key, defaults={'name': name, 'points': points})
    print(f"✓ Created {DisciplineCategory.objects.count()} categories")
    
    # Create groups
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='ClassTeacher')
    Group.objects.get_or_create(name='Teacher')
    print("✓ Created user groups")
    
    # Check if admin exists, if not create with secure password
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
        print("  ⚠️ IMPORTANT: Change password after first login!")
    else:
        print("✓ Admin user already exists")
    
    print("\n✅ System initialization complete!")
    print("\n📋 System Status:")
    print(f"   Streams: {Stream.objects.count()}")
    print(f"   Categories: {DisciplineCategory.objects.count()}")
    print(f"   Groups: 3 (Admin, ClassTeacher, Teacher)")
    print("   Users: 1 (admin)")
    print("\n⚠️  No demo users created. All users must register.")

if __name__ == '__main__':
    init()
