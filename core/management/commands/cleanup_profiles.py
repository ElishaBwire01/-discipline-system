from django.core.management.base import BaseCommand
from core.models import TeacherProfile, Stream

class Command(BaseCommand):
    help = 'Clean up teacher profiles with deleted streams'

    def handle(self, *args, **options):
        # Find teacher profiles with assigned streams that don't exist
        profiles = TeacherProfile.objects.filter(assigned_stream__isnull=False)
        cleaned = 0
        
        for profile in profiles:
            try:
                # Check if the stream still exists
                stream = Stream.objects.get(id=profile.assigned_stream.id, is_active=True)
            except Stream.DoesNotExist:
                # Stream was deleted, remove it from profile
                self.stdout.write(f"⚠️ Cleaning up profile for: {profile.user.username}")
                profile.assigned_stream = None
                profile.has_chosen_stream = False
                profile.is_approved = False
                profile.save()
                cleaned += 1
        
        self.stdout.write(self.style.SUCCESS(f"✅ Cleaned up {cleaned} teacher profiles with deleted streams"))
