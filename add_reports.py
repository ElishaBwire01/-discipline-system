from core.models import Student, DisciplineCategory, DisciplineReport
from django.contrib.auth.models import User
import random

def add_sample_reports():
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found!")
        return
    
    # Get students
    students = Student.objects.filter(is_active=True)
    if students.count() == 0:
        print("❌ No students found!")
        return
    
    # Get categories
    categories = DisciplineCategory.objects.filter(is_active=True)
    if categories.count() == 0:
        print("❌ No categories found! Please run: python manage.py seed_categories")
        return
    
    ratings = ['VERY_MINOR', 'MINOR', 'MODERATE', 'SERIOUS', 'VERY_SERIOUS']
    ratings_weights = [3, 4, 3, 2, 1]  # Weighted random
    
    reports_added = 0
    
    # Add 3-5 reports for random students
    for i in range(1, 16):
        student = random.choice(students)
        category = random.choice(categories)
        rating = random.choices(ratings, weights=ratings_weights, k=1)[0]
        
        comments = [
            "Student was late to class",
            "Disruptive behavior during lesson",
            "Improper uniform worn to school",
            "Talking back to teacher",
            "Bullying other students",
            "Phone usage during class",
            "Not completing homework",
            "Fighting with another student",
            "Cheating on test",
            "Skipping class"
        ]
        
        try:
            report = DisciplineReport.objects.create(
                student=student,
                reported_by=admin,
                category=category,
                comments=random.choice(comments),
                rating=rating
            )
            reports_added += 1
            print(f"✅ Report {i}: {student.name} - {category.name} ({rating})")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ {reports_added} reports added successfully!")
    print(f"📊 Total reports: {DisciplineReport.objects.count()}")

if __name__ == "__main__":
    add_sample_reports()
