#!/usr/bin/env python
"""
test_hybrid.py
Test the hybrid storage configuration
Run: python test_hybrid.py
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from core.models import TeacherProfile


def test_hybrid():
    """Test hybrid storage configuration"""

    print("="*60)
    print("  🔧 TESTING HYBRID STORAGE")
    print("="*60)
    print("")

    # Test 1: Check storage type
    print("📌 Test 1: Storage Type")
    print(f"  DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    if "FileSystemStorage" in settings.DEFAULT_FILE_STORAGE:
        print("  ✅ Using LOCAL storage for media files")
    else:
        print(f"  ⚠️ Using: {settings.DEFAULT_FILE_STORAGE}")
    print("")

    # Test 2: Check media path
    print("📌 Test 2: Media Path")
    print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"  MEDIA_URL: {settings.MEDIA_URL}")
    if os.path.exists(settings.MEDIA_ROOT):
        print("  ✅ Media directory exists")
    else:
        print("  ⚠️ Media directory not found")
    print("")

    # Test 3: Check database
    print("📌 Test 3: Database Connection")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"  ✅ Connected to: {version[0][:50]}...")
    print("")

    # Test 4: Check upload
    print("📌 Test 4: File Upload Test")
    try:
        test_file = ContentFile(b"Test content", name="test.txt")
        saved_path = default_storage.save("test_upload.txt", test_file)
        if default_storage.exists(saved_path):
            print(f"  ✅ File saved to: {saved_path}")
            default_storage.delete(saved_path)
        else:
            print(f"  ❌ File not saved")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print("")

    # Test 5: Check profile picture
    print("📌 Test 5: Profile Picture Check")
    try:
        user = User.objects.filter(is_superuser=True).first()
        if user:
            profile = TeacherProfile.objects.filter(user=user).first()
            if profile and profile.profile_picture:
                print(f"  ✅ Profile picture found at: {profile.profile_picture.path}")
                if os.path.exists(profile.profile_picture.path):
                    print(f"  ✅ File exists: {profile.profile_picture.path}")
                else:
                    print(f"  ⚠️ File not found on disk")
            else:
                print("  ℹ️ No profile picture uploaded yet")
        else:
            print("  ℹ️ No admin user found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print("")

    print("="*60)
    print("  ✅ TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_hybrid()
