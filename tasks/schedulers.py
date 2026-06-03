"""
APScheduler tasks for sending daily task reminders.
Automatically started when Django loads (via tasks/apps.py).
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.models import User
from tasks.models import Task
from notifications.models import NotificationLog

logger = logging.getLogger(__name__)


def send_daily_reminders():
    """
    Send daily task reminders to all users at their configured reminder time.
    Runs every minute; checks if it's time for each user.
    """
    now = timezone.now()
    stats = {
        'total_users': 0,
        'reminders_sent': 0,
        'errors': 0,
    }
    
    try:
        # Get all active users who want task reminders
        users = User.objects.filter(task_reminders=True)
        stats['total_users'] = users.count()
        
        for user in users:
            try:
                # Get user's timezone
                import pytz
                user_tz = pytz.timezone(user.timezone)
                user_now = now.astimezone(user_tz)
                current_time = user_now.time()
                
                # Check if current time matches user's reminder time (within minute window)
                if current_time.hour == user.reminder_time.hour and current_time.minute == user.reminder_time.minute:
                    # Get pending tasks due within 7 days
                    today = user_now.date()
                    next_week = today + timedelta(days=7)
                    
                    tasks = Task.objects.filter(
                        user=user,
                        due_date__date__gte=today,
                        due_date__date__lte=next_week,
                        status__in=['pending', 'not_submitted'],  # Exclude 'done' tasks
                    ).order_by('due_date')
                    
                    if tasks.exists():
                        for task in tasks:
                            try:
                                send_task_reminder_email(user, task, now)
                                stats['reminders_sent'] += 1
                            except Exception as e:
                                logger.error(f"Error sending reminder for task {task.id}: {str(e)}")
                                stats['errors'] += 1
                                
            except Exception as e:
                logger.error(f"Error processing reminders for user {user.id}: {str(e)}")
                stats['errors'] += 1
        
        if stats['reminders_sent'] > 0:
            logger.info(f"Daily reminders: {stats['reminders_sent']} sent, {stats['errors']} errors")
        
    except Exception as e:
        logger.error(f"Error in send_daily_reminders: {str(e)}")
        stats['errors'] += 1
    
    return stats


def send_task_reminder_email(user, task, scheduled_time):
    """
    Send individual task reminder email and log it.
    """
    try:
        context = {
            'user': user,
            'task': task,
            'days_until_due': task.get_days_left(),
        }
        
        html_content = render_to_string('emails/task_reminder.html', context)
        text_content = strip_tags(html_content)
        
        # Send email (uses both console and Gmail backends)
        send_mail(
            subject=f'Task Reminder: {task.name}',
            message=text_content,
            from_email='study-planner@example.com',
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        
        # Log the notification
        NotificationLog.objects.create(
            user=user,
            notification_type='task_reminder',
            subject=f'Task Reminder: {task.name}',
            message_preview=f'Reminder for {task.name}',
            status='sent',
            scheduled_for=scheduled_time,
            sent_at=timezone.now(),
            related_task_id=task.id,
        )
        
        logger.debug(f"Task reminder sent to {user.email} for task {task.id}")
        
    except Exception as e:
        logger.error(f"Failed to send task reminder email: {str(e)}")
        # Log failure
        try:
            NotificationLog.objects.create(
                user=user,
                notification_type='task_reminder',
                subject=f'Task Reminder: {task.name}',
                message_preview=f'Failed to send reminder',
                status='failed',
                scheduled_for=scheduled_time,
                error_message=str(e),
                related_task_id=task.id,
            )
        except:
            pass
        raise


def cleanup_old_reminder_logs():
    """
    Delete notification logs older than 30 days.
    Keeps database clean and performant.
    """
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = NotificationLog.objects.filter(
        sent_at__lt=cutoff_date
    ).delete()
    logger.info(f"Cleaned up {deleted_count} old notification logs")
    return deleted_count


def send_daily_schedule_emails():
    """
    Send tomorrow's class schedule to all users who have enabled schedule reminders.
    Runs once daily at a scheduled time.
    """
    now = timezone.now()
    stats = {
        'total_users': 0,
        'emails_sent': 0,
        'errors': 0,
    }
    
    try:
        # Get all active users who want schedule reminders
        from django.db.models import Q
        users = User.objects.filter(
            schedule_reminders=True,
            is_active=True,
            is_email_verified=True
        )
        stats['total_users'] = users.count()
        
        if stats['total_users'] == 0:
            logger.info("No users with schedule reminders enabled")
            return stats
        
        for user in users:
            try:
                # Get user's timezone
                import pytz
                user_tz = pytz.timezone(user.timezone)
                user_now = now.astimezone(user_tz)
                
                # Calculate tomorrow's date
                tomorrow = user_now.date() + timedelta(days=1)
                
                # Map date to day of week (0=Monday, 6=Sunday)
                day_name_map = {
                    0: 'monday',
                    1: 'tuesday',
                    2: 'wednesday',
                    3: 'thursday',
                    4: 'friday',
                    5: 'saturday',
                    6: 'sunday',
                }
                tomorrow_day_name = day_name_map[tomorrow.weekday()]
                
                # Get all classes for tomorrow
                from timetable.models import TimetableEntry
                tomorrow_classes = TimetableEntry.objects.filter(
                    user=user,
                    day_of_week=tomorrow_day_name,
                ).order_by('start_time')
                
                # Send email
                send_schedule_email(user, tomorrow, tomorrow_classes, now)
                stats['emails_sent'] += 1
                
            except Exception as e:
                logger.error(f"Error sending schedule email to user {user.id}: {str(e)}")
                stats['errors'] += 1
        
        if stats['emails_sent'] > 0:
            logger.info(f"Daily schedule emails: {stats['emails_sent']} sent, {stats['errors']} errors")
        
    except Exception as e:
        logger.error(f"Error in send_daily_schedule_emails: {str(e)}")
        stats['errors'] += 1
    
    return stats


def send_schedule_email(user, schedule_date, classes, scheduled_time):
    """
    Send daily schedule email for a specific user.
    
    Args:
        user: User instance
        schedule_date: Date object for the schedule
        classes: QuerySet of TimetableEntry objects for that day
        scheduled_time: When the email was scheduled to send
    """
    try:
        context = {
            'user': user,
            'schedule_date': schedule_date,
            'classes': classes,
        }
        
        html_content = render_to_string('emails/daily_schedule.html', context)
        text_content = render_to_string('emails/daily_schedule.txt', context)
        
        # Send email
        send_mail(
            subject=f"Your Schedule for {schedule_date.strftime('%A, %B %d')}",
            message=text_content,
            from_email='study-planner@example.com',
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        
        # Log the notification
        NotificationLog.objects.create(
            user=user,
            notification_type='daily_schedule',
            subject=f"Your Schedule for {schedule_date.strftime('%A, %B %d')}",
            message_preview=f"Schedule for {classes.count()} classes",
            status='sent',
            scheduled_for=scheduled_time,
            sent_at=timezone.now(),
        )
        
        logger.debug(f"Schedule email sent to {user.email} for {schedule_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        logger.error(f"Failed to send schedule email: {str(e)}")
        # Log failure
        try:
            NotificationLog.objects.create(
                user=user,
                notification_type='daily_schedule',
                subject=f"Your Schedule for {schedule_date.strftime('%A, %B %d')}",
                message_preview=f"Failed to send schedule",
                status='failed',
                scheduled_for=scheduled_time,
                error_message=str(e),
            )
        except:
            pass
        raise


def register_schedulers(scheduler):
    """
    Register all scheduler jobs with APScheduler.
    Called from tasks/apps.py when Django initializes.
    """
    try:
        from django.conf import settings
        
        # Send reminders every minute (checks happen inside send_daily_reminders)
        scheduler.add_job(
            send_daily_reminders,
            'cron',
            minute='*',  # Every minute
            id='send_daily_reminders',
            name='Send daily task reminders',
            replace_existing=True,
            max_instances=1,
        )
        logger.info("✅ Registered: Daily task reminders (every minute)")
        
        # Send schedule emails at configured time (default: 6 PM UTC)
        schedule_hour = getattr(settings, 'SCHEDULE_EMAIL_HOUR', 18)
        schedule_minute = getattr(settings, 'SCHEDULE_EMAIL_MINUTE', 0)
        
        scheduler.add_job(
            send_daily_schedule_emails,
            'cron',
            hour=schedule_hour,
            minute=schedule_minute,
            id='send_daily_schedule_emails',
            name='Send daily class schedule',
            replace_existing=True,
            max_instances=1,
        )
        logger.info(f"✅ Registered: Daily schedule emails ({schedule_hour}:{schedule_minute:02d})")
        
        # Clean up old logs daily at 03:00 AM
        scheduler.add_job(
            cleanup_old_reminder_logs,
            'cron',
            hour=3,
            minute=0,
            id='cleanup_reminder_logs',
            name='Clean up old notification logs',
            replace_existing=True,
            max_instances=1,
        )
        logger.info("✅ Registered: Cleanup old logs (daily at 03:00)")
        
    except Exception as e:
        logger.error(f"Error registering task schedulers: {str(e)}")

