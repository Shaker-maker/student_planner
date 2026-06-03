from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import ReminderLog
import logging

logger = logging.getLogger(__name__)


class ReminderEmailService:
    """
    Service to handle sending reminder emails to students
    """

    @staticmethod
    def send_reminder_email(task, user):
        """
        Send a personalized reminder email to a user for a specific task
        
        Args:
            task: Task instance
            user: User instance
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Generate personalized message
            message = task.get_reminder_message()
            
            # Prepare email context
            context = {
                'user': user,
                'task': task,
                'message': message,
                'days_left': task.get_days_left(),
                'is_overdue': task.is_overdue(),
            }
            
            # Render HTML email template
            html_message = render_to_string('emails/task_reminder.html', context)
            plain_message = render_to_string('emails/task_reminder.txt', context)
            
            # Send email
            send_mail(
                subject=f"Reminder: {task.unit_name} {task.task_type}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Log the reminder
            ReminderLog.objects.create(
                task=task,
                user=user,
                message=message,
                notification_method='email',
                sent_date=timezone.now().date(),
            )
            
            logger.info(f"Reminder email sent to {user.email} for task '{task.name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send reminder email to {user.email} for task '{task.name}': {str(e)}")
            return False

    @staticmethod
    def send_bulk_reminders():
        """
        Send reminders to all users for their pending tasks
        This is typically called by a management command or scheduled task
        
        Returns:
            dict: Statistics about reminders sent
        """
        from .models import Task
        
        stats = {
            'total_tasks': 0,
            'reminders_sent': 0,
            'reminders_failed': 0,
        }
        
        try:
            now = timezone.now()
            today = now.date()
            
            # Get all tasks with due dates in the future or today
            tasks = Task.objects.filter(
                due_date__date__gte=today,
                status__in=['pending', 'not_submitted']
            ).select_related('user')
            
            stats['total_tasks'] = tasks.count()
            
            for task in tasks:
                # Check if reminder already sent today
                reminder_exists = ReminderLog.objects.filter(
                    task=task,
                    user=task.user,
                    sent_date=today
                ).exists()
                
                if not reminder_exists:
                    # Only send if user has email notifications enabled
                    if task.user.email_notifications:
                        if ReminderEmailService.send_reminder_email(task, task.user):
                            stats['reminders_sent'] += 1
                        else:
                            stats['reminders_failed'] += 1
            
            logger.info(f"Daily reminder batch completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error sending daily reminders: {str(e)}")
            return stats
