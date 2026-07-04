from django.core.management.base import BaseCommand
from core.models import DisciplineCategory

class Command(BaseCommand):
    help = 'Seed discipline categories'

    def handle(self, *args, **options):
        categories = [
            ('ATTENDANCE', 'Attendance Offenses'),
            ('ACADEMIC', 'Academic Offenses'),
            ('UNIFORM', 'Uniform & Grooming Offenses'),
            ('CLASSROOM', 'Classroom Misconduct'),
            ('DISRESPECT', 'Disrespect & Insubordination'),
            ('BULLYING', 'Bullying & Harassment'),
            ('FIGHTING', 'Fighting & Violence'),
            ('THEFT', 'Theft & Dishonesty'),
            ('PROPERTY', 'School Property Offenses'),
            ('TECHNOLOGY', 'Technology & Phone Misuse'),
            ('SUBSTANCE', 'Substance Abuse Offenses'),
            ('SEXUAL', 'Sexual Misconduct'),
            ('RELATIONSHIP', 'Relationship & Coupling Offenses'),
            ('SECURITY', 'School Security Offenses'),
            ('MASS_INDISCIPLINE', 'Mass Indiscipline'),
            ('HEALTH_SAFETY', 'Health & Safety Violations'),
            ('COMMUNITY', 'Community & Social Misconduct'),
            ('EXAM', 'Examination & Assessment Offenses'),
            ('LEADERSHIP', 'Leadership & Prefect Misconduct'),
            ('TRANSPORT', 'Transport & Travel Offenses'),
            ('ENVIRONMENT', 'Environmental & Sanitation Offenses'),
            ('CRIMINAL', 'Criminal & Legal Offenses'),
        ]

        count = 0
        for key, name in categories:
            obj, created = DisciplineCategory.objects.get_or_create(
                key=key,
                defaults={
                    'name': name,
                    'description': f'{name} - Disciplinary offense category',
                    'default_rating': 'MODERATE',
                    'is_active': True,
                    'order': count
                }
            )
            if created:
                count += 1
                self.stdout.write(f'✅ Created: {name}')
            else:
                self.stdout.write(f'⚠️ Already exists: {name}')

        self.stdout.write(self.style.SUCCESS(f'✅ {count} categories created successfully!'))
