from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.utils import timezone

# ============================================
# SCHOOL SETUP MODELS
# ============================================

class School(models.Model):
    name = models.CharField(max_length=200, help_text="School name")
    short_name = models.CharField(max_length=50, blank=True)
    motto = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='school/', null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    current_year = models.IntegerField(default=timezone.now().year)
    terms_per_year = models.IntegerField(default=3, choices=[(1, '1 Term'), (2, '2 Terms'), (3, '3 Terms'), (4, '4 Terms')])
    allow_teacher_registration = models.BooleanField(default=True)
    require_teacher_approval = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "School Settings"
    
    def __str__(self):
        return self.name


class GradeLevel(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grades')
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['school', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"


class AcademicTerm(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=50)
    term_number = models.IntegerField()
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    def get_duration_days(self):
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days
        return 0
    
    def get_duration_weeks(self):
        days = self.get_duration_days()
        return round(days / 7, 1)
    
    def get_duration_months(self):
        days = self.get_duration_days()
        return round(days / 30.44, 1)
    
    def get_duration_display(self):
        days = self.get_duration_days()
        if days == 0:
            return "0 days"
        elif days < 7:
            return f"{days} day{'s' if days != 1 else ''}"
        elif days < 30:
            weeks = self.get_duration_weeks()
            return f"{weeks} week{'s' if weeks != 1 else ''}"
        elif days < 365:
            months = self.get_duration_months()
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            return f"{days} days"
    
    class Meta:
        ordering = ['-year', '-term_number']
        unique_together = ['school', 'year', 'term_number']
    
    def __str__(self):
        return f"{self.name} ({self.year})"


class Stream(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='streams', null=True, blank=True)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['school', 'name']
    
    def __str__(self):
        return self.name


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    assigned_stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_form = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    has_chosen_stream = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)
    suspended_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_teachers')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.assigned_stream}"
    
    def is_active_user(self):
        return self.is_approved and not self.is_suspended


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class DisciplineCategory(models.Model):
    CATEGORY_KEYS = [
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
    
    key = models.CharField(max_length=30, choices=CATEGORY_KEYS, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    default_rating = models.CharField(max_length=20, choices=[
        ('VERY_MINOR', 'Very Minor'),
        ('MINOR', 'Minor'),
        ('MODERATE', 'Moderate'),
        ('SERIOUS', 'Serious'),
        ('VERY_SERIOUS', 'Very Serious'),
    ], default='MODERATE')
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    # AI-specific fields for better risk calculation
    risk_weight = models.PositiveSmallIntegerField(
        default=1,
        choices=[(1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')],
        help_text="Weight multiplier for risk calculation (1-5)"
    )
    severity_level = models.PositiveSmallIntegerField(
        default=3,
        choices=[(1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')],
        help_text="Severity level of the offense"
    )
    
    class Meta:
        verbose_name_plural = 'Discipline Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_risk_multiplier(self):
        """Get risk multiplier based on severity level"""
        return self.severity_level


class Student(models.Model):
    FORM_CHOICES = [(f'Form {i}', f'Form {i}') for i in range(1, 11)]
    
    RISK_LEVEL_CHOICES = [
        ('GOOD', 'Good'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]
    
    ACADEMIC_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRANSFERRED', 'Transferred'),
        ('DROPPED', 'Dropped Out'),
        ('GRADUATED', 'Graduated'),
    ]
    
    admission_number = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='students')
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    form = models.CharField(max_length=10, choices=FORM_CHOICES)
    year = models.IntegerField(default=timezone.now().year)
    optional_notes = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='student_pics/', null=True, blank=True)
    
    # Risk Management Fields
    risk_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='GOOD',
        db_index=True
    )
    
    # AI-specific fields for advanced analytics
    ai_risk_factors = models.JSONField(default=dict, blank=True, null=True)
    ai_last_analysis = models.DateTimeField(null=True, blank=True)
    intervention_count = models.PositiveIntegerField(default=0)
    last_incident_date = models.DateTimeField(null=True, blank=True)
    
    # Student Status Fields
    enrollment_date = models.DateField(null=True, blank=True)
    academic_status = models.CharField(
        max_length=20,
        choices=ACADEMIC_STATUS_CHOICES,
        default='ACTIVE'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_students')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['name']),
            models.Index(fields=['stream', 'form']),
            models.Index(fields=['risk_score']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['last_incident_date']),
            models.Index(fields=['academic_status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.admission_number})"
    
    def update_risk_score(self):
        """Update risk score based on all reports"""
        total = self.reports.aggregate(total=Sum('points'))['total'] or 0
        self.risk_score = min(total, 100)
        self.update_risk_level()
        self.save(update_fields=['risk_score', 'risk_level', 'updated_at'])
        return self.risk_score
    
    def update_risk_level(self):
        """Update risk level based on risk score"""
        if self.risk_score >= 60:
            self.risk_level = 'CRITICAL'
        elif self.risk_score >= 30:
            self.risk_level = 'WARNING'
        else:
            self.risk_level = 'GOOD'
    
    def update_last_incident(self):
        """Update last incident date from latest report"""
        latest_report = self.reports.order_by('-reported_at').first()
        if latest_report:
            self.last_incident_date = latest_report.reported_at
            self.save(update_fields=['last_incident_date'])
    
    def increment_intervention(self):
        """Increment intervention counter"""
        self.intervention_count += 1
        self.save(update_fields=['intervention_count'])
    
    def save(self, *args, **kwargs):
        """Override save to auto-update risk level"""
        self.update_risk_level()
        super().save(*args, **kwargs)
    
    @property
    def is_critical(self):
        return self.risk_score >= 60
    
    @property
    def total_reports(self):
        return self.reports.count()
    
    @property
    def days_since_last_incident(self):
        """Calculate days since last incident"""
        if self.last_incident_date:
            delta = timezone.now() - self.last_incident_date
            return delta.days
        return None
    
    @property
    def risk_trend(self):
        """Determine risk trend based on recent reports"""
        recent_reports = self.reports.order_by('-reported_at')[:5]
        if recent_reports.count() < 2:
            return 'stable'
        
        # Compare points from oldest to newest
        points = [r.points for r in recent_reports]
        if points[0] > points[-1]:
            return 'improving'
        elif points[0] < points[-1]:
            return 'worsening'
        return 'stable'


class DisciplineReport(models.Model):
    RATING_CHOICES = [
        ('VERY_MINOR', 'Very Minor'),
        ('MINOR', 'Minor'),
        ('MODERATE', 'Moderate'),
        ('SERIOUS', 'Serious'),
        ('VERY_SERIOUS', 'Very Serious'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    category = models.ForeignKey(DisciplineCategory, on_delete=models.PROTECT, related_name='reports')
    category_name = models.CharField(max_length=200, editable=False)
    comments = models.TextField(blank=True)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='MODERATE')
    points = models.IntegerField(default=10)
    reported_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['reported_at']),
            models.Index(fields=['student', 'reported_at']),
            models.Index(fields=['rating']),
            models.Index(fields=['points']),
        ]
    
    def __str__(self):
        return f"{self.student.name} - {self.category_name} by {self.reported_by.username}"
    
    def save(self, *args, **kwargs):
        self.category_name = self.category.name
        rating_points = {
            'VERY_MINOR': 5,
            'MINOR': 10,
            'MODERATE': 20,
            'SERIOUS': 30,
            'VERY_SERIOUS': 40,
        }
        # Apply category risk weight multiplier
        base_points = rating_points.get(self.rating, 10)
        self.points = base_points * self.category.risk_weight
        super().save(*args, **kwargs)
        self.student.update_risk_score()
        self.student.update_last_incident()
        self._notify_class_teacher()
        if self.student.total_reports >= 20 or self.student.risk_score >= 60:
            self._notify_admin()
        self._create_ai_analysis()
    
    def _notify_class_teacher(self):
        class_teachers = User.objects.filter(
            teacher_profile__assigned_stream=self.student.stream,
            groups__name='ClassTeacher'
        )
        if class_teachers.exists():
            notification = Notification.objects.create(
                title=f'📝 New Report: {self.student.name}',
                message=(
                    f'Student: {self.student.name} (ID: {self.student.admission_number})\n'
                    f'Category: {self.category_name}\n'
                    f'Points: +{self.points}\n'
                    f'Rating: {self.get_rating_display()}\n'
                    f'Risk Level: {self.student.risk_level}\n'
                    f'Reported by: {self.reported_by.get_full_name() or self.reported_by.username}'
                ),
                notification_type='warning',
                student=self.student,
            )
            notification.target_users.set(class_teachers)
    
    def _notify_admin(self):
        admins = User.objects.filter(is_superuser=True)
        if admins.exists():
            notification = Notification.objects.create(
                title=f'⚠️ CRITICAL ALERT: {self.student.name}',
                message=(
                    f'Student: {self.student.name} (ID: {self.student.admission_number})\n'
                    f'Total Reports: {self.student.total_reports}\n'
                    f'Risk Score: {self.student.risk_score}%\n'
                    f'Risk Level: {self.student.risk_level}\n'
                    f'Last Report: {self.category_name} by '
                    f'{self.reported_by.get_full_name() or self.reported_by.username}\n'
                    f'Days since last incident: {self.student.days_since_last_incident or "N/A"}'
                ),
                notification_type='critical',
                student=self.student,
            )
            notification.target_users.set(admins)
            notification.save()
    
    def _create_ai_analysis(self):
        """Create AI analysis for the student"""
        from django.utils import timezone
        import json
        
        student = self.student
        analysis = {
            'last_analysis': timezone.now().isoformat(),
            'total_reports': student.total_reports,
            'risk_score': student.risk_score,
            'risk_level': student.risk_level,
            'recent_trend': student.risk_trend,
            'days_since_incident': student.days_since_last_incident,
            'intervention_count': student.intervention_count,
            'category_breakdown': list(
                student.reports.values('category__name')
                .annotate(count=models.Count('id'))
                .order_by('-count')
            )
        }
        student.ai_risk_factors = analysis
        student.ai_last_analysis = timezone.now()
        student.save(update_fields=['ai_risk_factors', 'ai_last_analysis'])


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('critical', 'Critical Alert'),
        ('warning', 'Warning'),
        ('info', 'Information'),
        ('success', 'Success'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)
    target_users = models.ManyToManyField(User, related_name='notifications')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.notification_type}"
    
    def mark_read(self, user):
        self.target_users.remove(user)
        if not self.target_users.exists():
            self.is_read = True
            self.save(update_fields=['is_read'])


class PasswordReset(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_resets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    new_password = models.CharField(max_length=128, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['requested_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.requested_at}"


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_admin_notification(title, message, notification_type='info', student=None):
    """Create a notification for all admin users"""
    admins = User.objects.filter(is_superuser=True)
    if admins.exists():
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            student=student,
        )
        notification.target_users.set(admins)
        return notification
    return None


def create_user_notification(user, title, message, notification_type='info', student=None):
    """Create a notification for a specific user"""
    notification = Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        student=student,
    )
    notification.target_users.add(user)
    if notification_type == 'critical':
        create_admin_notification(f'⚠️ {title}', message, 'critical', student)
    return notification


def bulk_update_risk_levels():
    """Utility function to update all students' risk levels"""
    from django.db import transaction
    
    with transaction.atomic():
        for student in Student.objects.all():
            student.update_risk_level()
            student.save(update_fields=['risk_level'])
    print(f"✅ Updated risk levels for {Student.objects.count()} students")


def calculate_risk_trend(student):
    """Calculate risk trend for a student"""
    recent_reports = student.reports.order_by('-reported_at')[:5]
    if recent_reports.count() < 2:
        return 'stable'
    
    points = [r.points for r in recent_reports]
    if points[0] > points[-1]:
        return 'improving'
    elif points[0] < points[-1]:
        return 'worsening'
    return 'stable'