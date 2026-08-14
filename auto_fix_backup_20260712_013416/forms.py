  # core/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, DisciplineReport, DisciplineCategory, Stream, GradeLevel


class StudentForm(forms.ModelForm):
    """Form for creating and editing students."""

    class Meta:
        model = Student
        fields = [
            "admission_number",
            "name",
            "stream",
            "form",
            "year",
            "optional_notes",
        ]
        widgets = {
            "admission_number": forms.TextInput(
                attrs={
                    "class": "form-control-modern",
                    "placeholder": "Enter admission number",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control-modern",
                    "placeholder": "Enter full name",
                }
            ),
            "stream": forms.Select(
                attrs={
                    "class": "form-control-modern",
                    "data-placeholder": "Select stream",
                }
            ),
            "form": forms.Select(
                attrs={
                    "class": "form-control-modern",
                    "data-placeholder": "Select form",
                }
            ),
            "year": forms.NumberInput(
                attrs={
                    "class": "form-control-modern",
                    "placeholder": "Year",
                }
            ),
            "optional_notes": forms.Textarea(
                attrs={
                    "class": "form-control-modern",
                    "rows": 3,
                    "placeholder": "Optional notes about the student...",
                }
            ),
        }
        labels = {
            "admission_number": "Admission Number",
            "name": "Full Name",
            "stream": "Stream/Class",
            "form": "Form/Grade",
            "year": "Academic Year",
            "optional_notes": "Notes",
        }
        help_texts = {
            "admission_number": "Unique student identifier",
            "stream": "Select the student's stream/class",
            "form": "Select the student's form/grade level",
        }
        error_messages = {
            "admission_number": {
                "unique": "A student with this admission number already exists.",
                "required": "Admission number is required.",
            },
            "name": {
                "required": "Student name is required.",
                "max_length": "Student name cannot exceed 200 characters.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show active streams
        self.fields["stream"].queryset = Stream.objects.filter(is_active=True).order_by(
            "name"
        )
        self.fields["stream"].empty_label = "-- Select Stream --"

        # Only show active grade levels for form choices
        active_grades = GradeLevel.objects.filter(is_active=True).order_by(
            "order", "name"
        )
        if active_grades.exists():
            self.fields["form"].choices = [(g.name, g.name) for g in active_grades]
        else:
            # Fallback to default FORM_CHOICES
            self.fields["form"].choices = Student.FORM_CHOICES

        # Set default year if not provided
        if not self.instance.year:
            self.fields["year"].initial = Student._meta.get_field("year").default

    def clean_admission_number(self):
        """Validate admission number format."""
        admission = self.cleaned_data.get("admission_number")
        if admission:
            admission = admission.strip().upper()
            # Check for existing student with same admission number
            if (
                Student.objects.filter(admission_number=admission)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError(
                    "A student with this admission number already exists."
                )
            # Validate format (alphanumeric, 4-20 chars)
            if not re.match(r"^[A-Za-z0-9]{4,20}$", admission):
                raise ValidationError(
                    "Admission number must be 4-20 alphanumeric characters."
                )
        return admission

    def clean_name(self):
        """Validate student name."""
        name = self.cleaned_data.get("name")
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("Student name must be at least 2 characters.")
        return name

    def clean_year(self):
        """Validate year."""
        year = self.cleaned_data.get("year")
        if year:
            from django.utils import timezone

            current_year = timezone.now().year
            if year < 2000 or year > current_year + 5:
                raise ValidationError(
                    f"Year must be between 2000 and {current_year + 5}."
                )
        return year


class DisciplineReportForm(forms.ModelForm):
    """
    Report form used by both Teachers and Class Teachers.
    The category field renders a grouped <select> organised by the
    DisciplineCategory model (22 standard groups + Prefect Misconduct).
    The comments field lets the teacher describe the specific incident.
    """

    class Meta:
        model = DisciplineReport
        fields = ["student", "category", "rating", "comments"]
        widgets = {
            "student": forms.Select(
                attrs={
                    "class": "form-control-modern",
                    "data-placeholder": "Search student...",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control-modern",
                    "data-placeholder": "— Select offence category —",
                }
            ),
            "rating": forms.Select(
                attrs={
                    "class": "form-control-modern",
                }
            ),
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control-modern",
                    "rows": 3,
                    "placeholder": "Describe the specific incident in detail…",
                }
            ),
        }
        labels = {
            "student": "Student",
            "category": "Offence Category",
            "rating": "Severity Rating",
            "comments": "Incident Description / Comments",
        }
        help_texts = {
            "category": "Select the appropriate category for this offense",
            "rating": "Select the severity level of the offense",
        }
        error_messages = {
            "student": {
                "required": "Please select a student.",
            },
            "category": {
                "required": "Please select an offence category.",
            },
            "comments": {
                "required": "Please provide a description of the incident.",
            },
        }

    def __init__(self, *args, **kwargs):
        # Allow passing a filtered student queryset
        student_queryset = kwargs.pop("student_queryset", None)
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # Only show active categories, ordered by display order
        self.fields["category"].queryset = DisciplineCategory.objects.filter(
            is_active=True
        ).order_by("order", "name")
        self.fields["category"].empty_label = "— Select offence category —"

        # Filter students if a queryset is provided
        if student_queryset is not None:
            self.fields["student"].queryset = student_queryset
        else:
            self.fields["student"].queryset = Student.objects.filter(
                is_active=True
            ).order_by("name")

        self.fields["student"].empty_label = "-- Select Student --"

        # Set default rating
        if not self.instance.pk:
            self.fields["rating"].initial = "MODERATE"

        # Store user for additional validation
        self._user = user

    def clean_comments(self):
        """Validate comments."""
        comments = self.cleaned_data.get("comments")
        if comments:
            comments = comments.strip()
            if len(comments) < 3:
                raise ValidationError(
                    "Please provide a more detailed description (at least 3 characters)."
                )
        return comments

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        category = cleaned_data.get("category")
        rating = cleaned_data.get("rating")

        # If rating is VERY_SERIOUS, suggest admin notification
        if rating == "VERY_SERIOUS" and self._user and not self._user.is_superuser:
            # This is just a warning, not a validation error
            pass

        return cleaned_data


class BulkUploadForm(forms.Form):
    """
    Form for bulk uploading students via CSV/text input.
    """

    csv_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control-modern",
                "rows": 10,
                "placeholder": (
                    "name,admission_number,stream,form,year,notes\n"
                    "John Doe,ADM001,MULUMBA,Form 1,2026,Good student\n"
                    "Jane Smith,ADM002,GONZA,Form 2,2026,Needs attention"
                ),
            }
        ),
        label="Student Data (CSV format)",
        help_text="Enter student data in CSV format: name, admission_number, stream, form, year, notes",
        required=True,
        error_messages={
            "required": "Please enter student data.",
        },
    )

    def clean_csv_data(self):
        """Parse and validate CSV data."""
        data = self.cleaned_data.get("csv_data", "").strip()

        if not data:
            raise ValidationError("Please enter student data.")

        lines = data.strip().split("\n")
        parsed_data = []
        errors = []

        # Expected headers
        expected_headers = [
            "name",
            "admission_number",
            "stream",
            "form",
            "year",
            "notes",
        ]

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines
            if not line.strip():
                continue

            # Parse CSV line (simple split by comma)
            parts = line.split(",")
            if len(parts) < 4:
                errors.append(
                    f"Line {line_num}: Expected at least 4 columns (name, admission, stream, form)"
                )
                continue

            # Extract values
            name = parts[0].strip() if len(parts) > 0 else ""
            admission = parts[1].strip() if len(parts) > 1 else ""
            stream = parts[2].strip() if len(parts) > 2 else ""
            form = parts[3].strip() if len(parts) > 3 else ""
            year = parts[4].strip() if len(parts) > 4 else ""
            notes = parts[5].strip() if len(parts) > 5 else ""

            # Validate
            if not name:
                errors.append(f"Line {line_num}: Name is required.")
                continue

            if not admission:
                errors.append(f"Line {line_num}: Admission number is required.")
                continue

            if not stream:
                errors.append(f"Line {line_num}: Stream is required.")
                continue

            if not form:
                errors.append(f"Line {line_num}: Form is required.")
                continue

            # Validate year
            try:
                year_int = int(year) if year else None
                if year and (year_int < 2000 or year_int > 2030):
                    errors.append(
                        f"Line {line_num}: Year must be between 2000 and 2030."
                    )
                    continue
            except ValueError:
                errors.append(f"Line {line_num}: Year must be a valid number.")
                continue

            parsed_data.append(
                {
                    "name": name,
                    "admission_number": admission,
                    "stream": stream,
                    "form": form,
                    "year": year_int or 2026,
                    "notes": notes,
                }
            )

        if errors:
            raise ValidationError(f"Errors found in CSV data:\n" + "\n".join(errors))

        if not parsed_data:
            raise ValidationError("No valid student data found.")

        return parsed_data

    def save(self, user=None):
        """Process and save the uploaded students."""
        data = self.cleaned_data.get("csv_data", [])
        results = {
            "added": 0,
            "existing": 0,
            "errors": [],
        }

        for student_data in data:
            try:
                # Get or create stream
                stream_name = student_data["stream"]
                stream, created = Stream.objects.get_or_create(
                    name=stream_name, defaults={"is_active": True}
                )

                # Get or create grade level
                grade_name = student_data["form"]
                grade, created = GradeLevel.objects.get_or_create(
                    name=grade_name,
                    defaults={
                        "code": grade_name[:3].upper(),
                        "order": 0,
                        "is_active": True,
                    },
                )

                # Create student
                student, created = Student.objects.get_or_create(
                    admission_number=student_data["admission_number"],
                    defaults={
                        "name": student_data["name"],
                        "stream": stream,
                        "grade_level": grade,
                        "form": student_data["form"],
                        "year": student_data["year"],
                        "optional_notes": student_data["notes"],
                        "created_by": user,
                        "is_active": True,
                    },
                )

                if created:
                    results["added"] += 1
                else:
                    results["existing"] += 1

            except Exception as e:
                results["errors"].append(
                    f"{student_data.get('admission_number', 'Unknown')}: {str(e)}"
                )

        return results


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control-modern"}),
            "last_name": forms.TextInput(attrs={"class": "form-control-modern"}),
            "email": forms.EmailInput(attrs={"class": "form-control-modern"}),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
        }


class ChangePasswordForm(forms.Form):
    """Form for changing password."""

    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control-modern",
                "placeholder": "Enter current password",
            }
        ),
        label="Current Password",
        required=True,
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control-modern",
                "placeholder": "Enter new password (min 8 characters)",
            }
        ),
        label="New Password",
        required=True,
        min_length=8,
        help_text="Password must be at least 8 characters.",
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control-modern",
                "placeholder": "Confirm new password",
            }
        ),
        label="Confirm Password",
        required=True,
    )

    def clean(self):
        """Validate that passwords match."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("New passwords do not match.")

        return cleaned_data


class ResetPasswordForm(forms.Form):
    """Form for resetting password (admin)."""

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control-modern",
                "placeholder": "Enter new password",
            }
        ),
        label="New Password",
        required=True,
        min_length=8,
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control-modern",
                "placeholder": "Confirm new password",
            }
        ),
        label="Confirm Password",
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


class NotificationForm(forms.ModelForm):
    """Form for creating notifications."""

    class Meta:
        model = Notification
        fields = ["title", "message", "notification_type", "student", "target_users"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control-modern"}),
            "message": forms.Textarea(
                attrs={"class": "form-control-modern", "rows": 4}
            ),
            "notification_type": forms.Select(attrs={"class": "form-control-modern"}),
            "student": forms.Select(attrs={"class": "form-control-modern"}),
            "target_users": forms.SelectMultiple(
                attrs={"class": "form-control-modern"}
            ),
        }


import re  # For validation in StudentForm
