from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_initials(name):
    """Get initials from a name."""
    if not name:
        return ""
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

@register.filter
def avatar_class(user):
    """Return the avatar class for a user."""
    if not user:
        return "teacher-avatar-placeholder"
    if hasattr(user, 'teacher_profile') and user.teacher_profile.profile_picture:
        return "has-avatar"
    return "teacher-avatar-placeholder"

@register.filter
def get_avatar(user):
    """Get the avatar HTML for a user."""
    if not user:
        return '<span class="teacher-avatar-placeholder">??</span>'

    # Check if user has a profile picture
    if hasattr(user, 'teacher_profile') and user.teacher_profile.profile_picture:
        try:
            return mark_safe(f'<img src="{user.teacher_profile.profile_picture.url}" alt="{user.get_full_name()}" class="avatar-img">')
        except:
            pass

    # Fallback to initials
    initials = get_initials(user.get_full_name() or user.username)
    return mark_safe(f'<span class="teacher-avatar-placeholder">{initials}</span>')
