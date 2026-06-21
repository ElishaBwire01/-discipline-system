# ============================================
# FIX URL CONFIGURATION AND TEMPLATES
# Resolves NoReverseMatch errors
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing URL Configuration and Templates" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$projectPath = "C:\Windows\System32\discipline"
$templatePath = "$projectPath\templates"

# ============================================
# FIX CORE/URLS.PY
# ============================================
Write-Host "[1/3] Fixing core/urls.py..." -ForegroundColor Yellow
@'
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard URLs - Main entry point
    path('', views.dashboard_redirect, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Class Teacher Dashboard
    path('class-teacher-dashboard/', views.class_teacher_dashboard, name='class_teacher_dashboard'),
    
    # Teacher Dashboard
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # Student Profile
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    
    # API Endpoints
    path('api/search-students/', views.search_students_api, name='search_students_api'),
    path('api/notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]
'@ | Out-File -FilePath "$projectPath\core\urls.py" -Encoding utf8 -Force

# ============================================
# UPDATE CORE/VIEWS.PY WITH REDIRECT FIX
# ============================================
Write-Host "[2/3] Updating core/views.py..." -ForegroundColor Yellow

# Read existing views.py and append the redirect function
$viewsContent = @'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Student, DisciplineReport, DisciplineCategory, Notification, Stream, TeacherProfile

def admin_required(user):
    return user.is_superuser

def class_teacher_required(user):
    return user.is_superuser or user.groups.filter(name='ClassTeacher').exists()

@login_required
def dashboard_redirect(request):
    """Redirect users to their appropriate dashboard based on role"""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.groups.filter(name='ClassTeacher').exists():
        return redirect('class_teacher_dashboard')
    else:
        return redirect('teacher_dashboard')

@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    # Statistics with optimized queries
    total_students = Student.objects.filter(is_active=True).count()
    critical_students = Student.objects.filter(risk_score__gte=60, is_active=True).count()
    total_reports = DisciplineReport.objects.count()
    reports_this_month = DisciplineReport.objects.filter(
        reported_at__month=timezone.now().month
    ).count()
    
    # Teacher performance stats
    teacher_stats = DisciplineReport.objects.values(
        'reported_by__username',
        'reported_by__first_name',
        'reported_by__last_name'
    ).annotate(
        total_reports=Count('id'),
        avg_points=Avg('category__points')
    ).order_by('-total_reports')[:10]
    
    # Category statistics
    category_stats = DisciplineReport.objects.values(
        'category__name'
    ).annotate(
        total=Count('id'),
        total_points=Sum('category__points')
    ).order_by('-total')
    
    # High risk students
    high_risk_students = Student.objects.filter(
        risk_score__gte=60, is_active=True
    ).select_related('stream')[:20]
    
    # Recent reports
    recent_reports = DisciplineReport.objects.select_related(
        'student', 'reported_by', 'category'
    )[:50]
    
    # Weekly trend
    week_ago = timezone.now() - timedelta(days=7)
    weekly_reports = DisciplineReport.objects.filter(
        reported_at__gte=week_ago
    ).extra({'date': "date(reported_at)"}).values('date').annotate(count=Count('id'))
    
    # Pagination for students
    students_list = Student.objects.select_related('stream').filter(is_active=True)
    paginator = Paginator(students_list, 20)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_student':
            try:
                stream = Stream.objects.get(name=request.POST.get('stream'))
                Student.objects.create(
                    admission_number=request.POST.get('admission_number'),
                    name=request.POST.get('name'),
                    stream=stream,
                    form=request.POST.get('form'),
                    year=int(request.POST.get('year', timezone.now().year)),
                    optional_notes=request.POST.get('optional_notes', ''),
                    created_by=request.user
                )
                messages.success(request, 'Student added successfully')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
            return redirect('admin_dashboard')
        
        elif action == 'delete_student':
            student_id = request.POST.get('student_id')
            Student.objects.filter(id=student_id).update(is_active=False)
            messages.success(request, 'Student deactivated successfully')
            return redirect('admin_dashboard')
    
    context = {
        'students': students,
        'total_students': total_students,
        'critical_students': critical_students,
        'total_reports': total_reports,
        'reports_this_month': reports_this_month,
        'high_risk_students': high_risk_students,
        'teacher_stats': teacher_stats,
        'category_stats': category_stats,
        'recent_reports': recent_reports,
        'weekly_reports': list(weekly_reports),
        'streams': Stream.STREAM_CHOICES,
        'forms': Student.FORM_CHOICES,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(class_teacher_required)
def class_teacher_dashboard(request):
    # Get teacher profile
    try:
        profile = request.user.teacher_profile
        assigned_stream = profile.assigned_stream
        assigned_form = profile.assigned_form
    except TeacherProfile.DoesNotExist:
        assigned_stream = None
        assigned_form = None
    
    # Filter students by assigned class
    my_students = Student.objects.filter(is_active=True)
    if assigned_stream:
        my_students = my_students.filter(stream=assigned_stream)
    if assigned_form:
        my_students = my_students.filter(form=assigned_form)
    
    my_students = my_students.select_related('stream')[:50]
    
    # Recent reports in their class
    recent_reports = DisciplineReport.objects.select_related(
        'student', 'reported_by', 'category'
    )
    if assigned_stream:
        recent_reports = recent_reports.filter(student__stream=assigned_stream)
    recent_reports = recent_reports[:30]
    
    # Unread notifications
    notifications = request.user.notifications.filter(is_read=False)[:20]
    
    # Class statistics
    class_stats = {
        'total': my_students.count(),
        'critical': my_students.filter(risk_score__gte=60).count(),
        'warning': my_students.filter(risk_score__range=(30, 59)).count(),
        'good': my_students.filter(risk_score__lt=30).count(),
        'avg_risk': my_students.aggregate(Avg('risk_score'))['risk_score__avg'] or 0,
    }
    
    # Handle bulk upload
    if request.method == 'POST' and request.POST.get('action') == 'bulk_upload':
        data = request.POST.get('bulk_data', '')
        lines = data.strip().split('\n')
        added = 0
        errors = 0
        
        for line in lines:
            if ',' in line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    name, admission, stream_name, form = parts[:4]
                    year = int(parts[4]) if len(parts) > 4 else timezone.now().year
                    notes = parts[5] if len(parts) > 5 else ''
                    
                    try:
                        stream = Stream.objects.get(name=stream_name.upper())
                        Student.objects.get_or_create(
                            admission_number=admission,
                            defaults={
                                'name': name,
                                'stream': stream,
                                'form': form,
                                'year': year,
                                'optional_notes': notes,
                                'created_by': request.user
                            }
                        )
                        added += 1
                    except Stream.DoesNotExist:
                        errors += 1
        
        messages.success(request, f'Added {added} students. Errors: {errors}')
        return redirect('class_teacher_dashboard')
    
    context = {
        'my_students': my_students,
        'recent_reports': recent_reports,
        'notifications': notifications,
        'class_stats': class_stats,
        'assigned_stream': assigned_stream,
        'assigned_form': assigned_form,
    }
    return render(request, 'class_teacher_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    students = Student.objects.filter(is_active=True).select_related('stream').order_by('name')
    categories = DisciplineCategory.objects.filter(is_active=True)
    
    # Handle student report submission
    if request.method == 'POST' and request.POST.get('action') == 'report_student':
        student_id = request.POST.get('student_id')
        category_id = request.POST.get('category_id')
        comments = request.POST.get('comments', '')
        
        student = get_object_or_404(Student, id=student_id)
        category = get_object_or_404(DisciplineCategory, id=category_id)
        
        report = DisciplineReport.objects.create(
            student=student,
            reported_by=request.user,
            category=category,
            comments=comments
        )
        
        messages.success(
            request,
            f'Report submitted: {category.name} (+{category.points} points). '
            f'Student risk score: {student.risk_score}%'
        )
        return redirect('teacher_dashboard')
    
    context = {
        'students': students,
        'categories': categories,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id, is_active=True)
    reports = student.reports.select_related('reported_by', 'category').all()
    
    # Analytics
    category_breakdown = reports.values('category__name').annotate(
        count=Count('id'),
        total_points=Sum('category__points')
    )
    
    teacher_breakdown = reports.values(
        'reported_by__username',
        'reported_by__first_name',
        'reported_by__last_name'
    ).annotate(count=Count('id'))
    
    # Timeline data for chart
    timeline = []
    for report in reports[:30]:
        timeline.append({
            'date': report.reported_at.strftime('%Y-%m-%d'),
            'points': report.category.points,
            'category': report.category.name,
        })
    
    context = {
        'student': student,
        'reports': reports,
        'category_breakdown': category_breakdown,
        'teacher_breakdown': teacher_breakdown,
        'timeline': timeline,
        'total_reports': reports.count(),
        'total_points': student.risk_score,
    }
    return render(request, 'student_profile.html', context)

@login_required
def search_students_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'students': []})
    
    students = Student.objects.filter(
        Q(name__icontains=query) | Q(admission_number__icontains=query),
        is_active=True
    ).select_related('stream')[:20]
    
    data = [{
        'id': s.id,
        'name': s.name,
        'admission_number': s.admission_number,
        'stream': s.stream.get_name_display(),
        'form': s.form,
        'risk_score': s.risk_score,
        'risk_level': 'Critical' if s.is_critical else 'Good',
        'is_critical': s.is_critical,
    } for s in students]
    
    return JsonResponse({'students': data})

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id)
        notification.mark_read(request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
'@

$viewsContent | Out-File -FilePath "$projectPath\core\views.py" -Encoding utf8 -Force

# ============================================
# FIX BASE.HTML - Remove dashboard URL
# ============================================
Write-Host "[3/3] Fixing base.html template..." -ForegroundColor Yellow
@'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Disciplinary Program{% endblock %}</title>
    
    <!-- Bootstrap 5 + Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --success: #4caf50;
            --danger: #f44336;
            --warning: #ff9800;
            --info: #2196f3;
            --dark: #1a1a2e;
            --light: #f8f9fa;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar-modern {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: 800;
            font-size: 1.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .card-modern {
            background: white;
            border-radius: 20px;
            border: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .card-modern:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .card-header-modern {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 1.5rem;
            border: none;
            font-weight: 600;
        }
        
        .stat-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 20px;
        }
        
        .stat-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 1.8rem;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            margin: 0.5rem 0;
        }
        
        .stat-icon-primary { background: linear-gradient(135deg, #667eea20, #764ba220); color: #667eea; }
        .stat-icon-danger { background: linear-gradient(135deg, #f5576c20, #f093fb20); color: #f5576c; }
        .stat-icon-success { background: linear-gradient(135deg, #43e97b20, #38f9d720); color: #43e97b; }
        .stat-icon-info { background: linear-gradient(135deg, #4facfe20, #00f2fe20); color: #4facfe; }
        
        .table-modern {
            background: white;
            border-radius: 15px;
            overflow: hidden;
        }
        
        .table-modern thead th {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 1rem;
            font-weight: 600;
        }
        
        .table-modern tbody tr:hover {
            background: rgba(67, 97, 238, 0.05);
            cursor: pointer;
        }
        
        .btn-modern {
            border-radius: 50px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .btn-modern-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
        }
        
        .btn-modern-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);
        }
        
        .progress-modern {
            height: 10px;
            border-radius: 10px;
            background: #e0e0e0;
            overflow: hidden;
        }
        
        .progress-bar-modern {
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .search-box {
            position: relative;
            margin-bottom: 2rem;
        }
        
        .search-box input {
            width: 100%;
            padding: 1rem 3rem 1rem 1.5rem;
            border: 2px solid #e0e0e0;
            border-radius: 50px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .search-box input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
        }
        
        .search-box i {
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            color: #999;
        }
        
        .badge-critical {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 1.5s infinite;
            padding: 5px 10px;
            border-radius: 20px;
            color: white;
        }
        
        .badge-warning {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 5px 10px;
            border-radius: 20px;
            color: white;
        }
        
        .badge-success {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 5px 10px;
            border-radius: 20px;
            color: white;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.8; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.5s ease-out;
        }
        
        .alert-modern {
            border-radius: 15px;
            border: none;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        @media (max-width: 768px) {
            .stat-value {
                font-size: 1.5rem;
            }
            .table-modern {
                font-size: 0.85rem;
            }
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar-modern navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-gavel me-2"></i>Disciplinary Program
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'logout' %}">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}
    
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
            <div class="alert alert-modern alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {% if message.tags == 'success' %}
                <i class="fas fa-check-circle me-2"></i>
                {% else %}
                <i class="fas fa-exclamation-circle me-2"></i>
                {% endif %}
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
        
        $(document).ready(function() {
            $('.card-modern, .stat-card').addClass('fade-in-up');
        });
        
        function showToast(message, type) {
            const toast = $(`
                <div class="toast-modern alert alert-${type}" style="position: fixed; top: 20px; right: 20px; z-index: 9999; animation: slideInRight 0.3s ease-out;">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                    ${message}
                </div>
            `);
            $('body').append(toast);
            setTimeout(() => toast.fadeOut(), 3000);
        }
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
'@ | Out-File -FilePath "$templatePath\base.html" -Encoding utf8 -Force

# ============================================
# CREATE SIMPLE INDEX PAGE
# ============================================
Write-Host "[+] Creating index.html redirect..." -ForegroundColor Yellow
@'
{% load core_tags %}
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={% url 'login' %}">
    <title>Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="{% url 'login' %}">login page</a>...</p>
</body>
</html>
'@ | Out-File -FilePath "$templatePath\index.html" -Encoding utf8 -Force

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ ALL FIXES APPLIED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Restart your server with these commands:" -ForegroundColor Yellow
Write-Host "cd C:\Windows\System32\discipline" -ForegroundColor White
Write-Host "python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Access the application:" -ForegroundColor Cyan
Write-Host "   URL: http://127.0.0.1:8000/login/" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Login Credentials:" -ForegroundColor Yellow
Write-Host "   Admin:          admin / admin123" -ForegroundColor White
Write-Host "   Class Teacher:  classteacher / teacher123" -ForegroundColor White
Write-Host "   Teacher:        teacher / teacher123" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Green

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
Set-Location $projectPath
python manage.py makemigrations core --noinput
python manage.py migrate --noinput

Write-Host "`n✅ Fix complete! Run 'python manage.py runserver' to start the server." -ForegroundColor Green