from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class NotificationPreference(models.Model):
    """
    User's notification preferences and settings
    """
    REMINDER_TYPE_CHOICES = [
        ('task_daily', 'Daily Task Reminders'),
        ('class_1day', 'Class Reminders - 1 Day Before'),
        ('class_1hour', 'Class Reminders - 1 Hour Before'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notification toggles
    email_notifications = models.BooleanField(default=True, help_text="Overall email notification toggle")
    task_reminders_enabled = models.BooleanField(default=True, help_text="Enable daily task reminders")
    class_reminders_enabled = models.BooleanField(default=True, help_text="Enable class reminders")
    
    # Timing preferences
    reminder_time = models.TimeField(
        default='08:00',
        help_text="Preferred time to receive daily reminders (HH:MM format)"
    )
    class_reminder_days_before = models.IntegerField(
        default=1,
        choices=[(1, '1 Day'), (3, '3 Days'), (7, '1 Week')],
        help_text="How many days in advance to get class reminders"
    )
    
    # Notification frequency
    send_digest = models.BooleanField(
        default=False,
        help_text="Send a digest of all reminders instead of individual emails"
    )
    digest_frequency = models.CharField(
        max_length=20,
        default='daily',
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        help_text="How often to receive digest emails"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"


class NotificationLog(models.Model):
    """
    Log of all notifications sent to users
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('task_reminder', 'Task Reminder'),
        ('class_reminder', 'Class Reminder'),
        ('digest', 'Digest Email'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_logs')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Content
    message_preview = models.TextField(max_length=500, help_text="Preview of the notification message")
    
    # Metadata
    related_task_id = models.UUIDField(null=True, blank=True, help_text="Task ID if this is a task reminder")
    related_class_id = models.UUIDField(null=True, blank=True, help_text="Class (TimetableEntry) ID if this is a class reminder")
    
    # Timestamps
    scheduled_for = models.DateTimeField(help_text="When the notification was scheduled")
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was actually sent")
    created_at = models.DateTimeField(default=timezone.now)
    
    # Error tracking
    error_message = models.TextField(blank=True, help_text="Error details if notification failed")
    retry_count = models.IntegerField(default=0, help_text="Number of retry attempts")
    
    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-scheduled_for']
        indexes = [
            models.Index(fields=['user', 'scheduled_for']),
            models.Index(fields=['status', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} to {self.user.email} - {self.status}"
    
    def mark_as_sent(self):
        """Mark notification as successfully sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message=''):
        """Mark notification as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()


class NotificationTemplate(models.Model):
    """
    Email templates for notifications
    """
    TEMPLATE_TYPE_CHOICES = [
        ('task_reminder', 'Task Reminder'),
        ('class_reminder', 'Class Reminder'),
        ('digest', 'Digest Email'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    subject = models.CharField(max_length=255, help_text="Email subject line")
    html_body = models.TextField(help_text="HTML email template")
    text_body = models.TextField(help_text="Plain text email template")
    
    is_active = models.BooleanField(default=True, help_text="Whether this template is in use")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"{self.template_type} Template"
