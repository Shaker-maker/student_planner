from django.contrib import admin
from .models import Task, ReminderLog


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_name', 'task_type', 'user', 'status', 'due_date', 'days_left_display']
    list_filter = ['task_type', 'status', 'due_date', 'created_at']
    search_fields = ['name', 'unit_name', 'user__email', 'user__first_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Task Information', {
            'fields': ('id', 'user', 'name', 'unit_name', 'task_type', 'description')
        }),
        ('Due Date & Status', {
            'fields': ('due_date', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def days_left_display(self, obj):
        days = obj.get_days_left()
        if days == 0:
            return "🔴 Due Today"
        elif days < 0:
            return "❌ Overdue"
        elif days == 1:
            return "🟠 1 day left"
        elif days <= 3:
            return f"🟡 {days} days left"
        else:
            return f"🟢 {days} days left"
    
    days_left_display.short_description = "Days Left"


@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'notification_method', 'sent_at']
    list_filter = ['notification_method', 'sent_at', 'sent_date']
    search_fields = ['task__name', 'user__email', 'message']
    readonly_fields = ['id', 'sent_at', 'message']
    fieldsets = (
        ('Reminder Information', {
            'fields': ('id', 'task', 'user', 'notification_method')
        }),
        ('Message & Timing', {
            'fields': ('message', 'sent_at', 'sent_date')
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of reminder logs"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion but show a warning"""
        return True
