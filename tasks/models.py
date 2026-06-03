from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Task(models.Model):
    """
    Model for managing student assignments and CATs (Continuous Assessment Tests)
    """
    TASK_TYPE_CHOICES = [
        ('assignment', 'Assignment'),
        ('cat', 'CAT'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('not_submitted', 'Not Submitted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    
    # Task details
    name = models.CharField(max_length=255, help_text="Name of the assignment or CAT")
    unit_name = models.CharField(max_length=255, help_text="e.g., Database Systems")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='assignment')
    description = models.TextField(blank=True, null=True, help_text="Optional task description")
    
    # Due date and status
    due_date = models.DateTimeField(help_text="When the task is due")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.unit_name} (Due: {self.due_date.strftime('%Y-%m-%d')})"

    def get_days_left(self):
        """Calculate days remaining until due date"""
        now = timezone.now()
        delta = self.due_date - now
        days = delta.days
        
        if days < 0:
            return 0
        return days

    def get_reminder_message(self):
        """Generate personalized reminder message based on days left"""
        days_left = self.get_days_left()
        user_first_name = self.user.first_name
        task_type = "assignment" if self.task_type == 'assignment' else "CAT"
        
        if days_left > 1:
            return f"Hey {user_first_name} 👋🏽, your {self.unit_name} {task_type} is due in {days_left} days."
        elif days_left == 1:
            return f"Hey {user_first_name}, your {self.unit_name} {task_type} is due tomorrow. Don't forget to revise!"
        elif days_left == 0:
            return f"Hey {user_first_name}, today's the deadline for your {self.unit_name} {task_type}. Make sure you submit it on time!"
        else:
            return f"Hey {user_first_name}, your {self.unit_name} {task_type} deadline has passed."

    def is_overdue(self):
        """Check if task is overdue"""
        return timezone.now() > self.due_date

    def is_due_today(self):
        """Check if task is due today"""
        today = timezone.now().date()
        return self.due_date.date() == today


class ReminderLog(models.Model):
    """
    Log of sent reminders to track which reminders have been sent
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='reminder_logs',
        null=True,
        blank=True,
        help_text="Associated task (null for class reminders)"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminder_logs')
    
    # Reminder details
    message = models.TextField(help_text="The reminder message that was sent")
    notification_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
        ],
        default='email'
    )
    
    sent_at = models.DateTimeField(default=timezone.now)
    sent_date = models.DateField(help_text="Date the reminder was sent", db_index=True)
    
    class Meta:
        verbose_name = 'Reminder Log'
        verbose_name_plural = 'Reminder Logs'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'sent_date']),
            models.Index(fields=['task', 'sent_date']),
        ]

    def __str__(self):
        return f"Reminder for {self.task.name} sent to {self.user.email} on {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
