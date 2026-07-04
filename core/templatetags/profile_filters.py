from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def profile_picture_url(profile, request):
    """Get the full URL for a profile picture"""
    if profile and profile.profile_picture:
        try:
            return request.build_absolute_uri(profile.profile_picture.url)
        except:
            return None
    return None

@register.filter
def profile_picture_html(user, request):
    """Generate HTML for profile picture with fallback"""
    if user and hasattr(user, 'teacher_profile') and user.teacher_profile.profile_picture:
        try:
            url = request.build_absolute_uri(user.teacher_profile.profile_picture.url)
            return mark_safe(f'<img src="{url}" alt="{user.username}" class="teacher-avatar" onerror="this.style.display=\'none\';">')
        except:
            pass
    initials = user.get_full_name()[:1].upper() if user.get_full_name() else user.username[:1].upper()
    return mark_safe(f'<span class="teacher-avatar-placeholder">{initials}</span>')
