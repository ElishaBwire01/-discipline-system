from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_only(view_func):
    """Decorator to allow only admin users"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            raise PermissionDenied("Admin access required")
        return view_func(request, *args, **kwargs)
    return wrapper

def class_teacher_only(view_func):
    """Decorator to allow only class teachers"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.groups.filter(name='ClassTeacher').exists()):
            raise PermissionDenied("Class Teacher access required")
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_only(view_func):
    """Decorator to allow teachers (including class teachers)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or 
                request.user.groups.filter(name='ClassTeacher').exists() or
                request.user.groups.filter(name='Teacher').exists()):
            raise PermissionDenied("Teacher access required")
        return view_func(request, *args, **kwargs)
    return wrapper
