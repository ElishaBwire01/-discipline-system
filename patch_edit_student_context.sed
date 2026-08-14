/def edit_student/,/return render/ {
    /context = {/ {
        a\
        \    # Get grade levels for dropdown\
        \    school = School.objects.first()\
        \    grade_levels = GradeLevel.objects.filter(school=school, is_active=True).order_by('order') if school else []\
        a\
        \        'grade_levels': grade_levels,  # ADD THIS LINE
    }
}
