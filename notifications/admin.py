from django.contrib import admin
from .models import NotificationPreference, NotificationLog, NotificationTemplate


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'reminder_time', 'created_at')
    list_filter = ('email_notifications', 'task_reminders_enabled', 'class_reminders_enabled')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': ('email_notifications', 'task_reminders_enabled', 'class_reminders_enabled')
        }),
        ('Timing Preferences', {
            'fields': ('reminder_time', 'class_reminder_days_before', 'send_digest', 'digest_frequency')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'status', 'subject', 'scheduled_for')
    list_filter = ('notification_type', 'status', 'scheduled_for')
    search_fields = ('user__email', 'subject', 'message_preview')
    readonly_fields = ('id', 'created_at', 'sent_at')
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'notification_type', 'subject')
        }),
        ('Content', {
            'fields': ('message_preview', 'related_task_id', 'related_class_id')
        }),
        ('Status & Timing', {
            'fields': ('status', 'scheduled_for', 'sent_at', 'retry_count', 'error_message')
        }),
        ('System', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # NotificationLogs are created automatically
        return False


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_type', 'is_active', 'updated_at')
    list_filter = ('template_type', 'is_active')
    search_fields = ('subject',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Template Info', {
            'fields': ('template_type', 'is_active', 'subject')
        }),
        ('Email Content', {
            'fields': ('html_body', 'text_body'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
