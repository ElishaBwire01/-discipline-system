import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import Stream

# All streams
streams = ['MULUMBA', 'KIZZA', 'LUKA', 'GONZA', 'KAAGWA', 'MUKASA', 'WASWA', 'MUWANGA', 'KIZITO']

print("Checking streams...")
for stream_name in streams:
    stream, created = Stream.objects.get_or_create(name=stream_name)
    if created:
        print(f"  ✓ Created stream: {stream.get_name_display()}")
    else:
        print(f"  ✓ Stream already exists: {stream.get_name_display()}")

print(f"\n✅ Total streams: {Stream.objects.count()}")
print("\n📋 Available Streams:")
for stream in Stream.objects.all():
    print(f"   - {stream.get_name_display()}")
