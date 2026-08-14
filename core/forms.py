from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, Stream, DisciplineReport, DisciplineCategory, School, GradeLevel

class StudentForm(forms.ModelForm):
    """Form for creating and editing students."""
    
    class Meta:
        model = Student
        fields = ['admission_number', 'name', 'stream', 'grade_level', 'form', 'year', 'optional_notes']
        widgets = {
            'admission_number': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Enter admission number',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Enter full name',
            }),
            'stream': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select stream',
            }),
            'grade_level': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select grade level',
            }),
            'form': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select form',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control-modern',
                'placeholder': 'Year',
            }),
            'optional_notes': forms.Textarea(attrs={
                'class': 'form-control-modern',
                'rows': 3,
                'placeholder': 'Optional notes about the student...',
            }),
        }
        labels = {
            'admission_number': 'Admission Number',
            'name': 'Student Name',
            'stream': 'Stream/Class',
            'grade_level': 'Grade Level',
            'form': 'Form',
            'year': 'Academic Year',
            'optional_notes': 'Optional Notes',
        }
        help_texts = {
            'admission_number': 'Unique student identifier (e.g., 2024-001)',
            'stream': 'Select the student\'s stream/class',
            'grade_level': 'Select the student\'s grade level',
            'form': 'Select the student\'s form',
            'year': 'Academic year (e.g., 2024)',
            'optional_notes': 'Any additional information about the student',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter streams to only active ones
        self.fields['stream'].queryset = Stream.objects.filter(is_active=True).order_by('name')
        # Filter grade_level to only active ones
        self.fields['grade_level'].queryset = GradeLevel.objects.filter(is_active=True).order_by('order')
        # Form choices are defined in the model

class DisciplineReportForm(forms.ModelForm):
    """Form for creating discipline reports."""
    
    class Meta:
        model = DisciplineReport
        fields = ['student', 'category', 'rating', 'comments']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select student',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select offence category',
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control-modern',
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control-modern',
                'rows': 4,
                'placeholder': 'Enter detailed report comments...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = DisciplineCategory.objects.filter(is_active=True).order_by('order', 'name')
