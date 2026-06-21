# ============================================
# DISCIPLINARY PROGRAM - TEMPLATE CREATOR
# Modern UI like Zeraki - Interactive Dashboard
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creating Interactive Templates" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$templatePath = "C:\Windows\System32\discipline\templates"
New-Item -ItemType Directory -Force -Path $templatePath | Out-Null

# ============================================
# BASE TEMPLATE - Modern Layout
# ============================================
Write-Host "[1/7] Creating base.html (Master Layout)..." -ForegroundColor Yellow
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
        
        /* Modern Navbar */
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
        
        /* Cards */
        .card-modern {
            background: white;
            border-radius: 20px;
            border: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            overflow: hidden;
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
        
        /* Stats Cards */
        .stat-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
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
        
        /* Tables */
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
        
        /* Buttons */
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
        
        /* Progress Bar */
        .progress-modern {
            height: 10px;
            border-radius: 10px;
            background: #e0e0e0;
        }
        
        .progress-bar-modern {
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        /* Alerts */
        .alert-modern {
            border-radius: 15px;
            border: none;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* Animations */
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
        
        /* Search Box */
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
        
        /* Modal */
        .modal-modern .modal-content {
            border-radius: 20px;
            border: none;
        }
        
        .modal-modern .modal-header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 20px 20px 0 0;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .stat-value {
                font-size: 1.5rem;
            }
            
            .table-modern {
                font-size: 0.85rem;
            }
            
            .btn-modern {
                padding: 0.35rem 1rem;
                font-size: 0.85rem;
            }
        }
        
        /* Loading Spinner */
        .spinner-modern {
            width: 50px;
            height: 50px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Toast Notifications */
        .toast-modern {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            animation: slideInRight 0.3s ease-out;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        /* Badges */
        .badge-critical {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 1.5s infinite;
        }
        
        .badge-warning {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        
        .badge-success {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.8; }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar-modern navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="{% url 'dashboard' %}">
                <i class="fas fa-gavel me-2"></i>Disciplinary Program
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-bell"></i>
                            {% if notifications_count %}
                            <span class="badge bg-danger">{{ notifications_count }}</span>
                            {% endif %}
                        </a>
                        <div class="dropdown-menu dropdown-menu-end">
                            <h6 class="dropdown-header">Notifications</h6>
                            <div class="dropdown-divider"></div>
                            <a class="dropdown-item" href="#">No new notifications</a>
                        </div>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle"></i> {{ user.username }}
                        </a>
                        <div class="dropdown-menu dropdown-menu-end">
                            <a class="dropdown-item" href="#"><i class="fas fa-user"></i> Profile</a>
                            <a class="dropdown-item" href="#"><i class="fas fa-cog"></i> Settings</a>
                            <div class="dropdown-divider"></div>
                            <a class="dropdown-item" href="{% url 'logout' %}">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </div>
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
                <i class="fas fa-{{ message.tags == 'success' and 'check-circle' or 'exclamation-circle' }} me-2"></i>
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-hide alerts after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
        
        // Add fade-in animation to all cards
        $(document).ready(function() {
            $('.card-modern, .stat-card').addClass('fade-in-up');
        });
        
        // Show toast notification
        function showToast(message, type = 'success') {
            const toast = $(`
                <div class="toast-modern alert alert-${type}">
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
'@ | Out-File -FilePath "$templatePath\base.html" -Encoding utf8

# ============================================
# LOGIN TEMPLATE
# ============================================
Write-Host "[2/7] Creating login.html (Modern Login)..." -ForegroundColor Yellow
@'
{% extends 'base.html' %}

{% block title %}Login - Disciplinary Program{% endblock %}

{% block extra_css %}
<style>
    .login-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .login-card {
        background: white;
        border-radius: 30px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        width: 100%;
        max-width: 450px;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
    }
    
    .login-icon i {
        font-size: 2.5rem;
        color: white;
    }
    
    .login-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .input-group-modern {
        position: relative;
        margin-bottom: 1.5rem;
    }
    
    .input-group-modern input {
        width: 100%;
        padding: 1rem 1rem 1rem 3rem;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .input-group-modern input:focus {
        border-color: #667eea;
        outline: none;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .input-group-modern i {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: #999;
    }
    
    .btn-login {
        width: 100%;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 15px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .btn-login:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    .credentials {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1rem;
        margin-top: 2rem;
    }
    
    .credentials h6 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .credentials p {
        margin-bottom: 0.25rem;
        font-size: 0.85rem;
    }
    
    .credentials i {
        margin-right: 0.5rem;
        color: #667eea;
    }
</style>
{% endblock %}

{% block content %}
<div class="login-wrapper">
    <div class="login-card">
        <div class="login-header">
            <div class="login-icon">
                <i class="fas fa-gavel"></i>
            </div>
            <h2 class="login-title">Disciplinary Program</h2>
            <p class="text-muted">School Management System</p>
        </div>
        
        <form method="post">
            {% csrf_token %}
            <div class="input-group-modern">
                <i class="fas fa-user"></i>
                <input type="text" name="username" placeholder="Username" required autofocus>
            </div>
            <div class="input-group-modern">
                <i class="fas fa-lock"></i>
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit" class="btn-login">
                <i class="fas fa-sign-in-alt me-2"></i>Login
            </button>
        </form>
        
        <div class="credentials">
            <h6><i class="fas fa-info-circle"></i> Demo Credentials</h6>
            <p><i class="fas fa-crown"></i> <strong>Admin:</strong> admin / admin123</p>
            <p><i class="fas fa-chalkboard-teacher"></i> <strong>Class Teacher:</strong> classteacher / teacher123</p>
            <p><i class="fas fa-user-graduate"></i> <strong>Teacher:</strong> teacher / teacher123</p>
        </div>
    </div>
</div>
{% endblock %}
'@ | Out-File -FilePath "$templatePath\login.html" -Encoding utf8

# ============================================
# ADMIN DASHBOARD
# ============================================
Write-Host "[3/7] Creating admin_dashboard.html..." -ForegroundColor Yellow
@'
{% extends 'base.html' %}

{% block title %}Admin Dashboard{% endblock %}

{% block extra_css %}
<style>
    .stat-icon-primary { background: linear-gradient(135deg, #667eea20, #764ba220); color: #667eea; }
    .stat-icon-danger { background: linear-gradient(135deg, #f5576c20, #f093fb20); color: #f5576c; }
    .stat-icon-success { background: linear-gradient(135deg, #43e97b20, #38f9d720); color: #43e97b; }
    .stat-icon-info { background: linear-gradient(135deg, #4facfe20, #00f2fe20); color: #4facfe; }
    
    .quick-action {
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .quick-action:hover {
        transform: translateX(5px);
    }
</style>
{% endblock %}

{% block content %}
<!-- Stats Overview -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-primary">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-value">{{ total_students }}</div>
            <div class="text-muted">Total Students</div>
            <small class="text-success"><i class="fas fa-arrow-up"></i> +12% this month</small>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-danger">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="stat-value">{{ critical_students }}</div>
            <div class="text-muted">Critical Cases</div>
            <small class="text-danger"><i class="fas fa-arrow-up"></i> Need attention</small>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-success">
                <i class="fas fa-flag-checkered"></i>
            </div>
            <div class="stat-value">{{ total_reports }}</div>
            <div class="text-muted">Total Reports</div>
            <small class="text-info"><i class="fas fa-chart-line"></i> This month: {{ reports_this_month }}</small>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-info">
                <i class="fas fa-chalkboard-teacher"></i>
            </div>
            <div class="stat-value">{{ teacher_stats|length }}</div>
            <div class="text-muted">Active Teachers</div>
            <small class="text-success"><i class="fas fa-users"></i> Reporting regularly</small>
        </div>
    </div>
</div>

<!-- Quick Actions & Charts -->
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card-modern">
            <div class="card-header-modern">
                <i class="fas fa-chart-bar me-2"></i> Weekly Report Trend
            </div>
            <div class="card-body p-4">
                <canvas id="weeklyChart" height="200"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card-modern">
            <div class="card-header-modern">
                <i class="fas fa-chart-pie me-2"></i> Categories Distribution
            </div>
            <div class="card-body p-4">
                <canvas id="categoryChart" height="200"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- Add Student Form -->
<div class="card-modern mb-4">
    <div class="card-header-modern">
        <i class="fas fa-plus-circle me-2"></i> Quick Add Student
    </div>
    <div class="card-body p-4">
        <form method="post" id="addStudentForm">
            {% csrf_token %}
            <input type="hidden" name="action" value="add_student">
            <div class="row">
                <div class="col-md-3 mb-3">
                    <input type="text" name="admission_number" class="form-control" placeholder="Admission Number" required>
                </div>
                <div class="col-md-3 mb-3">
                    <input type="text" name="name" class="form-control" placeholder="Full Name" required>
                </div>
                <div class="col-md-2 mb-3">
                    <select name="stream" class="form-control" required>
                        <option value="">Stream</option>
                        {% for stream_key, stream_name in streams %}
                        <option value="{{ stream_key }}">{{ stream_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2 mb-3">
                    <select name="form" class="form-control" required>
                        <option value="">Form</option>
                        {% for form_key, form_name in forms %}
                        <option value="{{ form_key }}">{{ form_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2 mb-3">
                    <button type="submit" class="btn-modern btn-modern-primary w-100">
                        <i class="fas fa-save"></i> Add Student
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- Students Table -->
<div class="card-modern">
    <div class="card-header-modern">
        <i class="fas fa-table me-2"></i> All Students
    </div>
    <div class="card-body p-0">
        <div class="search-box p-4">
            <i class="fas fa-search"></i>
            <input type="text" id="studentSearch" placeholder="Search by name or admission number...">
        </div>
        <div class="table-responsive">
            <table class="table-modern table" id="studentsTable">
                <thead>
                    <tr>
                        <th>Admission</th>
                        <th>Name</th>
                        <th>Stream</th>
                        <th>Form</th>
                        <th>Risk Score</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.admission_number }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.stream.get_name_display }}</td>
                        <td>{{ student.form }}</td>
                        <td>
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #f093fb, #f5576c){% elif student.risk_score >= 30 %}linear-gradient(135deg, #fa709a, #fee140){% else %}linear-gradient(135deg, #43e97b, #38f9d7){% endif %}">
                                </div>
                            </div>
                            <small>{{ student.risk_score }}%</small>
                        </td>
                        <td>
                            {% if student.is_critical %}
                            <span class="badge badge-critical">Critical</span>
                            {% elif student.risk_score >= 30 %}
                            <span class="badge badge-warning">Warning</span>
                            {% else %}
                            <span class="badge badge-success">Good</span>
                            {% endif %}
                        </td>
                        <td>
                            <a href="{% url 'student_profile' student.id %}" class="btn btn-sm btn-info">
                                <i class="fas fa-eye"></i>
                            </a>
                            <button class="btn btn-sm btn-danger" onclick="deleteStudent({{ student.id }})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- Pagination -->
        {% if students.has_other_pages %}
        <nav class="p-3">
            <ul class="pagination justify-content-center">
                {% if students.has_previous %}
                <li class="page-item"><a class="page-link" href="?page={{ students.previous_page_number }}">Previous</a></li>
                {% endif %}
                {% for i in students.paginator.page_range %}
                <li class="page-item {% if students.number == i %}active{% endif %}">
                    <a class="page-link" href="?page={{ i }}">{{ i }}</a>
                </li>
                {% endfor %}
                {% if students.has_next %}
                <li class="page-item"><a class="page-link" href="?page={{ students.next_page_number }}">Next</a></li>
                {% endif %}
            </ul>
        </nav>
        {% endif %}
    </div>
</div>

<script>
// Weekly Chart
const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
const weeklyData = {{ weekly_reports|safe }};
new Chart(weeklyCtx, {
    type: 'line',
    data: {
        labels: weeklyData.map(d => d.date),
        datasets: [{
            label: 'Reports',
            data: weeklyData.map(d => d.count),
            borderColor: '#4361ee',
            backgroundColor: 'rgba(67, 97, 238, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { position: 'top' }
        }
    }
});

// Category Chart
const categoryCtx = document.getElementById('categoryChart').getContext('2d');
const categoryData = {{ category_stats|safe }};
new Chart(categoryCtx, {
    type: 'doughnut',
    data: {
        labels: categoryData.map(c => c.category__name),
        datasets: [{
            data: categoryData.map(c => c.total),
            backgroundColor: ['#4361ee', '#3f37c9', '#4caf50', '#ff9800', '#f44336']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'bottom' }
        }
    }
});

// Search functionality
$('#studentSearch').on('keyup', function() {
    const value = $(this).val().toLowerCase();
    $('#studentsTable tbody tr').filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
});

// Delete student
function deleteStudent(id) {
    if (confirm('Are you sure you want to delete this student?')) {
        const form = $('<form method="post"></form>');
        form.append('<input type="hidden" name="action" value="delete_student">');
        form.append('<input type="hidden" name="student_id" value="' + id + '">');
        form.append('{% csrf_token %}');
        $('body').append(form);
        form.submit();
    }
}

// Auto-refresh alerts every 30 seconds
setInterval(function() {
    $.get('/api/alerts/', function(data) {
        if (data.has_alerts) {
            showToast(data.message, 'danger');
        }
    });
}, 30000);
</script>
{% endblock %}
'@ | Out-File -FilePath "$templatePath\admin_dashboard.html" -Encoding utf8

# ============================================
# CLASS TEACHER DASHBOARD
# ============================================
Write-Host "[4/7] Creating class_teacher_dashboard.html..." -ForegroundColor Yellow
@'
{% extends 'base.html' %}

{% block title %}Class Teacher Dashboard{% endblock %}

{% block content %}
<!-- Class Stats -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-primary">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-value">{{ class_stats.total }}</div>
            <div class="text-muted">My Students</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-danger">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="stat-value">{{ class_stats.critical }}</div>
            <div class="text-muted">Critical Cases</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-warning">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-value">{{ class_stats.avg_risk|floatformat:0 }}%</div>
            <div class="text-muted">Average Risk Score</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-icon stat-icon-info">
                <i class="fas fa-bell"></i>
            </div>
            <div class="stat-value">{{ notifications.count }}</div>
            <div class="text-muted">Pending Alerts</div>
        </div>
    </div>
</div>

<!-- Bulk Upload -->
<div class="card-modern mb-4">
    <div class="card-header-modern">
        <i class="fas fa-upload me-2"></i> Bulk Upload Students
    </div>
    <div class="card-body p-4">
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="bulk_upload">
            <div class="mb-3">
                <textarea name="bulk_data" class="form-control" rows="5" placeholder="name,admission_number,stream,form,year,notes&#10;John Doe,ADM001,MULUMBA,Form 1,2025,Good student"></textarea>
            </div>
            <button type="submit" class="btn-modern btn-modern-primary">
                <i class="fas fa-cloud-upload-alt"></i> Upload CSV
            </button>
        </form>
    </div>
</div>

<!-- My Students -->
<div class="card-modern mb-4">
    <div class="card-header-modern">
        <i class="fas fa-chalkboard me-2"></i> My Class - {{ assigned_stream|default:"All Streams" }} {{ assigned_form|default:"All Forms" }}
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table-modern table">
                <thead>
                    <tr>
                        <th>Admission</th>
                        <th>Name</th>
                        <th>Stream</th>
                        <th>Form</th>
                        <th>Risk Score</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in my_students %}
                    <tr>
                        <td>{{ student.admission_number }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.stream.get_name_display }}</td>
                        <td>{{ student.form }}</td>
                        <td>
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #f093fb, #f5576c){% elif student.risk_score >= 30 %}linear-gradient(135deg, #fa709a, #fee140){% else %}linear-gradient(135deg, #43e97b, #38f9d7){% endif %}">
                                </div>
                            </div>
                            <small>{{ student.risk_score }}%</small>
                        </td>
                        <td>
                            {% if student.is_critical %}
                            <span class="badge badge-critical">Critical</span>
                            {% else %}
                            <span class="badge badge-success">Good</span>
                            {% endif %}
                        </td>
                        <td>
                            <a href="{% url 'student_profile' student.id %}" class="btn btn-sm btn-info">
                                <i class="fas fa-eye"></i> View
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center py-4">
                            <i class="fas fa-folder-open fa-2x mb-2 d-block"></i>
                            No students found in your class
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Recent Reports -->
<div class="card-modern">
    <div class="card-header-modern">
        <i class="fas fa-history me-2"></i> Recent Reports in My Class
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table-modern table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Student</th>
                        <th>Category</th>
                        <th>Reported By</th>
                        <th>Points</th>
                    </tr>
                </thead>
                <tbody>
                    {% for report in recent_reports %}
                    <tr>
                        <td>{{ report.reported_at|date:"Y-m-d H:i" }}</td>
                        <td>{{ report.student.name }}</td>
                        <td>{{ report.category.name }}</td>
                        <td>{{ report.reported_by.get_full_name|default:report.reported_by.username }}</td>
                        <td class="text-danger">+{{ report.category.points }}</td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="5" class="text-center py-4">No reports yet</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Notifications Modal -->
<div class="modal fade" id="notificationsModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title"><i class="fas fa-bell me-2"></i>Notifications</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                {% for notif in notifications %}
                <div class="alert alert-{{ notif.notification_type }} mb-2">
                    <strong>{{ notif.title }}</strong>
                    <p class="mb-0 small">{{ notif.message|truncatechars:100 }}</p>
                </div>
                {% empty %}
                <p class="text-center text-muted">No notifications</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<script>
// Auto-refresh notifications
setInterval(function() {
    location.reload();
}, 60000);
</script>
{% endblock %}
'@ | Out-File -FilePath "$templatePath\class_teacher_dashboard.html" -Encoding utf8

# ============================================
# TEACHER DASHBOARD
# ============================================
Write-Host "[5/7] Creating teacher_dashboard.html..." -ForegroundColor Yellow
@'
{% extends 'base.html' %}

{% block title %}Teacher Dashboard{% endblock %}

{% block extra_css %}
<style>
    .search-result-card {
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .search-result-card:hover {
        transform: translateX(5px);
        background: linear-gradient(135deg, #667eea10, #764ba210);
    }
    
    .category-btn {
        transition: all 0.3s;
        margin: 5px;
    }
    
    .category-btn:hover {
        transform: translateY(-2px);
    }
</style>
{% endblock %}

{% block content %}
<!-- Search Section -->
<div class="card-modern mb-4">
    <div class="card-header-modern">
        <i class="fas fa-search me-2"></i> Search Student
    </div>
    <div class="card-body p-4">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="searchStudent" placeholder="Search by name or admission number...">
        </div>
        <div id="searchResults" class="mt-3"></div>
    </div>
</div>

<!-- All Students -->
<div class="card-modern">
    <div class="card-header-modern">
        <i class="fas fa-list me-2"></i> All Students
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table-modern table" id="studentsTable">
                <thead>
                    <tr>
                        <th>Admission</th>
                        <th>Name</th>
                        <th>Stream</th>
                        <th>Form</th>
                        <th>Risk Score</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.admission_number }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.stream.get_name_display }}</td>
                        <td>{{ student.form }}</td>
                        <td>
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #f093fb, #f5576c){% elif student.risk_score >= 30 %}linear-gradient(135deg, #fa709a, #fee140){% else %}linear-gradient(135deg, #43e97b, #38f9d7){% endif %}">
                                </div>
                            </div>
                            <small>{{ student.risk_score }}%</small>
                         </td>
                        <td>
                            <button class="btn-modern btn-modern-primary" onclick="openReportModal({{ student.id }}, '{{ student.name }}')" style="padding: 0.25rem 1rem;">
                                <i class="fas fa-flag"></i> Report
                            </button>
                         </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Report Modal -->
<div class="modal fade" id="reportModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fas fa-flag me-2"></i>Report Student
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="post">
                {% csrf_token %}
                <input type="hidden" name="action" value="report_student">
                <input type="hidden" name="student_id" id="reportStudentId">
                <div class="modal-body">
                    <p class="mb-3">Reporting: <strong id="reportStudentName"></strong></p>
                    <div class="mb-3">
                        <label class="form-label">Offense Category</label>
                        <select name="category_id" class="form-control" required>
                            {% for category in categories %}
                            <option value="{{ category.id }}">
                                {{ category.name }} (+{{ category.points }} points)
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Additional Comments</label>
                        <textarea name="comments" class="form-control" rows="3" placeholder="Describe the incident..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn-modern btn-modern-primary">Submit Report</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
let searchTimeout;

$('#searchStudent').on('keyup', function() {
    clearTimeout(searchTimeout);
    const query = $(this).val();
    
    if (query.length < 2) {
        $('#searchResults').html('');
        return;
    }
    
    searchTimeout = setTimeout(function() {
        $.get('/api/search-students/', { q: query }, function(data) {
            if (data.students.length > 0) {
                let html = '<h6 class="mb-3">Search Results:</h6>';
                data.students.forEach(student => {
                    html += `
                        <div class="search-result-card card mb-2 p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${student.name}</strong><br>
                                    <small>${student.admission_number} | ${student.stream} - ${student.form}</small>
                                    <br><small class="text-${student.is_critical ? 'danger' : 'success'}">Risk: ${student.risk_score}%</small>
                                </div>
                                <button class="btn-modern btn-modern-primary" onclick="openReportModal(${student.id}, '${student.name}')">
                                    <i class="fas fa-flag"></i> Report
                                </button>
                            </div>
                        </div>
                    `;
                });
                $('#searchResults').html(html);
            } else {
                $('#searchResults').html('<div class="alert alert-info">No students found</div>');
            }
        });
    }, 500);
});

function openReportModal(id, name) {
    $('#reportStudentId').val(id);
    $('#reportStudentName').text(name);
    $('#reportModal').modal('show');
}

// Success toast on report
{% if messages %}
{% for message in messages %}
showToast('{{ message }}', 'success');
{% endfor %}
{% endif %}
</script>
{% endblock %}
'@ | Out-File -FilePath "$templatePath\teacher_dashboard.html" -Encoding utf8

# ============================================
# STUDENT PROFILE
# ============================================
Write-Host "[6/7] Creating student_profile.html..." -ForegroundColor Yellow
@'
{% extends 'base.html' %}

{% block title %}{{ student.name }} - Profile{% endblock %}

{% block content %}
<div class="row">
    <!-- Left Column - Student Info -->
    <div class="col-md-4">
        <div class="card-modern mb-4">
            <div class="card-header-modern text-center">
                <i class="fas fa-user-graduate fa-3x mb-2"></i>
                <h4 class="mb-0">{{ student.name }}</h4>
                <small>{{ student.admission_number }}</small>
            </div>
            <div class="card-body p-4">
                <div class="mb-3">
                    <label class="text-muted">Stream</label>
                    <p class="mb-0"><strong>{{ student.stream.get_name_display }}</strong></p>
                </div>
                <div class="mb-3">
                    <label class="text-muted">Form</label>
                    <p class="mb-0"><strong>{{ student.form }}</strong></p>
                </div>
                <div class="mb-3">
                    <label class="text-muted">Year</label>
                    <p class="mb-0"><strong>{{ student.year }}</strong></p>
                </div>
                <div class="mb-3">
                    <label class="text-muted">Risk Score</label>
                    <div class="progress-modern mb-2">
                        <div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #f093fb, #f5576c){% elif student.risk_score >= 30 %}linear-gradient(135deg, #fa709a, #fee140){% else %}linear-gradient(135deg, #43e97b, #38f9d7){% endif %}">
                        </div>
                    </div>
                    <h3 class="{% if student.is_critical %}text-danger{% else %}text-success{% endif %}">{{ student.risk_score }}%</h3>
                </div>
                {% if student.optional_notes %}
                <div class="alert alert-info">
                    <i class="fas fa-sticky-note"></i> {{ student.optional_notes }}
                </div>
                {% endif %}
                <div class="text-center">
                    <span class="badge {% if student.is_critical %}badge-critical{% elif student.risk_score >= 30 %}badge-warning{% else %}badge-success{% endif %}" style="font-size: 1rem; padding: 0.5rem 1rem;">
                        {{ student.risk_level }}
                    </span>
                </div>
            </div>
        </div>
        
        <!-- Category Breakdown -->
        <div class="card-modern">
            <div class="card-header-modern">
                <i class="fas fa-chart-pie me-2"></i> Offense Categories
            </div>
            <div class="card-body p-4">
                <canvas id="categoryChart" height="250"></canvas>
                <div class="mt-3">
                    {% for cat in category_breakdown %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ cat.category__name }}</span>
                        <span class="badge bg-secondary">{{ cat.count }} times</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- Right Column - Reports & Timeline -->
    <div class="col-md-8">
        <!-- Risk Timeline -->
        <div class="card-modern mb-4">
            <div class="card-header-modern">
                <i class="fas fa-chart-line me-2"></i> Risk Score Timeline
            </div>
            <div class="card-body p-4">
                <canvas id="timelineChart" height="150"></canvas>
            </div>
        </div>
        
        <!-- Reports History -->
        <div class="card-modern">
            <div class="card-header-modern">
                <i class="fas fa-history me-2"></i> Report History ({{ total_reports }} reports)
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table-modern table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Category</th>
                                <th>Reported By</th>
                                <th>Points</th>
                                <th>Comments</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for report in reports %}
                            <tr>
                                <td>{{ report.reported_at|date:"Y-m-d H:i:s" }}</td>
                                <td>
                                    <span class="badge bg-danger">{{ report.category.name }}</span>
                                </td>
                                <td>{{ report.reported_by.get_full_name|default:report.reported_by.username }}</td>
                                <td><span class="text-danger">+{{ report.category.points }}</span></td>
                                <td>{{ report.comments|truncatechars:50|default:"-" }}</td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center py-4">
                                    <i class="fas fa-inbox fa-2x mb-2 d-block"></i>
                                    No reports yet
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Category Chart
const categoryCtx = document.getElementById('categoryChart').getContext('2d');
const categoryData = {{ category_breakdown|safe }};
new Chart(categoryCtx, {
    type: 'pie',
    data: {
        labels: categoryData.map(c => c.category__name),
        datasets: [{
            data: categoryData.map(c => c.count),
            backgroundColor: ['#4361ee', '#3f37c9', '#4caf50', '#ff9800', '#f44336']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'bottom' }
        }
    }
});

// Timeline Chart
const timelineCtx = document.getElementById('timelineChart').getContext('2d');
const timelineData = {{ timeline|safe }};
new Chart(timelineCtx, {
    type: 'line',
    data: {
        labels: timelineData.map(t => t.date),
        datasets: [{
            label: 'Points Added',
            data: timelineData.map(t => t.points),
            borderColor: '#4361ee',
            backgroundColor: 'rgba(67, 97, 238, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Points: ${context.raw}`;
                    }
                }
            }
        }
    }
});
</script>
{% endblock %}
'@ | Out-File -FilePath "$templatePath\student_profile.html" -Encoding utf8

# ============================================
# CREATE STATIC FOLDER AND FILES
# ============================================
Write-Host "[7/7] Creating static files..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "C:\Windows\System32\discipline\static\css" | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Windows\System32\discipline\static\js" | Out-Null

# Custom CSS
@'
/* Custom styles for Disciplinary Program */
.stat-card {
    transition: all 0.3s;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.btn-modern {
    transition: all 0.3s;
}

.btn-modern:hover {
    transform: translateY(-2px);
}

.progress-modern {
    overflow: hidden;
}

.progress-bar-modern {
    transition: width 0.5s ease;
}

.alert-modern {
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
'@ | Out-File -FilePath "C:\Windows\System32\discipline\static\css\custom.css" -Encoding utf8

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ ALL TEMPLATES CREATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Templates Location: $templatePath" -ForegroundColor Cyan
Write-Host "📁 Static Files: C:\Windows\System32\discipline\static" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "1. cd C:\Windows\System32\discipline" -ForegroundColor White
Write-Host "2. python manage.py runserver" -ForegroundColor White
Write-Host "3. Open browser to http://127.0.0.1:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Login with:" -ForegroundColor Yellow
Write-Host "   Admin: admin / admin123" -ForegroundColor White
Write-Host "   Class Teacher: classteacher / teacher123" -ForegroundColor White
Write-Host "   Teacher: teacher / teacher123" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Green

# Open the directory
explorer "C:\Windows\System32\discipline"
'@ | Out-File -FilePath "$templatePath\__init__.py" -Encoding utf8 -Force

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ ALL TEMPLATES CREATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Templates Location: $templatePath" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "1. cd C:\Windows\System32\discipline" -ForegroundColor White
Write-Host "2. python manage.py runserver" -ForegroundColor White
Write-Host "3. Open browser to http://127.0.0.1:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Login with:" -ForegroundColor Yellow
Write-Host "   Admin: admin / admin123" -ForegroundColor White
Write-Host "   Class Teacher: classteacher / teacher123" -ForegroundColor White
Write-Host "   Teacher: teacher / teacher123" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Green

# Open the directory
explorer "C:\Windows\System32\discipline"