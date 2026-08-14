#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def clear_and_create_superuser():
    with transaction.atomic():
        # Find and delete all existing superusers
        existing_superusers = User.objects.filter(is_superuser=True)
        count = existing_superusers.count()
        
        if count > 0:
            print(f"🗑️  Found {count} existing superuser(s):")
            for user in existing_superusers:
                print(f"   - {user.username} (ID: {user.id})")
            existing_superusers.delete()
            print(f"✅ Deleted {count} existing superuser(s)")
        else:
            print("ℹ️  No existing superusers found")
        
        # Create new superuser
        username = "Elisha"
        email = "elisha@school.com"
        password = "10203040"
        
        # Check if user exists as regular user
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            print(f"⚠️  User '{username}' exists as regular user. Promoting to superuser...")
            existing_user.is_superuser = True
            existing_user.is_staff = True
            existing_user.set_password(password)
            existing_user.save()
            new_user = existing_user
        else:
            # Create new superuser
            new_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        
        print(f"\n✅ Superuser created successfully!")
        print(f"   👤 Username: {new_user.username}")
        print(f"   📧 Email: {new_user.email}")
        print(f"   🔑 Password: {password}")
        print(f"   👑 Superuser: {new_user.is_superuser}")
        print(f"   💼 Staff: {new_user.is_staff}")
        print(f"   🆔 ID: {new_user.id}")
        
        # Show all users in system
        print("\n📋 All users in system:")
        print("-" * 40)
        for user in User.objects.all():
            print(f"  • {user.username} (ID: {user.id})")
            print(f"    - Superuser: {'✅' if user.is_superuser else '❌'}")
            print(f"    - Staff: {'✅' if user.is_staff else '❌'}")
            print(f"    - Active: {'✅' if user.is_active else '❌'}")
            print("-" * 40)
        
        print(f"\n📊 Total users: {User.objects.count()}")
        print(f"👑 Superusers: {User.objects.filter(is_superuser=True).count()}")

if __name__ == "__main__":
    print("=" * 60)
    print("  CLEAR SUPERUSERS & CREATE NEW SUPERUSER")
    print("=" * 60)
    clear_and_create_superuser()
    print("\n✅ Script completed successfully!")
