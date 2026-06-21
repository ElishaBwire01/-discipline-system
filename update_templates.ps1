# ============================================
# PROFESSIONAL TEMPLATE UPDATE SCRIPT
# ============================================
# This script updates all templates with professional UI

Write-Host "🚀 Starting Professional Template Updates..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$basePath = "C:\Windows\System32\discipline\templates"
$includesPath = "$basePath\includes"

# ============================================
# 1. UPDATE BASE.HTML
# ============================================
Write-Host "`n📝 Updating base.html..." -ForegroundColor Yellow

@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Disciplinary Management System{% endblock %}</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts - Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <!-- AOS Animation Library -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --primary-light: #60a5fa;
            --secondary: #7c3aed;
            --accent: #06b6d4;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #0f172a;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
            --radius: 12px;
            --radius-lg: 20px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--gray-50);
            min-height: 100vh;
            color: var(--dark);
        }
        
        /* ===== NAVBAR ===== */
        .navbar-modern {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border-bottom: 1px solid rgba(226, 232, 240, 0.6);
            padding: 0.75rem 0;
            position: sticky;
            top: 0;
            z-index: 1050;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        
        .navbar-brand {
            font-weight: 800;
            font-size: 1.25rem;
            color: var(--dark) !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .navbar-brand .brand-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1rem;
        }
        
        .nav-link {
            font-weight: 500;
            color: var(--gray-600) !important;
            transition: var(--transition);
            padding: 0.5rem 1rem !important;
            border-radius: var(--radius);
        }
        
        .nav-link:hover, .nav-link.active {
            color: var(--primary) !important;
            background: rgba(37, 99, 235, 0.08);
        }
        
        .nav-link i {
            margin-right: 0.5rem;
            width: 1.25rem;
            text-align: center;
        }
        
        /* ===== NOTIFICATIONS ===== */
        .notification-icon {
            position: relative;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: var(--radius);
            transition: var(--transition);
        }
        
        .notification-icon:hover {
            background: rgba(37, 99, 235, 0.08);
        }
        
        .notification-icon .bell-icon {
            font-size: 1.25rem;
            color: var(--gray-600);
        }
        
        .notification-badge {
            position: absolute;
            top: 0;
            right: 0;
            background: var(--danger);
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 700;
            min-width: 20px;
            text-align: center;
            border: 2px solid white;
            animation: pulse-badge 2s infinite;
        }
        
        @keyframes pulse-badge {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .notification-dropdown {
            position: absolute;
            right: 0;
            top: calc(100% + 8px);
            min-width: 380px;
            max-width: 420px;
            background: white;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            border: 1px solid var(--gray-200);
            display: none;
            max-height: 480px;
            overflow-y: auto;
            z-index: 1060;
        }
        
        .notification-dropdown.show { display: block; }
        
        .notification-dropdown-header {
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        }
        
        .notification-item {
            padding: 0.75rem 1.25rem;
            border-bottom: 1px solid var(--gray-100);
            transition: var(--transition);
            cursor: pointer;
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
        }
        
        .notification-item:hover {
            background: var(--gray-50);
        }
        
        .notification-item .notif-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.875rem;
            margin-top: 0.125rem;
        }
        
        .notification-item .notif-icon.critical { background: #fef2f2; color: var(--danger); }
        .notification-item .notif-icon.warning { background: #fffbeb; color: var(--warning); }
        .notification-item .notif-icon.info { background: #eff6ff; color: var(--primary); }
        .notification-item .notif-icon.success { background: #ecfdf5; color: var(--success); }
        
        .notification-item .notif-content { flex: 1; min-width: 0; }
        .notification-item .notif-content .notif-title { font-weight: 600; font-size: 0.875rem; margin-bottom: 0.125rem; }
        .notification-item .notif-content .notif-message { font-size: 0.813rem; color: var(--gray-500); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .notification-item .notif-content .notif-time { font-size: 0.75rem; color: var(--gray-400); margin-top: 0.25rem; }
        
        /* ===== CARDS ===== */
        .card-modern {
            background: white;
            border-radius: var(--radius-lg);
            border: 1px solid var(--gray-200);
            box-shadow: var(--shadow);
            transition: var(--transition);
            overflow: hidden;
            margin-bottom: 1.5rem;
        }
        
        .card-modern:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }
        
        .card-header-modern {
            padding: 1rem 1.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .card-header-modern .header-icon {
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.875rem;
        }
        
        /* ===== STAT CARDS ===== */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background: white;
            border-radius: var(--radius-lg);
            padding: 1.25rem;
            border: 1px solid var(--gray-200);
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        
        .stat-card .stat-bg-icon {
            position: absolute;
            right: -10px;
            bottom: -10px;
            font-size: 4rem;
            opacity: 0.06;
            color: var(--primary);
        }
        
        .stat-card .stat-icon {
            width: 44px;
            height: 44px;
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
        }
        
        .stat-card .stat-icon.primary { background: #eff6ff; color: var(--primary); }
        .stat-card .stat-icon.danger { background: #fef2f2; color: var(--danger); }
        .stat-card .stat-icon.success { background: #ecfdf5; color: var(--success); }
        .stat-card .stat-icon.warning { background: #fffbeb; color: var(--warning); }
        .stat-card .stat-icon.info { background: #f0fdf4; color: var(--accent); }
        
        .stat-card .stat-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--dark);
            line-height: 1.2;
        }
        
        .stat-card .stat-label {
            font-size: 0.875rem;
            color: var(--gray-500);
            font-weight: 500;
        }
        
        .stat-card .stat-change {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.125rem 0.5rem;
            border-radius: 20px;
            display: inline-block;
            margin-top: 0.25rem;
        }
        
        .stat-card .stat-change.up { background: #ecfdf5; color: var(--success); }
        .stat-card .stat-change.down { background: #fef2f2; color: var(--danger); }
        
        /* ===== TABLES ===== */
        .table-modern {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        
        .table-modern thead th {
            background: var(--gray-50);
            color: var(--gray-600);
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.75rem 1rem;
            border-bottom: 2px solid var(--gray-200);
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .table-modern tbody td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--gray-100);
            vertical-align: middle;
            font-size: 0.875rem;
        }
        
        .table-modern tbody tr {
            transition: var(--transition);
        }
        
        .table-modern tbody tr:hover {
            background: var(--gray-50);
        }
        
        /* ===== PROGRESS BARS ===== */
        .progress-modern {
            height: 8px;
            border-radius: 999px;
            background: var(--gray-200);
            overflow: hidden;
            min-width: 80px;
        }
        
        .progress-bar-modern {
            height: 100%;
            border-radius: 999px;
            transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
            background: linear-gradient(135deg, var(--primary), var(--secondary));
        }
        
        /* ===== BADGES ===== */
        .badge-modern {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.75rem;
        }
        
        .badge-modern.badge-critical { background: #fef2f2; color: var(--danger); }
        .badge-modern.badge-warning { background: #fffbeb; color: var(--warning); }
        .badge-modern.badge-success { background: #ecfdf5; color: var(--success); }
        .badge-modern.badge-info { background: #eff6ff; color: var(--primary); }
        
        /* ===== BUTTONS ===== */
        .btn-modern {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.5rem 1.25rem;
            border-radius: var(--radius);
            font-weight: 600;
            font-size: 0.875rem;
            transition: var(--transition);
            border: none;
            cursor: pointer;
            text-decoration: none;
        }
        
        .btn-modern-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }
        
        .btn-modern-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.35);
            color: white;
        }
        
        .btn-modern-secondary { background: var(--gray-200); color: var(--gray-700); }
        .btn-modern-secondary:hover { background: var(--gray-300); color: var(--gray-700); }
        
        .btn-modern-success { background: var(--success); color: white; }
        .btn-modern-success:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(16, 185, 129, 0.35); color: white; }
        
        .btn-modern-danger { background: var(--danger); color: white; }
        .btn-modern-danger:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(239, 68, 68, 0.35); color: white; }
        
        .btn-modern-warning { background: var(--warning); color: white; }
        .btn-modern-warning:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(245, 158, 11, 0.35); color: white; }
        
        .btn-modern-sm { padding: 0.25rem 0.75rem; font-size: 0.75rem; }
        
        /* ===== FORMS ===== */
        .form-control-modern {
            width: 100%;
            padding: 0.625rem 1rem;
            border: 2px solid var(--gray-200);
            border-radius: var(--radius);
            font-size: 0.875rem;
            transition: var(--transition);
            background: white;
        }
        
        .form-control-modern:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }
        
        .form-control-modern::placeholder { color: var(--gray-400); }
        .form-label-modern { font-weight: 600; font-size: 0.875rem; color: var(--gray-700); margin-bottom: 0.375rem; }
        
        /* ===== SEARCH BOX ===== */
        .search-box {
            position: relative;
        }
        
        .search-box .search-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gray-400);
        }
        
        .search-box input {
            width: 100%;
            padding: 0.625rem 1rem 0.625rem 2.75rem;
            border: 2px solid var(--gray-200);
            border-radius: var(--radius);
            font-size: 0.875rem;
            transition: var(--transition);
        }
        
        .search-box input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }
        
        /* ===== ALERTS ===== */
        .alert-modern {
            border: none;
            border-radius: var(--radius-lg);
            padding: 1rem 1.25rem;
            box-shadow: var(--shadow);
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .alert-modern .alert-icon {
            font-size: 1.25rem;
            margin-top: 0.125rem;
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .stat-grid { grid-template-columns: repeat(2, 1fr); }
            .notification-dropdown { min-width: calc(100vw - 2rem); right: -1rem; }
            .table-modern { font-size: 0.813rem; }
            .table-modern thead th, .table-modern tbody td { padding: 0.5rem 0.625rem; }
            .card-header-modern { font-size: 0.875rem; padding: 0.75rem 1rem; }
        }
        
        @media (max-width: 480px) {
            .stat-grid { grid-template-columns: 1fr 1fr; gap: 0.625rem; }
            .stat-card { padding: 0.875rem; }
            .stat-card .stat-value { font-size: 1.25rem; }
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.5s ease-out forwards;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .slide-in {
            animation: slideIn 0.4s ease-out forwards;
        }
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--gray-100); }
        ::-webkit-scrollbar-thumb { background: var(--gray-300); border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--gray-400); }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar-modern navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="{% url 'dashboard' %}">
                <span class="brand-icon"><i class="fas fa-gavel"></i></span>
                <span>Disciplinary System</span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center gap-1">
                    <!-- Notifications -->
                    <li class="nav-item">
                        <div class="notification-icon" id="notificationIcon">
                            <i class="fas fa-bell bell-icon"></i>
                            {% if notification_count > 0 or admin_notification_count > 0 %}
                            <span class="notification-badge" id="notificationBadge">
                                {{ notification_count|add:admin_notification_count }}
                            </span>
                            {% endif %}
                            <div class="notification-dropdown" id="notificationDropdown">
                                <div class="notification-dropdown-header">
                                    <span><i class="fas fa-bell me-2"></i>Notifications</span>
                                    <span class="badge bg-primary" id="notificationCount">{{ notification_count|add:admin_notification_count }}</span>
                                </div>
                                <div id="notificationList">
                                    {% if unread_notifications %}
                                        {% for notif in unread_notifications %}
                                        <div class="notification-item" onclick="markNotificationRead({{ notif.id }})">
                                            <div class="notif-icon {{ notif.notification_type }}">
                                                <i class="fas {% if notif.notification_type == 'critical' %}fa-exclamation-triangle{% elif notif.notification_type == 'warning' %}fa-exclamation-circle{% else %}fa-info-circle{% endif %}"></i>
                                            </div>
                                            <div class="notif-content">
                                                <div class="notif-title">{{ notif.title }}</div>
                                                <div class="notif-message">{{ notif.message|truncatechars:80 }}</div>
                                                <div class="notif-time"><i class="far fa-clock me-1"></i>{{ notif.created_at|date:"M d, H:i" }}</div>
                                            </div>
                                        </div>
                                        {% endfor %}
                                    {% endif %}
                                    
                                    {% if user.is_superuser %}
                                        {% if pending_approvals > 0 %}
                                        <div class="notification-item" onclick="location.href='{% url 'manage_users' %}?status=pending'">
                                            <div class="notif-icon warning"><i class="fas fa-user-check"></i></div>
                                            <div class="notif-content">
                                                <div class="notif-title">{{ pending_approvals }} Pending Approvals</div>
                                                <div class="notif-message">Teachers waiting for account approval</div>
                                                <div class="notif-time">Click to review</div>
                                            </div>
                                        </div>
                                        {% endif %}
                                        
                                        {% if pending_resets > 0 %}
                                        <div class="notification-item" onclick="location.href='{% url 'admin_reset_requests' %}'">
                                            <div class="notif-icon info"><i class="fas fa-key"></i></div>
                                            <div class="notif-content">
                                                <div class="notif-title">{{ pending_resets }} Password Reset Requests</div>
                                                <div class="notif-message">Teachers requesting password reset</div>
                                                <div class="notif-time">Click to review</div>
                                            </div>
                                        </div>
                                        {% endif %}
                                    {% endif %}
                                    
                                    {% if not unread_notifications and not pending_approvals and not pending_resets %}
                                    <div class="text-center py-4">
                                        <i class="fas fa-check-circle text-success" style="font-size: 2rem;"></i>
                                        <p class="text-muted mt-2 mb-0">All caught up!</p>
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </li>
                    
                    <!-- User Menu -->
                    <li class="nav-item dropdown">
                        <a class="nav-link d-flex align-items-center gap-2" href="#" role="button" data-bs-toggle="dropdown">
                            {% if user.teacher_profile.profile_picture %}
                            <img src="{{ user.teacher_profile.profile_picture.url }}" alt="Profile" 
                                 style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary);">
                            {% else %}
                            <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75rem; font-weight: 700;">
                                {{ user.get_full_name|default:user.username|slice:":1"|upper }}
                            </div>
                            {% endif %}
                            <span>{{ user.get_full_name|default:user.username }}</span>
                            {% if user.teacher_profile and not user.teacher_profile.is_approved %}
                            <span class="badge bg-warning text-dark ms-1">Pending</span>
                            {% endif %}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end shadow-lg border-0 rounded-3 py-2">
                            <li><a class="dropdown-item" href="{% url 'user_profile_settings' %}"><i class="fas fa-user-cog me-2 text-primary"></i>My Profile</a></li>
                            <li><a class="dropdown-item" href="{% url 'dashboard' %}"><i class="fas fa-tachometer-alt me-2 text-info"></i>Dashboard</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="{% url 'logout' %}"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}
    
    <div class="container py-4">
        {% if messages %}
            {% for message in messages %}
            <div class="alert-modern alert alert-{{ message.tags }} fade-in-up" role="alert">
                <span class="alert-icon">
                    {% if message.tags == 'success' %}<i class="fas fa-check-circle text-success"></i>
                    {% elif message.tags == 'error' %}<i class="fas fa-exclamation-circle text-danger"></i>
                    {% elif message.tags == 'warning' %}<i class="fas fa-exclamation-triangle text-warning"></i>
                    {% else %}<i class="fas fa-info-circle text-primary"></i>{% endif %}
                </span>
                <div>{{ message }}</div>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialize AOS
        AOS.init({ duration: 600, once: true });
        
        // Auto-dismiss alerts
        setTimeout(function() { 
            document.querySelectorAll('.alert').forEach(function(el) {
                el.style.transition = 'opacity 0.5s';
                el.style.opacity = '0';
                setTimeout(function() { el.remove(); }, 500);
            });
        }, 5000);
        
        // Notification toggle
        document.getElementById('notificationIcon')?.addEventListener('click', function(e) {
            e.stopPropagation();
            document.getElementById('notificationDropdown').classList.toggle('show');
        });
        
        document.addEventListener('click', function() {
            document.getElementById('notificationDropdown')?.classList.remove('show');
        });
        
        function markNotificationRead(id) {
            fetch('/api/notifications/read/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': '{{ csrf_token }}' } })
                .then(response => response.json())
                .then(data => { if (data.status === 'success') location.reload(); });
        }
        window.markNotificationRead = markNotificationRead;
        
        // Auto-refresh notifications
        setInterval(function() {
            fetch('/api/notifications/')
                .then(r => r.json())
                .then(data => {
                    const badge = document.getElementById('notificationBadge');
                    const count = document.getElementById('notificationCount');
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.style.display = 'block';
                        count.textContent = data.count;
                    } else {
                        badge.style.display = 'none';
                        count.textContent = '0';
                    }
                });
        }, 30000);
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"@ | Set-Content "$basePath\base.html" -Encoding UTF8

Write-Host "✅ base.html updated" -ForegroundColor Green

# ============================================
# 2. UPDATE LOGIN.HTML
# ============================================
Write-Host "`n📝 Updating login.html..." -ForegroundColor Yellow

@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Login - Disciplinary Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            padding: 1.5rem;
        }
        
        .login-wrapper {
            width: 100%;
            max-width: 440px;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 25px 60px rgba(0,0,0,0.3);
            backdrop-filter: blur(20px);
        }
        
        .login-brand {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-brand .brand-icon {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 1.75rem;
            color: white;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
        }
        
        .login-brand h1 {
            font-size: 1.5rem;
            font-weight: 800;
            color: #0f172a;
        }
        
        .login-brand p {
            color: #64748b;
            font-size: 0.875rem;
        }
        
        .form-group-modern {
            margin-bottom: 1.25rem;
        }
        
        .form-group-modern label {
            font-weight: 600;
            font-size: 0.813rem;
            color: #334155;
            margin-bottom: 0.375rem;
            display: block;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .input-wrapper .input-icon {
            position: absolute;
            left: 0.875rem;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 1rem;
        }
        
        .input-wrapper input {
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 2.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 0.9375rem;
            transition: all 0.3s;
            background: #f8fafc;
        }
        
        .input-wrapper input:focus {
            border-color: #2563eb;
            background: white;
            outline: none;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }
        
        .btn-login {
            width: 100%;
            padding: 0.875rem;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.35);
        }
        
        .login-footer {
            text-align: center;
            margin-top: 1.5rem;
            font-size: 0.875rem;
        }
        
        .login-footer a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
        }
        
        .login-footer a:hover { text-decoration: underline; }
        
        .alert-modern {
            border-radius: 12px;
            border: none;
            padding: 0.875rem 1rem;
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        @media (max-width: 480px) {
            .login-card { padding: 1.75rem; }
            .login-brand h1 { font-size: 1.25rem; }
        }
    </style>
</head>
<body>
    <div class="login-wrapper">
        <div class="login-card">
            <div class="login-brand">
                <div class="brand-icon"><i class="fas fa-gavel"></i></div>
                <h1>Disciplinary System</h1>
                <p>School Management Platform</p>
            </div>
            
            {% if messages %}
                {% for message in messages %}
                <div class="alert-modern alert alert-{{ message.tags }}">
                    <i class="fas fa-{% if message.tags == 'success' %}check-circle{% else %}exclamation-circle{% endif %}"></i>
                    {{ message }}
                </div>
                {% endfor %}
            {% endif %}
            
            {% if error %}
            <div class="alert-modern alert alert-danger">
                <i class="fas fa-exclamation-circle"></i>
                {{ error }}
            </div>
            {% endif %}
            
            <form method="post">
                {% csrf_token %}
                <div class="form-group-modern">
                    <label>Username</label>
                    <div class="input-wrapper">
                        <span class="input-icon"><i class="fas fa-user"></i></span>
                        <input type="text" name="username" placeholder="Enter your username" required autofocus>
                    </div>
                </div>
                <div class="form-group-modern">
                    <label>Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon"><i class="fas fa-lock"></i></span>
                        <input type="password" name="password" placeholder="Enter your password" required>
                    </div>
                </div>
                <button type="submit" class="btn-login">
                    <i class="fas fa-sign-in-alt me-2"></i>Sign In
                </button>
            </form>
            
            <div class="login-footer">
                <a href="/register/"><i class="fas fa-user-plus me-1"></i>Create Account</a>
                <span class="mx-2 text-muted">|</span>
                <a href="/request-reset/"><i class="fas fa-key me-1"></i>Forgot Password?</a>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"@ | Set-Content "$basePath\login.html" -Encoding UTF8

Write-Host "✅ login.html updated" -ForegroundColor Green

# ============================================
# 3. UPDATE REGISTER.HTML
# ============================================
Write-Host "`n📝 Updating register.html..." -ForegroundColor Yellow

@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Register - Disciplinary Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            padding: 1.5rem;
        }
        
        .register-wrapper {
            width: 100%;
            max-width: 520px;
        }
        
        .register-card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 25px 60px rgba(0,0,0,0.3);
        }
        
        .register-brand { text-align: center; margin-bottom: 2rem; }
        
        .register-brand .brand-icon {
            width: 64px; height: 64px;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 1rem; font-size: 1.75rem; color: white;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
        }
        
        .register-brand h1 { font-size: 1.5rem; font-weight: 800; color: #0f172a; }
        .register-brand p { color: #64748b; font-size: 0.875rem; }
        
        .form-group-modern { margin-bottom: 1rem; }
        .form-group-modern label { font-weight: 600; font-size: 0.813rem; color: #334155; margin-bottom: 0.375rem; display: block; }
        
        .input-wrapper { position: relative; }
        .input-wrapper .input-icon {
            position: absolute; left: 0.875rem; top: 50%;
            transform: translateY(-50%); color: #94a3b8; font-size: 1rem;
        }
        
        .input-wrapper input, .input-wrapper select {
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 2.75rem;
            border: 2px solid #e2e8f0; border-radius: 12px;
            font-size: 0.9375rem; transition: all 0.3s;
            background: #f8fafc;
            appearance: none;
            -webkit-appearance: none;
        }
        
        .input-wrapper input:focus, .input-wrapper select:focus {
            border-color: #2563eb; background: white;
            outline: none; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }
        
        .input-wrapper select { padding-right: 2.5rem; }
        .input-wrapper .select-arrow {
            position: absolute; right: 0.875rem; top: 50%;
            transform: translateY(-50%); color: #94a3b8;
            pointer-events: none;
        }
        
        .btn-register {
            width: 100%; padding: 0.875rem;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white; border: none; border-radius: 12px;
            font-size: 1rem; font-weight: 600; transition: all 0.3s;
            cursor: pointer;
        }
        .btn-register:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(37, 99, 235, 0.35); }
        
        .role-info {
            background: #f1f5f9; padding: 0.75rem 1rem; border-radius: 10px;
            font-size: 0.813rem; color: #475569; margin-top: 0.25rem;
        }
        .role-info i { color: #2563eb; margin-right: 0.5rem; }
        
        .register-footer { text-align: center; margin-top: 1.5rem; font-size: 0.875rem; }
        .register-footer a { color: #2563eb; text-decoration: none; font-weight: 600; }
        .register-footer a:hover { text-decoration: underline; }
        
        .alert-modern {
            border-radius: 12px; border: none; padding: 0.875rem 1rem;
            font-size: 0.875rem; display: flex; align-items: center; gap: 0.5rem;
        }
        
        @media (max-width: 480px) {
            .register-card { padding: 1.75rem; }
            .register-brand h1 { font-size: 1.25rem; }
        }
    </style>
</head>
<body>
    <div class="register-wrapper">
        <div class="register-card">
            <div class="register-brand">
                <div class="brand-icon"><i class="fas fa-user-plus"></i></div>
                <h1>Create Account</h1>
                <p>Join the Disciplinary Management System</p>
            </div>
            
            {% if messages %}
                {% for message in messages %}
                <div class="alert-modern alert alert-{{ message.tags }}">
                    <i class="fas fa-{% if message.tags == 'success' %}check-circle{% else %}exclamation-circle{% endif %}"></i>
                    {{ message }}
                </div>
                {% endfor %}
            {% endif %}
            
            {% if error %}
            <div class="alert-modern alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> {{ error }}
            </div>
            {% endif %}
            
            <form method="post">
                {% csrf_token %}
                <div class="row g-2">
                    <div class="col-12">
                        <div class="form-group-modern">
                            <label>Full Name</label>
                            <div class="input-wrapper">
                                <span class="input-icon"><i class="fas fa-user"></i></span>
                                <input type="text" name="full_name" placeholder="Enter your full name" required>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group-modern">
                            <label>Username</label>
                            <div class="input-wrapper">
                                <span class="input-icon"><i class="fas fa-user-tag"></i></span>
                                <input type="text" name="username" placeholder="Choose username" required>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group-modern">
                            <label>Email</label>
                            <div class="input-wrapper">
                                <span class="input-icon"><i class="fas fa-envelope"></i></span>
                                <input type="email" name="email" placeholder="your@email.com" required>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group-modern">
                            <label>Password</label>
                            <div class="input-wrapper">
                                <span class="input-icon"><i class="fas fa-lock"></i></span>
                                <input type="password" name="password" placeholder="Min 8 characters" required>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group-modern">
                            <label>Confirm Password</label>
                            <div class="input-wrapper">
                                <span class="input-icon"><i class="fas fa-lock"></i></span>
                                <input type="password" name="password2" placeholder="Confirm password" required>
                            </div>
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="form-group-modern">
                            <label>Role</label>
                            <div class="input-wrapper">
                                <span class="input-icon"><i class="fas fa-user-graduate"></i></span>
                                <select name="role" required>
                                    <option value="teacher">Teacher</option>
                                    <option value="class_teacher">Class Teacher</option>
                                </select>
                                <span class="select-arrow"><i class="fas fa-chevron-down"></i></span>
                            </div>
                            <div class="role-info">
                                <i class="fas fa-info-circle"></i>
                                <strong>Class Teacher:</strong> Select stream after registration, wait for admin approval.
                                <br>
                                <i class="fas fa-info-circle"></i>
                                <strong>Teacher:</strong> Start reporting students immediately.
                            </div>
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn-register mt-2">
                    <i class="fas fa-user-plus me-2"></i>Create Account
                </button>
            </form>
            
            <div class="register-footer">
                Already have an account? <a href="{% url 'login' %}">Sign In</a>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"@ | Set-Content "$basePath\register.html" -Encoding UTF8

Write-Host "✅ register.html updated" -ForegroundColor Green

# ============================================
# 4. UPDATE ADMIN_DASHBOARD.HTML
# ============================================
Write-Host "`n📝 Updating admin_dashboard.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Admin Dashboard{% endblock %}

{% block content %}
<!-- Pending Approvals Alert -->
{% if pending_approvals > 0 %}
<div class="alert-modern alert alert-warning mb-4" data-aos="fade-up">
    <span class="alert-icon"><i class="fas fa-user-clock text-warning"></i></span>
    <div>
        <strong>{{ pending_approvals }}</strong> teacher(s) waiting for approval.
        <a href="{% url 'manage_users' %}?status=pending" class="btn btn-sm btn-warning ms-2">Review Now</a>
    </div>
</div>
{% endif %}

<!-- Stats Grid -->
<div class="stat-grid" data-aos="fade-up">
    <div class="stat-card">
        <div class="stat-bg-icon"><i class="fas fa-users"></i></div>
        <div class="stat-icon primary"><i class="fas fa-users"></i></div>
        <div class="stat-value">{{ total_students }}</div>
        <div class="stat-label">Total Students</div>
    </div>
    <div class="stat-card">
        <div class="stat-bg-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="stat-icon danger"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="stat-value">{{ critical_students }}</div>
        <div class="stat-label">Critical Cases</div>
    </div>
    <div class="stat-card">
        <div class="stat-bg-icon"><i class="fas fa-flag"></i></div>
        <div class="stat-icon success"><i class="fas fa-flag"></i></div>
        <div class="stat-value">{{ total_reports }}</div>
        <div class="stat-label">Total Reports</div>
        <div class="stat-change up">{{ reports_today }} today</div>
    </div>
    <div class="stat-card">
        <div class="stat-bg-icon"><i class="fas fa-user-clock"></i></div>
        <div class="stat-icon info"><i class="fas fa-user-clock"></i></div>
        <div class="stat-value">{{ online_count }}</div>
        <div class="stat-label">Online Teachers</div>
    </div>
</div>

<!-- Management Actions -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-cog"></i></span>
        System Management
    </div>
    <div class="card-body p-3">
        <div class="d-flex flex-wrap gap-2">
            <a href="{% url 'manage_users' %}" class="btn-modern btn-modern-primary">
                <i class="fas fa-users"></i> Manage Users
                {% if pending_approvals > 0 %}<span class="badge bg-light text-dark ms-1">{{ pending_approvals }}</span>{% endif %}
            </a>
            <a href="{% url 'admin_reset_requests' %}" class="btn-modern btn-modern-warning">
                <i class="fas fa-key"></i> Password Resets
                <span class="badge bg-light text-dark ms-1" id="resetCount">0</span>
            </a>
            <a href="{% url 'admin_profile' %}" class="btn-modern btn-modern-secondary">
                <i class="fas fa-user-cog"></i> My Profile
            </a>
        </div>
    </div>
</div>

<!-- Add Student -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-plus-circle"></i></span>
        Add Student
    </div>
    <div class="card-body p-4">
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="add_student">
            <div class="row g-3">
                <div class="col-md-3"><input type="text" name="admission_number" class="form-control-modern" placeholder="Admission Number" required></div>
                <div class="col-md-3"><input type="text" name="name" class="form-control-modern" placeholder="Full Name" required></div>
                <div class="col-md-2">
                    <select name="stream" class="form-control-modern" required>
                        <option value="">Stream</option>
                        {% for stream_key, stream_name in streams %}
                        <option value="{{ stream_key }}">{{ stream_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <select name="form" class="form-control-modern" required>
                        <option value="">Form</option>
                        {% for form_key, form_name in forms %}
                        <option value="{{ form_key }}">{{ form_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2"><button type="submit" class="btn-modern btn-modern-primary w-100"><i class="fas fa-plus"></i> Add</button></div>
            </div>
        </form>
    </div>
</div>

<!-- Students Table -->
<div class="card-modern" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-search"></i></span>
        Students
    </div>
    <div class="card-body p-3">
        <form method="get" class="row g-2 mb-3">
            <div class="col-md-3"><input type="text" name="search" class="form-control-modern" placeholder="Search..." value="{{ search_query }}"></div>
            <div class="col-md-2">
                <select name="stream" class="form-control-modern">
                    <option value="">All Streams</option>
                    {% for stream_key, stream_name in streams %}
                    <option value="{{ stream_key }}" {% if stream_filter == stream_key %}selected{% endif %}>{{ stream_name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <select name="form" class="form-control-modern">
                    <option value="">All Forms</option>
                    {% for form_key, form_name in forms %}
                    <option value="{{ form_key }}" {% if form_filter == form_key %}selected{% endif %}>{{ form_name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <select name="risk" class="form-control-modern">
                    <option value="">All Status</option>
                    <option value="critical" {% if risk_filter == 'critical' %}selected{% endif %}>Critical</option>
                    <option value="warning" {% if risk_filter == 'warning' %}selected{% endif %}>Warning</option>
                    <option value="good" {% if risk_filter == 'good' %}selected{% endif %}>Good</option>
                </select>
            </div>
            <div class="col-md-3"><button type="submit" class="btn-modern btn-modern-primary w-100"><i class="fas fa-filter"></i> Filter</button></div>
        </form>
        
        <div class="table-responsive">
            <table class="table-modern">
                <thead><tr>
                    <th>Admission</th><th>Name</th><th>Stream</th><th>Form</th>
                    <th>Reports</th><th>Risk Score</th><th>Status</th><th>Action</th>
                </tr></thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.admission_number }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.stream.get_name_display }}</td>
                        <td>{{ student.form }}</td>
                        <td><span class="badge-modern {% if student.total_reports >= 20 %}badge-critical{% else %}badge-info{% endif %}">{{ student.total_reports }}</span></td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <div class="progress-modern"><div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #ef4444, #dc2626){% elif student.risk_score >= 30 %}linear-gradient(135deg, #f59e0b, #d97706){% else %}linear-gradient(135deg, #10b981, #059669){% endif %}"></div></div>
                                <span class="fw-bold" style="font-size:0.813rem;">{{ student.risk_score }}%</span>
                            </div>
                        </td>
                        <td>
                            {% if student.is_critical %}<span class="badge-modern badge-critical">Critical</span>
                            {% elif student.risk_score >= 30 %}<span class="badge-modern badge-warning">Warning</span>
                            {% else %}<span class="badge-modern badge-success">Good</span>{% endif %}
                        </td>
                        <td><a href="{% url 'student_profile' student.id %}" class="btn-modern btn-modern-primary btn-modern-sm"><i class="fas fa-eye"></i></a></td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="8" class="text-center py-4 text-muted">No students found</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        {% if students.has_other_pages %}
        <nav class="mt-3"><ul class="pagination justify-content-center">
            {% if students.has_previous %}<li class="page-item"><a class="page-link" href="?page={{ students.previous_page_number }}&search={{ search_query }}&stream={{ stream_filter }}&form={{ form_filter }}&risk={{ risk_filter }}">Prev</a></li>{% endif %}
            {% for i in students.paginator.page_range %}<li class="page-item {% if students.number == i %}active{% endif %}"><a class="page-link" href="?page={{ i }}&search={{ search_query }}&stream={{ stream_filter }}&form={{ form_filter }}&risk={{ risk_filter }}">{{ i }}</a></li>{% endfor %}
            {% if students.has_next %}<li class="page-item"><a class="page-link" href="?page={{ students.next_page_number }}&search={{ search_query }}&stream={{ stream_filter }}&form={{ form_filter }}&risk={{ risk_filter }}">Next</a></li>{% endif %}
        </ul></nav>
        {% endif %}
    </div>
</div>
{% endblock %}
"@ | Set-Content "$basePath\admin_dashboard.html" -Encoding UTF8

Write-Host "✅ admin_dashboard.html updated" -ForegroundColor Green

# ============================================
# 5. UPDATE TEACHER_DASHBOARD.HTML
# ============================================
Write-Host "`n📝 Updating teacher_dashboard.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Teacher Dashboard{% endblock %}

{% block content %}
<div class="row g-2 mb-3">
    <div class="col-12">
        <div class="card-modern">
            <div class="card-body p-3">
                <div class="d-flex flex-wrap gap-2">
                    <a href="{% url 'user_profile_settings' %}" class="btn-modern btn-modern-secondary"><i class="fas fa-user-cog"></i> Profile</a>
                    <a href="{% url 'teacher_dashboard' %}" class="btn-modern btn-modern-primary"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Search -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-search"></i></span>
        Search Student
    </div>
    <div class="card-body p-4">
        <div class="search-box">
            <span class="search-icon"><i class="fas fa-search"></i></span>
            <input type="text" id="searchStudent" placeholder="Search by name or admission number...">
        </div>
        <div id="searchResults" class="mt-3"></div>
    </div>
</div>

<!-- Students -->
<div class="card-modern" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-list"></i></span>
        All Students
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table-modern">
                <thead><tr>
                    <th>Admission</th><th>Name</th><th>Stream</th><th>Form</th>
                    <th>Reports</th><th>Risk Score</th><th>Action</th>
                </tr></thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.admission_number }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.stream.get_name_display }}</td>
                        <td>{{ student.form }}</td>
                        <td>{{ student.total_reports }}</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <div class="progress-modern"><div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #ef4444, #dc2626){% elif student.risk_score >= 30 %}linear-gradient(135deg, #f59e0b, #d97706){% else %}linear-gradient(135deg, #10b981, #059669){% endif %}"></div></div>
                                <span class="fw-bold" style="font-size:0.813rem;">{{ student.risk_score }}%</span>
                            </div>
                        </td>
                        <td>
                            <button class="btn-modern btn-modern-primary btn-modern-sm" onclick="openReportModal({{ student.id }}, '{{ student.name }}')"><i class="fas fa-flag"></i> Report</button>
                            <a href="{% url 'student_profile' student.id %}" class="btn-modern btn-modern-secondary btn-modern-sm"><i class="fas fa-eye"></i></a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="7" class="text-center py-4 text-muted">No students found</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Report Modal -->
<div class="modal fade" id="reportModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4">
            <div class="modal-header border-0">
                <h5 class="modal-title fw-bold"><i class="fas fa-flag text-primary me-2"></i>Report Student</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="post" action="{% url 'teacher_dashboard' %}">
                {% csrf_token %}
                <input type="hidden" name="action" value="report_student">
                <input type="hidden" name="student_id" id="reportStudentId">
                <div class="modal-body">
                    <p class="mb-3">Reporting: <strong id="reportStudentName"></strong></p>
                    {% include 'includes/custom_case.html' %}
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn-modern btn-modern-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-paper-plane"></i> Submit</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
function openReportModal(id, name) {
    document.getElementById('reportStudentId').value = id;
    document.getElementById('reportStudentName').textContent = name;
    new bootstrap.Modal(document.getElementById('reportModal')).show();
}

var searchTimeout;
$('#searchStudent').on('keyup', function() {
    clearTimeout(searchTimeout);
    var query = $(this).val();
    if (query.length < 2) { $('#searchResults').html(''); return; }
    searchTimeout = setTimeout(function() {
        $.get('/api/search-students/', { q: query }, function(data) {
            if (data.students.length > 0) {
                var html = '<h6 class="mb-2">Results:</h6>';
                data.students.forEach(function(s) {
                    html += '<div class="card p-3 mb-2"><div class="d-flex justify-content-between align-items-center"><div><strong>'+s.name+'</strong><br><small>'+s.admission_number+' | '+s.stream+' | Risk: '+s.risk_score+'%</small></div><div><button class="btn-modern btn-modern-primary btn-modern-sm" onclick="openReportModal('+s.id+', \''+s.name+'\')"><i class="fas fa-flag"></i></button> <a href="/student/'+s.id+'/" class="btn-modern btn-modern-secondary btn-modern-sm"><i class="fas fa-eye"></i></a></div></div></div>';
                });
                $('#searchResults').html(html);
            } else { $('#searchResults').html('<div class="alert alert-info">No students found</div>'); }
        });
    }, 500);
});
</script>
{% endblock %}
"@ | Set-Content "$basePath\teacher_dashboard.html" -Encoding UTF8

Write-Host "✅ teacher_dashboard.html updated" -ForegroundColor Green

# ============================================
# 6. UPDATE CLASS_TEACHER_DASHBOARD.HTML
# ============================================
Write-Host "`n📝 Updating class_teacher_dashboard.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Class Teacher Dashboard{% endblock %}

{% block content %}
<div class="alert-modern alert alert-info mb-4" data-aos="fade-up">
    <span class="alert-icon"><i class="fas fa-chalkboard-teacher"></i></span>
    <div>
        <strong>{{ assigned_stream.get_name_display }}</strong> - {{ assigned_form|default:"All Forms" }}
        {% if not user.teacher_profile.is_approved %}<span class="badge-modern badge-warning ms-2">Pending Approval</span>{% endif %}
    </div>
</div>

<!-- Quick Actions -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-body p-3">
        <div class="d-flex flex-wrap gap-2">
            <a href="{% url 'user_profile_settings' %}" class="btn-modern btn-modern-secondary"><i class="fas fa-user-cog"></i> Profile</a>
            <a href="{% url 'class_teacher_dashboard' %}" class="btn-modern btn-modern-primary"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
        </div>
    </div>
</div>

<!-- Stats -->
<div class="stat-grid" data-aos="fade-up">
    <div class="stat-card"><div class="stat-bg-icon"><i class="fas fa-users"></i></div><div class="stat-icon primary"><i class="fas fa-users"></i></div><div class="stat-value">{{ class_stats.total }}</div><div class="stat-label">My Students</div></div>
    <div class="stat-card"><div class="stat-bg-icon"><i class="fas fa-exclamation-triangle"></i></div><div class="stat-icon danger"><i class="fas fa-exclamation-triangle"></i></div><div class="stat-value">{{ class_stats.critical }}</div><div class="stat-label">Critical Cases</div></div>
    <div class="stat-card"><div class="stat-bg-icon"><i class="fas fa-chart-line"></i></div><div class="stat-icon warning"><i class="fas fa-chart-line"></i></div><div class="stat-value">{{ class_stats.avg_risk|floatformat:0 }}%</div><div class="stat-label">Average Risk</div></div>
    <div class="stat-card"><div class="stat-bg-icon"><i class="fas fa-bell"></i></div><div class="stat-icon info"><i class="fas fa-bell"></i></div><div class="stat-value">{{ notification_count }}</div><div class="stat-label">Notifications</div></div>
</div>

<!-- Add Student -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-plus-circle"></i></span>
        Add Student to {{ assigned_stream.get_name_display }}
    </div>
    <div class="card-body p-4">
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="add_student">
            <div class="row g-3">
                <div class="col-md-3"><input type="text" name="admission_number" class="form-control-modern" placeholder="Admission Number" required></div>
                <div class="col-md-3"><input type="text" name="name" class="form-control-modern" placeholder="Full Name" required></div>
                <div class="col-md-2">
                    <select name="form" class="form-control-modern" required>
                        <option value="">Form</option>
                        {% for form_key, form_name in forms %}<option value="{{ form_key }}" {% if assigned_form == form_key %}selected{% endif %}>{{ form_name }}</option>{% endfor %}
                    </select>
                </div>
                <div class="col-md-2"><input type="number" name="year" class="form-control-modern" placeholder="Year" value="2026"></div>
                <div class="col-md-2"><button type="submit" class="btn-modern btn-modern-primary w-100"><i class="fas fa-plus"></i> Add</button></div>
            </div>
        </form>
    </div>
</div>

<!-- Search -->
<div class="card-modern mb-4" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-search"></i></span>
        Search & Report Students
    </div>
    <div class="card-body p-4">
        <div class="search-box">
            <span class="search-icon"><i class="fas fa-search"></i></span>
            <input type="text" id="searchStudent" placeholder="Search by name or admission number...">
        </div>
        <div id="searchResults" class="mt-3"></div>
    </div>
</div>

<!-- My Students -->
<div class="card-modern" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-chalkboard"></i></span>
        My Students - {{ assigned_stream.get_name_display }}
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table-modern">
                <thead><tr>
                    <th>Admission</th><th>Name</th><th>Form</th>
                    <th>Reports</th><th>Risk Score</th><th>Status</th><th>Action</th>
                </tr></thead>
                <tbody>
                    {% for student in my_students %}
                    <tr>
                        <td>{{ student.admission_number }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.form }}</td>
                        <td>{{ student.total_reports }}</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <div class="progress-modern"><div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #ef4444, #dc2626){% elif student.risk_score >= 30 %}linear-gradient(135deg, #f59e0b, #d97706){% else %}linear-gradient(135deg, #10b981, #059669){% endif %}"></div></div>
                                <span class="fw-bold" style="font-size:0.813rem;">{{ student.risk_score }}%</span>
                            </div>
                        </td>
                        <td>
                            {% if student.is_critical %}<span class="badge-modern badge-critical">Critical</span>
                            {% elif student.risk_score >= 30 %}<span class="badge-modern badge-warning">Warning</span>
                            {% else %}<span class="badge-modern badge-success">Good</span>{% endif %}
                        </td>
                        <td>
                            <button class="btn-modern btn-modern-primary btn-modern-sm" onclick="openReportModal({{ student.id }}, '{{ student.name }}')"><i class="fas fa-flag"></i></button>
                            <a href="{% url 'student_profile' student.id %}" class="btn-modern btn-modern-secondary btn-modern-sm"><i class="fas fa-eye"></i></a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="7" class="text-center py-4 text-muted">No students in your class</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Report Modal -->
<div class="modal fade" id="reportModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4">
            <div class="modal-header border-0">
                <h5 class="modal-title fw-bold"><i class="fas fa-flag text-primary me-2"></i>Report Student</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="post" action="{% url 'class_teacher_dashboard' %}">
                {% csrf_token %}
                <input type="hidden" name="action" value="report_student">
                <input type="hidden" name="student_id" id="reportStudentId">
                <div class="modal-body">
                    <p class="mb-3">Reporting: <strong id="reportStudentName"></strong></p>
                    {% include 'includes/custom_case.html' %}
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn-modern btn-modern-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-paper-plane"></i> Submit</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
function openReportModal(id, name) {
    document.getElementById('reportStudentId').value = id;
    document.getElementById('reportStudentName').textContent = name;
    new bootstrap.Modal(document.getElementById('reportModal')).show();
}

var searchTimeout;
$('#searchStudent').on('keyup', function() {
    clearTimeout(searchTimeout);
    var query = $(this).val();
    if (query.length < 2) { $('#searchResults').html(''); return; }
    searchTimeout = setTimeout(function() {
        $.get('/api/search-students/', { q: query }, function(data) {
            if (data.students.length > 0) {
                var html = '<h6 class="mb-2">Results:</h6>';
                data.students.forEach(function(s) {
                    html += '<div class="card p-3 mb-2"><div class="d-flex justify-content-between align-items-center"><div><strong>'+s.name+'</strong><br><small>'+s.admission_number+' | '+s.stream+' | Risk: '+s.risk_score+'%</small></div><div><button class="btn-modern btn-modern-primary btn-modern-sm" onclick="openReportModal('+s.id+', \''+s.name+'\')"><i class="fas fa-flag"></i></button> <a href="/student/'+s.id+'/" class="btn-modern btn-modern-secondary btn-modern-sm"><i class="fas fa-eye"></i></a></div></div></div>';
                });
                $('#searchResults').html(html);
            } else { $('#searchResults').html('<div class="alert alert-info">No students found</div>'); }
        });
    }, 500);
});
</script>
{% endblock %}
"@ | Set-Content "$basePath\class_teacher_dashboard.html" -Encoding UTF8

Write-Host "✅ class_teacher_dashboard.html updated" -ForegroundColor Green

# ============================================
# 7. UPDATE STUDENT_PROFILE.HTML
# ============================================
Write-Host "`n📝 Updating student_profile.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}{{ student.name }} - Profile{% endblock %}

{% block content %}
<div class="row g-4">
    <div class="col-lg-4" data-aos="fade-right">
        <!-- Profile Card -->
        <div class="card-modern">
            <div class="card-header-modern text-center">
                <div class="mb-3">
                    {% if student.profile_picture %}
                    <img src="{{ student.profile_picture.url }}" alt="{{ student.name }}" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid white;">
                    {% else %}
                    <div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #7c3aed); display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 3px solid white;">
                        <i class="fas fa-user-graduate fa-3x" style="color: white;"></i>
                    </div>
                    {% endif %}
                </div>
                <h4 class="mb-0">{{ student.name }}</h4>
                <small class="text-light">{{ student.admission_number }}</small>
                {% if user.is_superuser or user.teacher_profile.assigned_stream == student.stream %}
                <div class="mt-2"><a href="{% url 'edit_student' student.id %}" class="btn btn-sm btn-light"><i class="fas fa-edit"></i> Edit</a></div>
                {% endif %}
            </div>
            <div class="card-body p-4">
                <div class="mb-3"><label class="text-muted">Stream</label><p class="mb-0 fw-bold">{{ student.stream.get_name_display }}</p></div>
                <div class="mb-3"><label class="text-muted">Form</label><p class="mb-0 fw-bold">{{ student.form }}</p></div>
                <div class="mb-3"><label class="text-muted">Year</label><p class="mb-0 fw-bold">{{ student.year }}</p></div>
                <div class="mb-3"><label class="text-muted">Total Reports</label><p class="mb-0 fw-bold">{{ total_reports }}</p></div>
                <div class="mb-3">
                    <label class="text-muted">Risk Score</label>
                    <div class="progress-modern mb-2"><div class="progress-bar-modern" style="width: {{ student.risk_score }}%; background: {% if student.risk_score >= 60 %}linear-gradient(135deg, #ef4444, #dc2626){% elif student.risk_score >= 30 %}linear-gradient(135deg, #f59e0b, #d97706){% else %}linear-gradient(135deg, #10b981, #059669){% endif %}"></div></div>
                    <h3 class="{% if student.is_critical %}text-danger{% else %}text-success{% endif %}">{{ student.risk_score }}%</h3>
                </div>
                {% if student.optional_notes %}
                <div class="alert alert-info"><i class="fas fa-sticky-note"></i> {{ student.optional_notes }}</div>
                {% endif %}
                <div class="text-center">
                    <span class="badge-modern {% if student.is_critical %}badge-critical{% elif student.risk_score >= 30 %}badge-warning{% else %}badge-success{% endif %}" style="font-size:1rem; padding:0.5rem 1.5rem;">
                        {{ student.risk_level }}
                    </span>
                </div>
            </div>
        </div>
        
        <!-- Category Breakdown -->
        <div class="card-modern mt-4" data-aos="fade-right">
            <div class="card-header-modern">
                <span class="header-icon"><i class="fas fa-chart-pie"></i></span>
                Offense Categories
            </div>
            <div class="card-body p-4">
                {% if category_breakdown %}
                <canvas id="categoryChart" height="200"></canvas>
                <div class="mt-3">{% for cat in category_breakdown %}<div class="d-flex justify-content-between mb-2"><span>{{ cat.category__name }}</span><span class="badge-modern badge-info">{{ cat.count }}x</span></div>{% endfor %}</div>
                {% else %}<p class="text-muted text-center">No categories</p>{% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-lg-8" data-aos="fade-left">
        <!-- Timeline -->
        <div class="card-modern mb-4">
            <div class="card-header-modern">
                <span class="header-icon"><i class="fas fa-chart-line"></i></span>
                Risk Timeline
            </div>
            <div class="card-body p-4">
                {% if timeline %}<canvas id="timelineChart" height="150"></canvas>{% else %}<p class="text-muted text-center">No data</p>{% endif %}
            </div>
        </div>
        
        <!-- Reports -->
        <div class="card-modern">
            <div class="card-header-modern">
                <span class="header-icon"><i class="fas fa-history"></i></span>
                Report History <span class="badge bg-light text-dark ms-2">{{ total_reports }}</span>
            </div>
            <div class="card-body p-0">
                {% if reports %}
                <div class="table-responsive">
                    <table class="table-modern">
                        <thead><tr><th>Date</th><th>Category</th><th>Reported By</th><th>Points</th><th>Rating</th></tr></thead>
                        <tbody>{% for report in reports %}<tr>
                            <td>{{ report.reported_at|date:"Y-m-d H:i" }}</td>
                            <td><span class="badge-modern badge-critical">{{ report.category.name }}</span></td>
                            <td>{{ report.reported_by.get_full_name|default:report.reported_by.username }}</td>
                            <td class="text-danger">+{{ report.points }}</td>
                            <td><span class="badge-modern {% if report.rating == 'VERY_SERIOUS' %}badge-critical{% elif report.rating == 'SERIOUS' %}badge-warning{% else %}badge-info{% endif %}">{{ report.get_rating_display }}</span></td>
                        </tr>{% endfor %}</tbody>
                    </table>
                </div>
                {% else %}<div class="text-center py-4 text-muted"><i class="fas fa-inbox fa-2x mb-2 d-block"></i>No reports</div>{% endif %}
            </div>
        </div>
    </div>
</div>

<script>
{% if category_breakdown %}
new Chart(document.getElementById('categoryChart'), {
    type: 'pie',
    data: {
        labels: {{ category_breakdown|safe }}.map(c => c.category__name),
        datasets: [{ data: {{ category_breakdown|safe }}.map(c => c.count), backgroundColor: ['#2563eb','#7c3aed','#10b981','#f59e0b','#ef4444'] }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
});
{% endif %}
{% if timeline %}
new Chart(document.getElementById('timelineChart'), {
    type: 'line',
    data: {
        labels: {{ timeline|safe }}.map(t => t.date),
        datasets: [{ label: 'Points', data: {{ timeline|safe }}.map(t => t.points), borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.1)', fill: true, tension: 0.4 }]
    },
    options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
});
{% endif %}
</script>
{% endblock %}
"@ | Set-Content "$basePath\student_profile.html" -Encoding UTF8

Write-Host "✅ student_profile.html updated" -ForegroundColor Green

# ============================================
# 8. UPDATE USER_PROFILE.HTML
# ============================================
Write-Host "`n📝 Updating user_profile.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}My Profile Settings{% endblock %}

{% block extra_css %}
<style>
    .profile-pic-container { position: relative; display: inline-block; }
    .profile-pic-container img { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 3px solid #2563eb; }
    .profile-pic-placeholder { width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #7c3aed); display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 3px solid #2563eb; }
    .profile-pic-placeholder i { font-size: 4rem; color: white; }
    .role-badge { display: inline-block; padding: 4px 16px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .role-admin { background: #fef2f2; color: #ef4444; }
    .role-class-teacher { background: #eff6ff; color: #2563eb; }
    .role-teacher { background: #ecfdf5; color: #10b981; }
    .form-section { border-bottom: 1px solid #e2e8f0; padding-bottom: 1.5rem; margin-bottom: 1.5rem; }
    .form-section:last-child { border-bottom: none; margin-bottom: 0; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card-modern" data-aos="fade-up">
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #2563eb, #7c3aed); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                        <i class="fas fa-user-cog fa-2x text-white"></i>
                    </div>
                    <h2 class="fw-bold">My Profile</h2>
                    <span class="role-badge 
                        {% if user.is_superuser %}role-admin
                        {% elif is_class_teacher %}role-class-teacher
                        {% else %}role-teacher{% endif %}">
                        <i class="fas fa-{% if user.is_superuser %}crown{% elif is_class_teacher %}chalkboard-teacher{% else %}user-graduate{% endif %} me-1"></i>
                        {% if user.is_superuser %}Administrator{% elif is_class_teacher %}Class Teacher{% else %}Teacher{% endif %}
                    </span>
                </div>

                <!-- Profile Picture -->
                <div class="form-section">
                    <h5><i class="fas fa-camera text-primary me-2"></i>Profile Picture</h5>
                    <div class="row align-items-center g-3">
                        <div class="col-md-3 text-center">
                            <div class="profile-pic-container">
                                {% if user.teacher_profile.profile_picture %}
                                <img src="{{ user.teacher_profile.profile_picture.url }}" alt="Profile">
                                {% else %}
                                <div class="profile-pic-placeholder"><i class="fas fa-user"></i></div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-9">
                            <form method="post" enctype="multipart/form-data" action="{% url 'upload_profile_picture' %}">
                                {% csrf_token %}
                                <div class="mb-3"><label class="form-label-modern">Upload New Picture</label><input type="file" name="profile_picture" class="form-control-modern" accept="image/*"></div>
                                <button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-upload"></i> Upload</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Account Info -->
                <div class="form-section">
                    <h5><i class="fas fa-info-circle text-primary me-2"></i>Account Information</h5>
                    <div class="row">
                        <div class="col-md-6"><p><strong>Username:</strong> {{ user.username }}</p></div>
                        <div class="col-md-6"><p><strong>Email:</strong> {{ user.email|default:"Not set" }}</p></div>
                        <div class="col-md-6"><p><strong>Full Name:</strong> {{ user.get_full_name|default:"Not set" }}</p></div>
                        {% if profile %}<div class="col-md-6"><p><strong>Stream:</strong> {{ profile.assigned_stream.get_name_display|default:"Not assigned" }}</p></div>{% endif %}
                    </div>
                </div>

                <!-- Update Name -->
                <div class="form-section">
                    <h5><i class="fas fa-user-edit text-primary me-2"></i>Update Full Name</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_full_name">
                        <div class="row g-2">
                            <div class="col-md-5"><input type="text" name="first_name" class="form-control-modern" value="{{ user.first_name }}" placeholder="First Name"></div>
                            <div class="col-md-5"><input type="text" name="last_name" class="form-control-modern" value="{{ user.last_name }}" placeholder="Last Name"></div>
                            <div class="col-md-2"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-save"></i> Update Name</button></div>
                        </div>
                    </form>
                </div>

                <!-- Change Username -->
                <div class="form-section">
                    <h5><i class="fas fa-user-tag text-primary me-2"></i>Change Username</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_username">
                        <div class="row g-2">
                            <div class="col-md-8"><input type="text" name="new_username" class="form-control-modern" value="{{ user.username }}" required></div>
                            <div class="col-md-4"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-save"></i> Change Username</button></div>
                        </div>
                    </form>
                </div>

                <!-- Change Email -->
                <div class="form-section">
                    <h5><i class="fas fa-envelope text-primary me-2"></i>Change Email</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_email">
                        <div class="row g-2">
                            <div class="col-md-8"><input type="email" name="new_email" class="form-control-modern" value="{{ user.email|default:'' }}" required></div>
                            <div class="col-md-4"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-save"></i> Change Email</button></div>
                        </div>
                    </form>
                </div>

                <!-- Change Password -->
                <div class="form-section">
                    <h5><i class="fas fa-key text-warning me-2"></i>Change Password</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_password">
                        <div class="row g-2">
                            <div class="col-12"><input type="password" name="current_password" class="form-control-modern" placeholder="Current Password" required></div>
                            <div class="col-md-6"><input type="password" name="new_password" class="form-control-modern" placeholder="New Password (min 8 chars)" required></div>
                            <div class="col-md-6"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Confirm Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-warning"><i class="fas fa-save"></i> Change Password</button></div>
                        </div>
                    </form>
                </div>

                <div class="text-center mt-3"><a href="{% url 'dashboard' %}" class="btn-modern btn-modern-secondary"><i class="fas fa-arrow-left"></i> Back to Dashboard</a></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@ | Set-Content "$basePath\user_profile.html" -Encoding UTF8

Write-Host "✅ user_profile.html updated" -ForegroundColor Green

# ============================================
# 9. UPDATE INCLUDES/CUSTOM_CASE.HTML
# ============================================
Write-Host "`n📝 Updating includes/custom_case.html..." -ForegroundColor Yellow

@"
<div class="mb-3">
    <label class="form-label-modern">Report Type</label>
    <div class="d-flex gap-3">
        <div class="form-check">
            <input class="form-check-input" type="radio" name="report_type" id="standardReport" value="standard" checked onclick="toggleCustomCase(false)">
            <label class="form-check-label" for="standardReport">Standard Offense</label>
        </div>
        <div class="form-check">
            <input class="form-check-input" type="radio" name="report_type" id="customReport" value="custom" onclick="toggleCustomCase(true)">
            <label class="form-check-label" for="customReport">Custom Case</label>
        </div>
    </div>
</div>

<!-- Standard Category -->
<div id="standardCategoryDiv">
    <div class="mb-3">
        <label class="form-label-modern">Offense Category</label>
        <select name="category_id" class="form-control-modern" id="categorySelect">
            <option value="">Select a category...</option>
            {% for category in categories %}
            <option value="{{ category.id }}">{{ category.name }} (+{{ category.points }} points)</option>
            {% endfor %}
            <option value="custom">-- Custom Case --</option>
        </select>
    </div>
</div>

<!-- Custom Case -->
<div id="customCaseDiv" style="display: none;">
    <div class="mb-3">
        <label class="form-label-modern">Custom Case Description</label>
        <input type="text" name="custom_case" class="form-control-modern" placeholder="Describe the custom case..." id="customCaseInput">
        <small class="text-muted">Example: "Disrespecting school property", "Bullying", etc.</small>
    </div>
</div>

<!-- Severity -->
<div class="mb-3">
    <label class="form-label-modern">Severity Rating</label>
    <select name="rating" class="form-control-modern">
        <option value="VERY_MINOR">Very Minor</option>
        <option value="MINOR">Minor</option>
        <option value="MODERATE" selected>Moderate</option>
        <option value="SERIOUS">Serious</option>
        <option value="VERY_SERIOUS">Very Serious</option>
    </select>
</div>

<!-- Comments -->
<div class="mb-3">
    <label class="form-label-modern">Additional Comments</label>
    <textarea name="comments" class="form-control-modern" rows="2" placeholder="Add any additional details..."></textarea>
</div>

<script>
function toggleCustomCase(isCustom) {
    document.getElementById('standardCategoryDiv').style.display = isCustom ? 'none' : 'block';
    document.getElementById('customCaseDiv').style.display = isCustom ? 'block' : 'none';
    document.getElementById('customCaseInput').required = isCustom;
    document.getElementById('categorySelect').required = !isCustom;
    if (isCustom) document.getElementById('categorySelect').value = 'custom';
}

document.getElementById('categorySelect')?.addEventListener('change', function() {
    if (this.value === 'custom') {
        document.getElementById('customReport').checked = true;
        toggleCustomCase(true);
    }
});
</script>
"@ | Set-Content "$includesPath\custom_case.html" -Encoding UTF8

Write-Host "✅ custom_case.html updated" -ForegroundColor Green

# ============================================
# 10. UPDATE INCLUDES/CUSTOM_CATEGORY.HTML
# ============================================
Write-Host "`n📝 Updating includes/custom_category.html..." -ForegroundColor Yellow

@"
<div class="mb-3">
    <label class="form-label-modern">Category Type</label>
    <div class="d-flex gap-3">
        <div class="form-check">
            <input class="form-check-input" type="radio" name="category_type" id="standardCategory" value="standard" checked onclick="toggleCustomCategory(false)">
            <label class="form-check-label" for="standardCategory">Standard Category</label>
        </div>
        <div class="form-check">
            <input class="form-check-input" type="radio" name="category_type" id="customCategory" value="custom" onclick="toggleCustomCategory(true)">
            <label class="form-check-label" for="customCategory">Custom Category</label>
        </div>
    </div>
</div>

<!-- Standard Category -->
<div id="standardCategoryDiv">
    <div class="mb-3">
        <label class="form-label-modern">Select Category</label>
        <select name="category_id" class="form-control-modern" id="categorySelect">
            <option value="">Select a category...</option>
            {% for category in categories %}
            <option value="{{ category.id }}">{{ category.name }} (+{{ category.points }} points)</option>
            {% endfor %}
            <option value="custom">-- Custom Category --</option>
        </select>
    </div>
</div>

<!-- Custom Category -->
<div id="customCategoryDiv" style="display: none;">
    <div class="mb-3">
        <label class="form-label-modern">Custom Category Name</label>
        <input type="text" name="custom_category" class="form-control-modern" placeholder="Enter custom category name..." id="customCategoryInput">
    </div>
    <div class="mb-3">
        <label class="form-label-modern">Points</label>
        <input type="number" name="custom_points" class="form-control-modern" placeholder="Enter points (1-50)" id="customPointsInput" min="1" max="50">
    </div>
</div>

<!-- Severity -->
<div class="mb-3">
    <label class="form-label-modern">Severity Rating</label>
    <select name="rating" class="form-control-modern">
        <option value="VERY_MINOR">Very Minor</option>
        <option value="MINOR">Minor</option>
        <option value="MODERATE" selected>Moderate</option>
        <option value="SERIOUS">Serious</option>
        <option value="VERY_SERIOUS">Very Serious</option>
    </select>
</div>

<!-- Comments -->
<div class="mb-3">
    <label class="form-label-modern">Additional Comments</label>
    <textarea name="comments" class="form-control-modern" rows="2" placeholder="Add any additional details..."></textarea>
</div>

<script>
function toggleCustomCategory(isCustom) {
    document.getElementById('standardCategoryDiv').style.display = isCustom ? 'none' : 'block';
    document.getElementById('customCategoryDiv').style.display = isCustom ? 'block' : 'none';
    document.getElementById('customCategoryInput').required = isCustom;
    document.getElementById('categorySelect').required = !isCustom;
    if (isCustom) document.getElementById('categorySelect').value = 'custom';
}

document.getElementById('categorySelect')?.addEventListener('change', function() {
    if (this.value === 'custom') {
        document.getElementById('customCategory').checked = true;
        toggleCustomCategory(true);
    }
});
</script>
"@ | Set-Content "$includesPath\custom_category.html" -Encoding UTF8

Write-Host "✅ custom_category.html updated" -ForegroundColor Green

# ============================================
# 11. UPDATE INCLUDES/REPORT_FORM.HTML
# ============================================
Write-Host "`n📝 Updating includes/report_form.html..." -ForegroundColor Yellow

@"
<div class="mb-3">
    <label class="form-label-modern">Category Name</label>
    <input type="text" name="category_name" class="form-control-modern" placeholder="Enter the category name (e.g., Bullying, Disrespect, Fighting, etc.)" required>
    <small class="text-muted">Enter any category you want to report</small>
</div>

<div class="mb-3">
    <label class="form-label-modern">Severity Rating</label>
    <select name="rating" class="form-control-modern" required>
        <option value="VERY_MINOR">Very Minor (5 points)</option>
        <option value="MINOR">Minor (10 points)</option>
        <option value="MODERATE" selected>Moderate (20 points)</option>
        <option value="SERIOUS">Serious (30 points)</option>
        <option value="VERY_SERIOUS">Very Serious (40 points)</option>
    </select>
    <small class="text-muted">Points are automatically assigned based on severity</small>
</div>

<div class="mb-3">
    <label class="form-label-modern">Additional Comments</label>
    <textarea name="comments" class="form-control-modern" rows="3" placeholder="Add any additional details..."></textarea>
</div>
"@ | Set-Content "$includesPath\report_form.html" -Encoding UTF8

Write-Host "✅ report_form.html updated" -ForegroundColor Green

# ============================================
# 12. UPDATE ADMIN_RESET_REQUESTS.HTML
# ============================================
Write-Host "`n📝 Updating admin_reset_requests.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Password Reset Requests{% endblock %}

{% block content %}
<div class="card-modern" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-key"></i></span>
        Password Reset Requests
        <span class="badge bg-light text-dark ms-2" id="pendingCount">{{ pending_resets|length }}</span>
    </div>
    <div class="card-body">
        {% if pending_resets %}
        <div class="table-responsive">
            <table class="table-modern">
                <thead><tr><th>Username</th><th>Full Name</th><th>Email</th><th>Requested At</th><th>Actions</th></tr></thead>
                <tbody>
                    {% for reset in pending_resets %}
                    <tr>
                        <td><strong>{{ reset.user.username }}</strong></td>
                        <td>{{ reset.user.get_full_name|default:"-" }}</td>
                        <td>{{ reset.user.email|default:"-" }}</td>
                        <td>{{ reset.requested_at|date:"Y-m-d H:i" }}</td>
                        <td>
                            <div class="d-flex gap-2 flex-wrap">
                                <form method="post" action="{% url 'approve_reset' reset.id %}">
                                    {% csrf_token %}
                                    <button type="submit" class="btn-modern btn-modern-success btn-modern-sm" onclick="return confirm('Reset password for {{ reset.user.username }}?')"><i class="fas fa-check"></i> Approve</button>
                                </form>
                                <form method="post" action="{% url 'reject_reset' reset.id %}">
                                    {% csrf_token %}
                                    <button type="submit" class="btn-modern btn-modern-danger btn-modern-sm" onclick="return confirm('Reject this request?')"><i class="fas fa-times"></i> Reject</button>
                                </form>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>No pending requests</div>
        {% endif %}
    </div>
</div>
<div class="mt-3"><a href="{% url 'admin_dashboard' %}" class="btn-modern btn-modern-secondary"><i class="fas fa-arrow-left"></i> Back</a></div>

<script>
setInterval(function() {
    $.get('/api/admin-notifications/', function(data) {
        data.notifications.forEach(function(n) {
            if (n.type === 'reset') {
                $('#pendingCount').text(n.count || '0');
            }
        });
    });
}, 30000);
</script>
{% endblock %}
"@ | Set-Content "$basePath\admin_reset_requests.html" -Encoding UTF8

Write-Host "✅ admin_reset_requests.html updated" -ForegroundColor Green

# ============================================
# 13. UPDATE MANAGE_USERS.HTML
# ============================================
Write-Host "`n📝 Updating manage_users.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Manage Users{% endblock %}

{% block content %}
<div class="card-modern" data-aos="fade-up">
    <div class="card-header-modern">
        <span class="header-icon"><i class="fas fa-users-cog"></i></span>
        User Management
        {% if pending_approvals > 0 %}<span class="badge bg-light text-dark ms-2">{{ pending_approvals }} pending</span>{% endif %}
        <span class="badge bg-light text-dark ms-2 ms-auto">Total: {{ teacher_users|length }}</span>
    </div>
    <div class="card-body">
        <div class="d-flex flex-wrap gap-2 mb-3">
            <a href="?status=" class="btn-modern btn-modern-secondary btn-modern-sm">All</a>
            <a href="?status=pending" class="btn-modern btn-modern-warning btn-modern-sm">Pending</a>
            <a href="?status=approved" class="btn-modern btn-modern-success btn-modern-sm">Approved</a>
            <a href="?status=suspended" class="btn-modern btn-modern-danger btn-modern-sm">Suspended</a>
        </div>
        
        <div class="table-responsive">
            <table class="table-modern">
                <thead><tr><th>Username</th><th>Full Name</th><th>Role</th><th>Stream</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                    {% for user in teacher_users %}
                    <tr class="{% if user.teacher_profile.is_suspended %}bg-danger bg-opacity-10{% elif not user.teacher_profile.is_approved %}bg-warning bg-opacity-10{% endif %}">
                        <td><strong>{{ user.username }}</strong></td>
                        <td>{{ user.get_full_name|default:"-" }}</td>
                        <td>{% if user.is_superuser %}<span class="badge-modern badge-critical">Admin</span>{% elif user.groups.first %}<span class="badge-modern badge-info">{{ user.groups.first.name }}</span>{% else %}<span class="badge-modern badge-secondary">Teacher</span>{% endif %}</td>
                        <td>{% if user.teacher_profile.assigned_stream %}{{ user.teacher_profile.assigned_stream.get_name_display }}{% else %}-{% endif %}</td>
                        <td>{% if user.teacher_profile.is_suspended %}<span class="badge-modern badge-critical">Suspended</span>{% elif user.teacher_profile.is_approved %}<span class="badge-modern badge-success">Approved</span>{% else %}<span class="badge-modern badge-warning">Pending</span>{% endif %}</td>
                        <td>
                            <div class="d-flex gap-1 flex-wrap">
                                {% if not user.teacher_profile.is_approved and not user.teacher_profile.is_suspended and not user.is_superuser %}
                                <form method="post" action="{% url 'approve_user' user.id %}">
                                    {% csrf_token %}<button type="submit" class="btn-modern btn-modern-success btn-modern-sm"><i class="fas fa-check"></i></button>
                                </form>
                                {% endif %}
                                {% if user.teacher_profile.is_approved and not user.teacher_profile.is_suspended and not user.is_superuser %}
                                <button class="btn-modern btn-modern-warning btn-modern-sm" onclick="suspendUser({{ user.id }})"><i class="fas fa-pause"></i></button>
                                {% endif %}
                                {% if user.teacher_profile.is_suspended and not user.is_superuser %}
                                <form method="post" action="{% url 'unsuspend_user' user.id %}">
                                    {% csrf_token %}<button type="submit" class="btn-modern btn-modern-success btn-modern-sm"><i class="fas fa-play"></i></button>
                                </form>
                                {% endif %}
                                {% if not user.is_superuser %}
                                <button class="btn-modern btn-modern-danger btn-modern-sm" onclick="deleteUser({{ user.id }}, '{{ user.username }}')"><i class="fas fa-trash"></i></button>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% empty %}<tr><td colspan="6" class="text-center py-4 text-muted">No users found</td></tr>{% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Suspend Modal -->
<div class="modal fade" id="suspendModal" tabindex="-1">
    <div class="modal-dialog"><div class="modal-content border-0 shadow-lg rounded-4">
        <div class="modal-header border-0"><h5 class="modal-title"><i class="fas fa-pause text-warning me-2"></i>Suspend User</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <form method="post" id="suspendForm"><div class="modal-body"><p>Reason for suspension</p><textarea name="reason" class="form-control-modern" rows="3" placeholder="Enter reason..." required></textarea></div><div class="modal-footer border-0"><button type="button" class="btn-modern btn-modern-secondary" data-bs-dismiss="modal">Cancel</button><button type="submit" class="btn-modern btn-modern-warning">Suspend</button></div></form>
    </div></div>
</div>

<!-- Ban Modal -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog"><div class="modal-content border-0 shadow-lg rounded-4">
        <div class="modal-header border-0"><h5 class="modal-title text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Permanent Ban</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <form method="post" id="deleteForm"><div class="modal-body"><p class="text-danger fw-bold">⚠️ This action is irreversible!</p><p>Ban <strong id="deleteUserName"></strong> permanently.</p><textarea name="reason" class="form-control-modern" rows="3" placeholder="Reason for ban..." required></textarea></div><div class="modal-footer border-0"><button type="button" class="btn-modern btn-modern-secondary" data-bs-dismiss="modal">Cancel</button><button type="submit" class="btn-modern btn-modern-danger">Permanently Ban</button></div></form>
    </div></div>
</div>

<script>
function suspendUser(id) { document.getElementById('suspendForm').action = '/suspend-user/'+id+'/'; new bootstrap.Modal(document.getElementById('suspendModal')).show(); }
function deleteUser(id, name) { document.getElementById('deleteForm').action = '/ban-user/'+id+'/'; document.getElementById('deleteUserName').textContent = name; new bootstrap.Modal(document.getElementById('deleteModal')).show(); }
</script>
{% endblock %}
"@ | Set-Content "$basePath\manage_users.html" -Encoding UTF8

Write-Host "✅ manage_users.html updated" -ForegroundColor Green

# ============================================
# 14. UPDATE CHOOSE_STREAM.HTML
# ============================================
Write-Host "`n📝 Updating choose_stream.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Choose Your Class{% endblock %}

{% block content %}
<div class="row justify-content-center" style="min-height: 70vh; align-items: center;">
    <div class="col-lg-6 col-md-8" data-aos="fade-up">
        <div class="card-modern">
            <div class="card-body p-4 p-lg-5 text-center">
                <div style="width: 72px; height: 72px; background: linear-gradient(135deg, #2563eb, #7c3aed); border-radius: 18px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem;">
                    <i class="fas fa-chalkboard-teacher fa-2x text-white"></i>
                </div>
                <h2 class="fw-bold">Welcome, {{ user.get_full_name|default:user.username }}</h2>
                <p class="text-muted mb-4">Select your assigned class stream to continue</p>
                
                <div class="alert alert-info text-start"><i class="fas fa-info-circle me-2"></i>After selecting your stream, your account will be pending admin approval.</div>
                
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3 text-start">
                        <label class="form-label-modern">Select Stream</label>
                        <select name="stream" class="form-control-modern" required>
                            <option value="">-- Choose your stream --</option>
                            {% for stream in streams %}<option value="{{ stream.id }}">{{ stream.get_name_display }}</option>{% endfor %}
                        </select>
                    </div>
                    <div class="mb-3 text-start">
                        <label class="form-label-modern">Select Form</label>
                        <select name="form" class="form-control-modern" required>
                            <option value="">-- Choose your form --</option>
                            {% for form_key, form_name in forms %}<option value="{{ form_key }}">{{ form_name }}</option>{% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="btn-modern btn-modern-primary w-100"><i class="fas fa-check-circle me-2"></i>Submit & Wait for Approval</button>
                </form>
                
                <div class="mt-3"><small class="text-muted">Streams: {% for stream in streams %}{{ stream.get_name_display }}{% if not forloop.last %}, {% endif %}{% endfor %}</small></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@ | Set-Content "$basePath\choose_stream.html" -Encoding UTF8

Write-Host "✅ choose_stream.html updated" -ForegroundColor Green

# ============================================
# 15. UPDATE REQUEST_RESET.HTML
# ============================================
Write-Host "`n📝 Updating request_reset.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Forgot Password{% endblock %}

{% block content %}
<div class="row justify-content-center" style="min-height: 70vh; align-items: center;">
    <div class="col-lg-5 col-md-7" data-aos="fade-up">
        <div class="card-modern">
            <div class="card-body p-4 p-lg-5 text-center">
                <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #2563eb, #7c3aed); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem;">
                    <i class="fas fa-key fa-2x text-white"></i>
                </div>
                <h2 class="fw-bold">Forgot Password?</h2>
                <p class="text-muted">Enter your username to request a reset</p>
                
                <div class="alert alert-info text-start"><i class="fas fa-info-circle me-2"></i><strong>How it works:</strong><br>1. Enter your username<br>2. Admin will review your request<br>3. You'll receive a new password</div>
                
                <form method="post" action="{% url 'request_password_reset' %}">
                    {% csrf_token %}
                    <div class="mb-3 text-start">
                        <label class="form-label-modern">Username</label>
                        <input type="text" name="username" class="form-control-modern" placeholder="Enter your username" required>
                    </div>
                    <button type="submit" class="btn-modern btn-modern-primary w-100"><i class="fas fa-paper-plane me-2"></i>Request Reset</button>
                </form>
                
                <div class="mt-3"><a href="{% url 'login' %}" class="text-muted"><i class="fas fa-arrow-left me-1"></i>Back to Login</a></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@ | Set-Content "$basePath\request_reset.html" -Encoding UTF8

Write-Host "✅ request_reset.html updated" -ForegroundColor Green

# ============================================
# 16. UPDATE EDIT_STUDENT.HTML
# ============================================
Write-Host "`n📝 Updating edit_student.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Edit Student - {{ student.name }}{% endblock %}

{% block extra_css %}
<style>
    .profile-pic-container { position: relative; display: inline-block; }
    .profile-pic-container img { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 3px solid #2563eb; }
    .profile-pic-placeholder { width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #7c3aed); display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 3px solid #2563eb; }
    .profile-pic-placeholder i { font-size: 4rem; color: white; }
    .form-section { border-bottom: 1px solid #e2e8f0; padding-bottom: 1.5rem; margin-bottom: 1.5rem; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8" data-aos="fade-up">
        <div class="card-modern">
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <h2 class="fw-bold"><i class="fas fa-user-edit text-primary me-2"></i>Edit Student</h2>
                    <p class="text-muted">{{ student.name }} ({{ student.admission_number }})</p>
                </div>

                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}<input type="hidden" name="action" value="update_student">
                    
                    <!-- Profile Picture -->
                    <div class="form-section">
                        <h5><i class="fas fa-camera text-primary me-2"></i>Profile Picture</h5>
                        <div class="row align-items-center g-3">
                            <div class="col-md-3 text-center">
                                <div class="profile-pic-container">
                                    {% if student.profile_picture %}
                                    <img src="{{ student.profile_picture.url }}" alt="{{ student.name }}">
                                    {% else %}
                                    <div class="profile-pic-placeholder"><i class="fas fa-user-graduate"></i></div>
                                    {% endif %}
                                </div>
                            </div>
                            <div class="col-md-9"><input type="file" name="profile_picture" class="form-control-modern" accept="image/*"></div>
                        </div>
                    </div>

                    <!-- Student Info -->
                    <div class="row g-3">
                        <div class="col-md-6"><label class="form-label-modern">Full Name</label><input type="text" name="name" class="form-control-modern" value="{{ student.name }}" required></div>
                        <div class="col-md-6"><label class="form-label-modern">Admission Number</label><input type="text" class="form-control-modern" value="{{ student.admission_number }}" disabled></div>
                        <div class="col-md-4"><label class="form-label-modern">Stream</label><input type="text" class="form-control-modern" value="{{ student.stream.get_name_display }}" disabled></div>
                        <div class="col-md-4">
                            <label class="form-label-modern">Form</label>
                            <select name="form" class="form-control-modern" required>
                                {% for form_key, form_name in forms %}<option value="{{ form_key }}" {% if student.form == form_key %}selected{% endif %}>{{ form_name }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="col-md-4"><label class="form-label-modern">Year</label><input type="number" name="year" class="form-control-modern" value="{{ student.year }}" required></div>
                        <div class="col-12"><label class="form-label-modern">Optional Notes</label><textarea name="optional_notes" class="form-control-modern" rows="3">{{ student.optional_notes }}</textarea></div>
                    </div>

                    <div class="d-flex gap-2 mt-4 flex-wrap">
                        <button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-save"></i> Update Student</button>
                        <a href="{% url 'student_profile' student.id %}" class="btn-modern btn-modern-secondary"><i class="fas fa-times"></i> Cancel</a>
                    </div>
                </form>

                <!-- Danger Zone -->
                <hr class="my-4">
                <div class="text-center">
                    <h5 class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Danger Zone</h5>
                    <form method="post" onsubmit="return confirm('Delete {{ student.name }} permanently?')">
                        {% csrf_token %}<input type="hidden" name="action" value="delete_student">
                        <button type="submit" class="btn-modern btn-modern-danger">
                            <i class="fas fa-trash"></i> {% if user.is_superuser %}Permanently Delete{% else %}Deactivate{% endif %}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@ | Set-Content "$basePath\edit_student.html" -Encoding UTF8

Write-Host "✅ edit_student.html updated" -ForegroundColor Green

# ============================================
# 17. UPDATE ADMIN_PROFILE.HTML
# ============================================
Write-Host "`n📝 Updating admin_profile.html..." -ForegroundColor Yellow

@"
{% extends 'base.html' %}

{% block title %}Admin Profile{% endblock %}

{% block extra_css %}
<style>
    .profile-pic-container { position: relative; display: inline-block; }
    .profile-pic-container img { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 3px solid #2563eb; }
    .profile-pic-placeholder { width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #7c3aed); display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 3px solid #2563eb; }
    .profile-pic-placeholder i { font-size: 4rem; color: white; }
    .form-section { border-bottom: 1px solid #e2e8f0; padding-bottom: 1.5rem; margin-bottom: 1.5rem; }
    .form-section:last-child { border-bottom: none; margin-bottom: 0; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8" data-aos="fade-up">
        <div class="card-modern">
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #2563eb, #7c3aed); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                        <i class="fas fa-user-shield fa-2x text-white"></i>
                    </div>
                    <h2 class="fw-bold">Admin Profile</h2>
                    <p class="text-muted">Manage your account credentials</p>
                    <div class="alert alert-info"><i class="fas fa-info-circle me-2"></i><strong>{{ user.username }}</strong>{% if user.email %} | {{ user.email }}{% endif %}</div>
                </div>

                <!-- Profile Picture -->
                <div class="form-section">
                    <h5><i class="fas fa-camera text-primary me-2"></i>Profile Picture</h5>
                    <div class="row align-items-center g-3">
                        <div class="col-md-3 text-center">
                            <div class="profile-pic-container">
                                {% if user.teacher_profile.profile_picture %}
                                <img src="{{ user.teacher_profile.profile_picture.url }}" alt="Profile">
                                {% else %}
                                <div class="profile-pic-placeholder"><i class="fas fa-user"></i></div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-9">
                            <form method="post" enctype="multipart/form-data" action="{% url 'upload_profile_picture' %}">
                                {% csrf_token %}
                                <div class="mb-3"><label class="form-label-modern">Upload New Picture</label><input type="file" name="profile_picture" class="form-control-modern" accept="image/*"></div>
                                <button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-upload"></i> Upload</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Change Password -->
                <div class="form-section">
                    <h5><i class="fas fa-key text-warning me-2"></i>Change Password</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_password">
                        <div class="row g-2">
                            <div class="col-12"><input type="password" name="current_password" class="form-control-modern" placeholder="Current Password" required></div>
                            <div class="col-md-6"><input type="password" name="new_password" class="form-control-modern" placeholder="New Password (min 8 chars)" required></div>
                            <div class="col-md-6"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Confirm Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-warning"><i class="fas fa-save"></i> Change Password</button></div>
                        </div>
                    </form>
                </div>

                <!-- Change Username -->
                <div class="form-section">
                    <h5><i class="fas fa-user-tag text-primary me-2"></i>Change Username</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_username">
                        <div class="row g-2">
                            <div class="col-md-8"><input type="text" name="new_username" class="form-control-modern" value="{{ user.username }}" required></div>
                            <div class="col-md-4"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-save"></i> Change Username</button></div>
                        </div>
                    </form>
                </div>

                <!-- Change Email -->
                <div class="form-section">
                    <h5><i class="fas fa-envelope text-primary me-2"></i>Change Email</h5>
                    <form method="post">
                        {% csrf_token %}<input type="hidden" name="action" value="change_email">
                        <div class="row g-2">
                            <div class="col-md-8"><input type="email" name="new_email" class="form-control-modern" value="{{ user.email|default:'' }}" required></div>
                            <div class="col-md-4"><input type="password" name="confirm_password" class="form-control-modern" placeholder="Password" required></div>
                            <div class="col-12"><button type="submit" class="btn-modern btn-modern-primary"><i class="fas fa-save"></i> Change Email</button></div>
                        </div>
                    </form>
                </div>

                <div class="text-center mt-3"><a href="{% url 'admin_dashboard' %}" class="btn-modern btn-modern-secondary"><i class="fas fa-arrow-left"></i> Back to Dashboard</a></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"@ | Set-Content "$basePath\admin_profile.html" -Encoding UTF8

Write-Host "✅ admin_profile.html updated" -ForegroundColor Green

# ============================================
# 18. UPDATE 500.HTML
# ============================================
Write-Host "`n📝 Updating 500.html..." -ForegroundColor Yellow

@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 - Server Error</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            padding: 1.5rem;
        }
        .error-box {
            background: rgba(255,255,255,0.95);
            border-radius: 24px;
            padding: 3rem;
            max-width: 480px;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0,0,0,0.3);
        }
        .error-box .error-icon {
            width: 80px; height: 80px;
            background: linear-gradient(135deg, #ef4444, #dc2626);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2.5rem; color: white;
        }
        .error-box h1 { font-size: 2rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem; }
        .error-box p { color: #64748b; margin-bottom: 1.5rem; }
        .error-box .btn-home {
            display: inline-flex; align-items: center; gap: 0.5rem;
            padding: 0.75rem 2rem;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white; border: none; border-radius: 12px;
            text-decoration: none; font-weight: 600;
            transition: all 0.3s;
        }
        .error-box .btn-home:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(37,99,235,0.35); }
    </style>
</head>
<body>
    <div class="error-box">
        <div class="error-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h1>500</h1>
        <p>Something went wrong on our end. Please try again later.</p>
        <a href="/" class="btn-home"><i class="fas fa-home"></i> Go Home</a>
    </div>
</body>
</html>
"@ | Set-Content "$basePath\500.html" -Encoding UTF8

Write-Host "✅ 500.html updated" -ForegroundColor Green

# ============================================
# COMPLETE
# ============================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✅ ALL TEMPLATES UPDATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n📋 Updated files:" -ForegroundColor Yellow
Write-Host "  ✅ base.html"
Write-Host "  ✅ login.html"
Write-Host "  ✅ register.html"
Write-Host "  ✅ admin_dashboard.html"
Write-Host "  ✅ teacher_dashboard.html"
Write-Host "  ✅ class_teacher_dashboard.html"
Write-Host "  ✅ student_profile.html"
Write-Host "  ✅ user_profile.html"
Write-Host "  ✅ admin_profile.html"
Write-Host "  ✅ manage_users.html"
Write-Host "  ✅ admin_reset_requests.html"
Write-Host "  ✅ choose_stream.html"
Write-Host "  ✅ request_reset.html"
Write-Host "  ✅ edit_student.html"
Write-Host "  ✅ 500.html"
Write-Host "  ✅ includes/custom_case.html"
Write-Host "  ✅ includes/custom_category.html"
Write-Host "  ✅ includes/report_form.html"
Write-Host "`n🔄 Restart your Django server to see changes:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor Gray
"@

Write-Host "`n✅ Done!" -ForegroundColor Green