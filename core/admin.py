from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Stream, TeacherProfile, UserSession,
    Student, DisciplineCategory, DisciplineReport, Notification,
)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'assigned_stream', 'assigned_form', 'is_online', 'last_activity']
    list_filter = ['is_online', 'assigned_stream']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'last_activity', 'is_active']
    list_filter = ['is_active']


@admin.register(DisciplineCategory)
class DisciplineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'default_rating', 'is_active', 'order']
    list_filter = ['is_active', 'default_rating']
    search_fields = ['name', 'key']
    list_editable = ['default_rating', 'is_active', 'order']
    ordering = ['order', 'name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'name', 'stream', 'form', 'risk_score_display', 'year']
    list_filter = ['stream', 'form', 'year']
    search_fields = ['admission_number', 'name']
    readonly_fields = ['risk_score', 'created_at']

    def risk_score_display(self, obj):
        color = 'red' if obj.risk_score >= 60 else 'orange' if obj.risk_score >= 30 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>', color, obj.risk_score
        )
    risk_score_display.short_description = 'Risk Score'


@admin.register(DisciplineReport)
class DisciplineReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'category', 'reported_by', 'points', 'rating', 'reported_at']
    list_filter = ['category', 'rating', 'reported_at']
    search_fields = ['student__name', 'category__name']
    readonly_fields = ['category_name', 'points']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'created_at', 'is_read']
    list_filter = ['notification_type', 'is_read']