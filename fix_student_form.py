#!/usr/bin/env python3
import re

with open('core/forms.py', 'r') as f:
    content = f.read()

# Find the StudentForm class and add grade field
if 'class StudentForm' in content:
    # Add grade field to the fields list
    fields_line = "fields = ['admission_number', 'name', 'stream', 'form', 'year', 'optional_notes']"
    new_fields_line = "fields = ['admission_number', 'name', 'stream', 'grade', 'form', 'year', 'optional_notes']"
    content = content.replace(fields_line, new_fields_line)
    
    # Add grade widget after form widget
    form_widget = """            'form': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select form',
            }),
            'year': forms.NumberInput(attrs={"""
    
    new_form_widget = """            'form': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select form',
            }),
            'grade': forms.Select(attrs={
                'class': 'form-control-modern',
                'data-placeholder': 'Select grade',
            }),
            'year': forms.NumberInput(attrs={"""
    
    content = content.replace(form_widget, new_form_widget)
    
    # Update labels
    labels_section = """        labels = {
            'admission_number': 'Admission Number',
            'name': 'Student Name',
            'stream': 'Stream/Class',
            'form': 'Form/Grade',
            'year': 'Academic Year',
            'optional_notes': 'Optional Notes',
        }"""
    
    new_labels = """        labels = {
            'admission_number': 'Admission Number',
            'name': 'Student Name',
            'stream': 'Stream/Class',
            'grade': 'Grade Level',
            'form': 'Form',
            'year': 'Academic Year',
            'optional_notes': 'Optional Notes',
        }"""
    
    content = content.replace(labels_section, new_labels)
    
    with open('core/forms.py', 'w') as f:
        f.write(content)
    
    print("✅ StudentForm updated with grade field!")
else:
    print("❌ StudentForm class not found")
