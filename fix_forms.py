import re
from pathlib import Path

file_path = Path("core/views.py")
content = file_path.read_text(encoding='utf-8')

# Find and replace the function
pattern = r'def _get_form_choices\(\):.*?(?=\n\ndef|\n@|\Z)'
replacement = '''def _get_form_choices():
    """Return grade-level form choices as objects (same pattern as streams)."""
    active_grades = GradeLevel.objects.filter(is_active=True).order_by("order", "name")
    if active_grades.exists():
        return active_grades
    default_choices = []
    for i, name in enumerate(['Form 1', 'Form 2', 'Form 3', 'Form 4'], 1):
        default_choices.append({
            'id': i,
            'name': name,
            'code': f'F{i}',
            'order': i,
            'is_active': True
        })
    return default_choices'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)
file_path.write_text(content, encoding='utf-8')
print("? Fixed _get_form_choices function")
