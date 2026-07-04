from django.core.management.base import BaseCommand
from core.models import School, Stream, GradeLevel, AcademicTerm
from django.contrib.auth.models import User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Initialize school data - only creates basic structure'

    def handle(self, *args, **options):
        # Check if admin exists
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('⚠️ No admin user found! Create one with: python manage.py createsuperuser'))
            return

        # Create school if not exists
        school, created = School.objects.get_or_create(
            id=1,
            defaults={
                'name': 'My School',
                'short_name': 'MS',
                'current_year': 2026,
                'terms_per_year': 3,
                'allow_teacher_registration': True,
                'require_teacher_approval': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created school: {school.name}'))
        else:
            self.stdout.write(f'ℹ️ School already exists: {school.name}')

        # Check if streams exist - if not, create default ones
        if Stream.objects.filter(school=school).count() == 0:
            streams = ['Mulumba', 'Kizza', 'Luka', 'Gonza', 'Kaagwa', 'Mukasa', 'Waswa', 'Muwanga', 'Kizito']
            for stream_name in streams:
                Stream.objects.create(
                    school=school,
                    name=stream_name,
                    code=stream_name[:3].upper(),
                    is_active=True
                )
                self.stdout.write(f'✅ Created stream: {stream_name}')
        else:
            self.stdout.write(f'ℹ️ Streams already exist: {Stream.objects.filter(school=school).count()} found')

        # Check if grades exist - if not, create default ones
        if GradeLevel.objects.filter(school=school).count() == 0:
            for i in range(1, 7):
                GradeLevel.objects.create(
                    school=school,
                    name=f'Form {i}',
                    code=f'F{i}',
                    order=i,
                    is_active=True
                )
                self.stdout.write(f'✅ Created grade: Form {i}')
        else:
            self.stdout.write(f'ℹ️ Grades already exist: {GradeLevel.objects.filter(school=school).count()} found')

        self.stdout.write(self.style.SUCCESS('✅ Initial setup complete!'))
        self.stdout.write('')
        self.stdout.write('📝 Next steps:')
        self.stdout.write('1. Login as admin')
        self.stdout.write('2. Go to School Setup (/school-setup/) to customize')
        self.stdout.write('3. Add/remove streams and grades as needed')
