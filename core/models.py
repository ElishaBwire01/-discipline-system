from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.utils import timezone

# ============================================
# STREAM MODEL
# ============================================

class Stream(models.Model):
    STREAM_CHOICES = [
        ('MULUMBA', 'Mulumba'),
        ('KIZZA', 'Kizza'),
        ('LUKA', 'Luka'),
        ('GONZA', 'Gonza'),
        ('KAAGWA', 'Kaagwa'),
        ('MUKASA', 'Mukasa'),
        ('WASWA', 'Waswa'),
        ('MUWANGA', 'Muwanga'),
        ('KIZITO', 'Kizito'),
    ]
    name = models.CharField(max_length=20, choices=STREAM_CHOICES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


# ============================================
# TEACHER PROFILE MODEL
# ============================================

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
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_teachers'
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.assigned_stream}"

    def is_active_user(self):
        return self.is_approved and not self.is_suspended


# ============================================
# USER SESSION MODEL
# ============================================

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

    class Meta:
        ordering = ['-last_activity']


# ============================================
# DISCIPLINE CATEGORY MODEL
# ============================================

class DisciplineCategory(models.Model):
    """
    Structured offence categories that teachers pick when filing a report.
    Seeded via the management command:  python manage.py seed_categories
    """
    CATEGORY_KEYS = [
        ('ATTENDANCE',       'Attendance Offenses'),
        ('ACADEMIC',         'Academic Offenses'),
        ('UNIFORM',          'Uniform & Grooming Offenses'),
        ('CLASSROOM',        'Classroom Misconduct'),
        ('DISRESPECT',       'Disrespect & Insubordination'),
        ('BULLYING',         'Bullying & Harassment'),
        ('FIGHTING',         'Fighting & Violence'),
        ('THEFT',            'Theft & Dishonesty'),
        ('PROPERTY',         'School Property Offenses'),
        ('TECHNOLOGY',       'Technology & Phone Misuse'),
        ('SUBSTANCE',        'Substance Abuse Offenses'),
        ('SEXUAL',           'Sexual Misconduct'),
        ('RELATIONSHIP',     'Relationship & Coupling Offenses'),
        ('SECURITY',         'School Security Offenses'),
        ('MASS_INDISCIPLINE','Mass Indiscipline'),
        ('HEALTH_SAFETY',    'Health & Safety Violations'),
        ('COMMUNITY',        'Community & Social Misconduct'),
        ('EXAM',             'Examination & Assessment Offenses'),
        ('LEADERSHIP',       'Leadership & Prefect Misconduct'),
        ('TRANSPORT',        'Transport & Travel Offenses'),
        ('ENVIRONMENT',      'Environmental & Sanitation Offenses'),
        ('CRIMINAL',         'Criminal & Legal Offenses'),
    ]

    key = models.CharField(max_length=30, choices=CATEGORY_KEYS, unique=True)
    name = models.CharField(max_length=120)          # human-readable label
    description = models.TextField(blank=True)       # optional detail shown in the form
    default_rating = models.CharField(
        max_length=20,
        choices=[
            ('VERY_MINOR', 'Very Minor'),
            ('MINOR', 'Minor'),
            ('MODERATE', 'Moderate'),
            ('SERIOUS', 'Serious'),
            ('VERY_SERIOUS', 'Very Serious'),
        ],
        default='MODERATE',
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0, help_text='Display order')

    class Meta:
        verbose_name_plural = 'Discipline Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


# ============================================
# STUDENT MODEL
# ============================================

class Student(models.Model):
    FORM_CHOICES = [(f'Form {i}', f'Form {i}') for i in range(1, 11)]

    admission_number = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='students')
    form = models.CharField(max_length=10, choices=FORM_CHOICES)
    year = models.IntegerField(default=timezone.now().year)
    optional_notes = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='student_pics/', null=True, blank=True)
    risk_score = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_students'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['name']),
            models.Index(fields=['stream', 'form']),
            models.Index(fields=['risk_score']),
        ]

    def __str__(self):
        return f"{self.name} ({self.admission_number})"

    def update_risk_score(self):
        total = self.reports.aggregate(total=Sum('points'))['total'] or 0
        self.risk_score = min(total, 100)
        self.save(update_fields=['risk_score', 'updated_at'])
        return self.risk_score

    @property
    def is_critical(self):
        return self.risk_score >= 60

    @property
    def risk_level(self):
        if self.risk_score >= 60:
            return 'CRITICAL'
        elif self.risk_score >= 30:
            return 'WARNING'
        return 'GOOD'

    @property
    def total_reports(self):
        return self.reports.count()


# ============================================
# DISCIPLINE REPORT MODEL
# ============================================

class DisciplineReport(models.Model):
    RATING_CHOICES = [
        ('VERY_MINOR',  'Very Minor'),
        ('MINOR',       'Minor'),
        ('MODERATE',    'Moderate'),
        ('SERIOUS',     'Serious'),
        ('VERY_SERIOUS','Very Serious'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')

    # ---- structured category (required) ----
    category = models.ForeignKey(
        DisciplineCategory, on_delete=models.PROTECT,
        related_name='reports',
        help_text='Select the offence category'
    )
    # Kept for quick access / legacy compatibility
    category_name = models.CharField(max_length=200, editable=False)

    # ---- free-text details ----
    comments = models.TextField(blank=True, help_text='Describe the specific incident')

    rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='MODERATE')
    points = models.IntegerField(default=10)
    reported_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['reported_at']),
            models.Index(fields=['student', 'reported_at']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.category_name} by {self.reported_by.username}"

    def save(self, *args, **kwargs):
        # Mirror category name for quick display
        self.category_name = self.category.name

        # Auto-calculate points based on rating
        rating_points = {
            'VERY_MINOR':  5,
            'MINOR':       10,
            'MODERATE':    20,
            'SERIOUS':     30,
            'VERY_SERIOUS':40,
        }
        self.points = rating_points.get(self.rating, 10)
        super().save(*args, **kwargs)
        self.student.update_risk_score()
        self._notify_class_teacher()
        if self.student.total_reports >= 20:
            self._notify_admin()

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
                title=f'⚠️ CRITICAL: {self.student.name} - {self.student.total_reports} Reports',
                message=(
                    f'Student: {self.student.name} (ID: {self.student.admission_number})\n'
                    f'Total Reports: {self.student.total_reports}\n'
                    f'Risk Score: {self.student.risk_score}%\n'
                    f'Last Report: {self.category_name} by '
                    f'{self.reported_by.get_full_name() or self.reported_by.username}'
                ),
                notification_type='critical',
                student=self.student,
            )
            notification.target_users.set(admins)


# ============================================
# NOTIFICATION MODEL
# ============================================

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('critical', 'Critical Alert'),
        ('warning',  'Warning'),
        ('info',     'Information'),
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


# ============================================
# PASSWORD RESET MODEL
# ============================================

class PasswordReset(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('approved',  'Approved'),
        ('completed', 'Completed'),
        ('rejected',  'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_resets'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    new_password = models.CharField(max_length=128, blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.requested_at}"

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['requested_at']),
        ]


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_admin_notification(title, message, notification_type='info', student=None):
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




