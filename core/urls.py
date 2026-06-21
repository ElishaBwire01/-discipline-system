from django.urls import path
from . import views

urlpatterns = [
    # ============================================
    # AUTHENTICATION
    # ============================================
    path('', views.custom_login, name='login'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # ============================================
    # PASSWORD RESET
    # ============================================
    path('request-reset/', views.request_password_reset, name='request_password_reset'),
    path('admin-reset-requests/', views.admin_reset_requests, name='admin_reset_requests'),
    path('approve-reset/<int:reset_id>/', views.approve_reset, name='approve_reset'),
    path('reject-reset/<int:reset_id>/', views.reject_reset, name='reject_reset'),
    
    # ============================================
    # DASHBOARDS
    # ============================================
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('choose-stream/', views.choose_stream, name='choose_stream'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('class-teacher-dashboard/', views.class_teacher_dashboard, name='class_teacher_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # ============================================
    # STUDENT MANAGEMENT
    # ============================================
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    
    # ============================================
    # USER MANAGEMENT (Admin only)
    # ============================================
    path('manage-users/', views.manage_users, name='manage_users'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('suspend-user/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('unsuspend-user/<int:user_id>/', views.unsuspend_user, name='unsuspend_user'),
    path('delete-user/<int:user_id>/', views.delete_user_permanent, name='delete_user_permanent'),
    path('ban-user/<int:user_id>/', views.ban_user_permanent, name='ban_user_permanent'),
    

        # ============================================
    # SUPABASE API ROUTES
    # ============================================
    path('api/supabase/sync-students/', views.supabase_sync_students, name='supabase_sync_students'),
    path('api/supabase/sync-reports/', views.supabase_sync_reports, name='supabase_sync_reports'),
    path('api/supabase/students/', views.supabase_get_students, name='supabase_get_students'),
    path('api/supabase/reports/', views.supabase_get_reports, name='supabase_get_reports'),

    # ============================================
    # USER PROFILE
    # ============================================
    path('profile/', views.user_profile_settings, name='user_profile_settings'),
    path('profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    
    # ============================================
    # API ENDPOINTS
    # ============================================
    path('api/search-students/', views.search_students_api, name='search_students_api'),
    path('api/notifications/', views.get_notifications_api, name='get_notifications_api'),
    path('api/notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/online-teachers/', views.online_teachers_api, name='online_teachers_api'),
    path('api/admin-notifications/', views.get_admin_notifications, name='get_admin_notifications'),
]


