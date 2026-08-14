#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from core.models import DisciplineCategory

# All offense categories defined in your model
offenses = [
    {
        'key': 'ATTENDANCE',
        'name': 'Attendance Offenses',
        'description': 'Unexcused absences, chronic lateness, truancy, and skipping classes',
        'default_rating': 'MODERATE',
        'risk_weight': 3,
        'severity_level': 3
    },
    {
        'key': 'ACADEMIC',
        'name': 'Academic Offenses',
        'description': 'Cheating, plagiarism, falsifying records, and academic dishonesty',
        'default_rating': 'SERIOUS',
        'risk_weight': 4,
        'severity_level': 4
    },
    {
        'key': 'UNIFORM',
        'name': 'Uniform & Grooming Offenses',
        'description': 'Improper uniform, inappropriate dressing, or grooming violations',
        'default_rating': 'MINOR',
        'risk_weight': 1,
        'severity_level': 2
    },
    {
        'key': 'CLASSROOM',
        'name': 'Classroom Misconduct',
        'description': 'Disruptive behavior, talking during lessons, refusing to follow instructions',
        'default_rating': 'MODERATE',
        'risk_weight': 2,
        'severity_level': 3
    },
    {
        'key': 'DISRESPECT',
        'name': 'Disrespect & Insubordination',
        'description': 'Showing disrespect to teachers, staff, or fellow students',
        'default_rating': 'SERIOUS',
        'risk_weight': 4,
        'severity_level': 4
    },
    {
        'key': 'BULLYING',
        'name': 'Bullying & Harassment',
        'description': 'Physical, verbal, or cyberbullying; intimidation of other students',
        'default_rating': 'SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
    {
        'key': 'FIGHTING',
        'name': 'Fighting & Violence',
        'description': 'Physical altercations, assault, or violent behavior',
        'default_rating': 'VERY_SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
    {
        'key': 'THEFT',
        'name': 'Theft & Dishonesty',
        'description': 'Stealing school property or personal belongings of others',
        'default_rating': 'SERIOUS',
        'risk_weight': 4,
        'severity_level': 4
    },
    {
        'key': 'PROPERTY',
        'name': 'School Property Offenses',
        'description': 'Vandalism, damaging school property, or misuse of school facilities',
        'default_rating': 'SERIOUS',
        'risk_weight': 4,
        'severity_level': 4
    },
    {
        'key': 'TECHNOLOGY',
        'name': 'Technology & Phone Misuse',
        'description': 'Unauthorized phone use, inappropriate online activity, or tech policy violations',
        'default_rating': 'MODERATE',
        'risk_weight': 3,
        'severity_level': 3
    },
    {
        'key': 'SUBSTANCE',
        'name': 'Substance Abuse Offenses',
        'description': 'Use, possession, or distribution of alcohol, drugs, or tobacco on campus',
        'default_rating': 'VERY_SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
    {
        'key': 'SEXUAL',
        'name': 'Sexual Misconduct',
        'description': 'Sexual harassment, inappropriate behavior, or sexual assault',
        'default_rating': 'VERY_SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
    {
        'key': 'RELATIONSHIP',
        'name': 'Relationship & Coupling Offenses',
        'description': 'Inappropriate relationships, public displays of affection, or coupling violations',
        'default_rating': 'MODERATE',
        'risk_weight': 3,
        'severity_level': 3
    },
    {
        'key': 'SECURITY',
        'name': 'School Security Offenses',
        'description': 'Breach of school security, unauthorized access, or security violations',
        'default_rating': 'SERIOUS',
        'risk_weight': 4,
        'severity_level': 4
    },
    {
        'key': 'MASS_INDISCIPLINE',
        'name': 'Mass Indiscipline',
        'description': 'Group misconduct, strikes, protests, or mass violation of rules',
        'default_rating': 'VERY_SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
    {
        'key': 'HEALTH_SAFETY',
        'name': 'Health & Safety Violations',
        'description': 'Violations of health guidelines, safety protocols, or hygiene standards',
        'default_rating': 'MODERATE',
        'risk_weight': 3,
        'severity_level': 3
    },
    {
        'key': 'COMMUNITY',
        'name': 'Community & Social Misconduct',
        'description': 'Misbehavior in the community, social media misuse, or affecting school reputation',
        'default_rating': 'MODERATE',
        'risk_weight': 3,
        'severity_level': 3
    },
    {
        'key': 'EXAM',
        'name': 'Examination & Assessment Offenses',
        'description': 'Exam malpractice, unauthorized materials, or assessment violations',
        'default_rating': 'VERY_SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
    {
        'key': 'LEADERSHIP',
        'name': 'Leadership & Prefect Misconduct',
        'description': 'Misconduct by prefects, student leaders, or abuse of leadership position',
        'default_rating': 'SERIOUS',
        'risk_weight': 4,
        'severity_level': 4
    },
    {
        'key': 'TRANSPORT',
        'name': 'Transport & Travel Offenses',
        'description': 'Violations related to school transport, travel rules, or commuting offenses',
        'default_rating': 'MODERATE',
        'risk_weight': 3,
        'severity_level': 3
    },
    {
        'key': 'ENVIRONMENT',
        'name': 'Environmental & Sanitation Offenses',
        'description': 'Environmental violations, poor sanitation, or waste disposal offenses',
        'default_rating': 'MINOR',
        'risk_weight': 2,
        'severity_level': 2
    },
    {
        'key': 'CRIMINAL',
        'name': 'Criminal & Legal Offenses',
        'description': 'Serious criminal activities, legal violations, or police involvement',
        'default_rating': 'VERY_SERIOUS',
        'risk_weight': 5,
        'severity_level': 5
    },
]

print("=" * 60)
print("  SEEDING DISCIPLINE CATEGORIES (OFFENSES)")
print("=" * 60)

created = 0
existing = 0

for offense in offenses:
    obj, is_created = DisciplineCategory.objects.get_or_create(
        key=offense['key'],
        defaults={
            'name': offense['name'],
            'description': offense['description'],
            'default_rating': offense['default_rating'],
            'risk_weight': offense['risk_weight'],
            'severity_level': offense['severity_level'],
            'is_active': True
        }
    )
    
    if is_created:
        created += 1
        print(f"✅ Created: {offense['key']} - {offense['name']}")
    else:
        existing += 1
        print(f"⏭️  Already exists: {offense['key']} - {offense['name']}")

print("=" * 60)
print(f"📊 Summary:")
print(f"   ✅ New offenses created: {created}")
print(f"   ⏭️  Already existing: {existing}")
print(f"   📝 Total offenses in system: {DisciplineCategory.objects.count()}")
print("=" * 60)

# Show all offenses in the system
print("\n📋 All Offenses in System:")
print("-" * 60)
for cat in DisciplineCategory.objects.all().order_by('order', 'name'):
    print(f"   🔹 {cat.key}: {cat.name}")
    print(f"      Risk Weight: {cat.risk_weight} | Severity: {cat.severity_level} | Rating: {cat.default_rating}")
    print(f"      {cat.description[:60]}...")
    print("-" * 60)
