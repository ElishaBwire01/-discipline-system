from django.urls import path
import os

from . import views

app_name = 'core'

urlpatterns = [
    # ============================================
    # ROOT - Redirect to login
    # ============================================
    path('', views.custom_login, name='login'),

    # ============================================
    # AUTHENTICATION
    # ============================================
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),

    # ============================================
    # DASHBOARDS
    # ============================================
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('class-teacher-dashboard/', views.class_teacher_dashboard, name=os.environ.get('SECRET_KEY', 'class_teacher_dashboard')),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('choose-stream/', views.choose_stream, name='choose_stream'),

    # ============================================
    # SCHOOL SETUP
    # ============================================
    path('school-setup/', views.school_setup, name='school_setup'),
    path('bulk-upload-students/', views.bulk_upload_students, name=os.environ.get('BULK_UPLOAD_STUDENTS_VALUE', 'bulk_upload_students')),
    path('download-template/', views.generate_excel_template, name='download_template'),
    path('download-text-template/', views.download_text_template, name=os.environ.get('SECRET_KEY', 'download_text_template')),

    # ============================================
    # STUDENT MANAGEMENT
    # ============================================
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('student/search/', views.search_students_api, name='search_students'),

    # ============================================
    # USER MANAGEMENT
    # ============================================
    path('manage-users/', views.manage_users, name='manage_users'),
    path('assign-class-teacher/', views.assign_class_teacher, name=os.environ.get('ASSIGN_CLASS_TEACHER_VALUE', 'assign_class_teacher')),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('suspend-user/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('unsuspend-user/<int:user_id>/', views.unsuspend_user, name='unsuspend_user'),
    path('delete-user/<int:user_id>/', views.delete_user_permanent, name=os.environ.get('SECRET_KEY', 'delete_user_permanent')),
    path('ban-user/<int:user_id>/', views.ban_user_permanent, name='ban_user_permanent'),

    # ============================================
    # USER PROFILE
    # ============================================
    path('profile/', views.user_profile_settings, name=os.environ.get('SECRET_KEY', 'user_profile_settings')),
    path('profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name=os.environ.get('SECRET_KEY', 'upload_profile_picture')),

    # ============================================
    # PASSWORD RESET
    # ============================================
    path('request-reset/', views.request_password_reset, name='request_password_reset'),
    path('admin-reset-requests/', views.admin_reset_requests, name=os.environ.get('ADMIN_RESET_REQUESTS_VALUE', 'admin_reset_requests')),
    path('approve-reset/<int:reset_id>/', views.approve_reset, name='approve_reset'),
    path('reject-reset/<int:reset_id>/', views.reject_reset, name='reject_reset'),

    # ============================================
    # AI DASHBOARD
    # ============================================
    path('ai/dashboard/', views.ai_dashboard, name='ai_dashboard'),

    # ============================================
    # AI CHAT
    # ============================================
    path('ai/chat/', views.ai_chat_page, name='ai_chat_page'),
    path('ai/chat/api/', views.ai_chat_api, name='ai_chat_api'),

    # ============================================
    # AI API ENDPOINTS
    # ============================================
    path('ai/api/global-recommendations/', views.global_recommendations, name=os.environ.get('SECRET_KEY', 'global_recommendations')),
    path('ai/api/student/<int:student_id>/recommendations/', views.student_recommendations, name=os.environ.get('SECRET_KEY', 'student_recommendations')),
    path('ai/api/class/<int:stream_id>/recommendations/', views.class_recommendations, name=os.environ.get('SECRET_KEY', 'class_recommendations')),
    path('ai/api/all-students/', views.ai_all_students, name='ai_all_students'),
    path('ai/api/student-by-name/', views.student_by_name, name='student_by_name'),
    path('ai/api/risk-stats/', views.ai_risk_stats, name='ai_risk_stats'),
    path('ai/api/trend-analysis/', views.ai_trend_analysis, name='ai_trend_analysis'),
    path('ai/api/intervention-suggestions/<int:student_id>/', views.ai_intervention_suggestions, name=os.environ.get('SECRET_KEY', 'ai_intervention_suggestions')),
    path('ai/api/bulk-risk-update/', views.ai_bulk_risk_update, name='ai_bulk_risk_update'),
    path('ai/api/predictive-analysis/', views.ai_predictive_analysis, name=os.environ.get('SECRET_KEY', 'ai_predictive_analysis')),
    path('ai/api/behavior-patterns/', views.ai_behavior_patterns, name=os.environ.get('AI_BEHAVIOR_PATTERNS_VALUE', 'ai_behavior_patterns')),
    path('ai/api/intervention-effectiveness/', views.ai_intervention_effectiveness, name=os.environ.get('SECRET_KEY', 'ai_intervention_effectiveness')),

    # ============================================
    # API ENDPOINTS
    # ============================================
    path('api/search-students/', views.search_students_api, name='search_students_api'),
    path('api/student-by-admission/<str:admission_number>/', views.student_by_admission, name=os.environ.get('STUDENT_BY_ADMISSION_VALUE', 'student_by_admission')),
    path('api/teacher-profile/<int:user_id>/', views.teacher_profile_api, name='teacher_profile_api'),
    path('api/report-error/', views.report_error, name='report_error'),
    path('api/notifications/', views.get_notifications_api, name=os.environ.get('SECRET_KEY', 'get_notifications_api')),
    path('api/notifications/read/<int:notification_id>/', views.mark_notification_read, name=os.environ.get('SECRET_KEY', 'mark_notification_read')),
    path('api/notifications/read-all/', views.mark_all_notifications_read, name=os.environ.get('SECRET_KEY', 'mark_all_notifications_read')),
    path('api/online-teachers/', views.online_teachers_api, name='online_teachers_api'),
    path('api/admin-notifications/', views.get_admin_notifications, name=os.environ.get('SECRET_KEY', 'get_admin_notifications')),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/streams/', views.get_streams_api, name='get_streams_api'),
    path('api/categories/', views.get_categories_api, name='get_categories_api'),

    # ============================================
    # REPORT EXPORTS
    # ============================================
    path('reports/export/<str:format>/', views.export_reports, name='export_reports'),
    path('reports/student/<int:student_id>/export/', views.export_student_reports, name=os.environ.get('SECRET_KEY', 'export_student_reports')),
    path('reports/summary/', views.export_summary_report, name=os.environ.get('SECRET_KEY', 'export_summary_report')),  # ? NEW
    path('reports/pdf/', views.export_pdf_report, name='export_pdf_report'),  # ? NEW

    # ============================================
    # CLASS TEACHER EXPORTS
    # ============================================
    path('class-export-reports/', views.export_class_reports, name=os.environ.get('EXPORT_CLASS_REPORTS_VALUE', 'export_class_reports')),  # ? NEW
    path('class-export-student/<int:student_id>/', views.export_class_student_reports, name=os.environ.get('SECRET_KEY', 'export_class_student_reports')),  # ? NEW

    # ============================================
    # DEBUG & TEST VIEWS
    # ============================================
    path('test-streams/', views.test_streams, name='test_streams'),
    path('debug-streams/', views.debug_streams, name='debug_streams'),
    path('test-ai/', views.test_ai, name='test_ai'),
]
