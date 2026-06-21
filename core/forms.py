from django import forms
from django.contrib.auth.models import User
from .models import Student, DisciplineReport, DisciplineCategory, Stream


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_number', 'name', 'stream', 'form', 'year', 'optional_notes']
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name':             forms.TextInput(attrs={'class': 'form-control'}),
            'stream':           forms.Select(attrs={'class': 'form-control'}),
            'form':             forms.Select(attrs={'class': 'form-control'}),
            'year':             forms.NumberInput(attrs={'class': 'form-control'}),
            'optional_notes':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DisciplineReportForm(forms.ModelForm):
    """
    Report form used by both Teachers and Class Teachers.
    The category field renders a grouped <select> organised by the
    DisciplineCategory model (22 standard groups + Prefect Misconduct).
    The comments field lets the teacher describe the specific incident.
    """

    class Meta:
        model = DisciplineReport
        fields = ['student', 'category', 'rating', 'comments']
        widgets = {
            'student':  forms.Select(attrs={'class': 'form-control select2'}),
            'category': forms.Select(attrs={'class': 'form-control select2',
                                            'data-placeholder': '— Select offence category —'}),
            'rating':   forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the specific incident in detail…',
            }),
        }
        labels = {
            'category': 'Offence Category',
            'comments': 'Incident Description / Comments',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories, ordered by display order
        self.fields['category'].queryset = DisciplineCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = '— Select offence category —'


class BulkUploadForm(forms.Form):
    csv_data = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 10,
        'placeholder': (
            'name,admission_number,stream,form,year,notes\n'
            'John Doe,ADM001,MULUMBA,Form 1,2025,Good student'
        ),
    }))