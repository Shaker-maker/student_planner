"""
APScheduler tasks for sending class reminders (1 hour and 1 day before).
Automatically started when Django loads (via timetable/apps.py).

Note: This is simplified to work with the current notification system.
Avoid duplicate emails via NotificationLog timestamps.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.models import User
from timetable.models import TimetableEntry
from notifications.models import NotificationLog

logger = logging.getLogger(__name__)

# Track reminders already sent this minute to prevent duplicates
_reminders_sent_this_minute = {}


def send_class_reminders():
    """
    Send class reminders 1 hour and 1 day before class starts.
    Called every 30 minutes by the scheduler.
    NOTE: Class reminders are currently simplified. For full functionality,
    add ReminderLog model to track which reminders have been sent.
    """
    now = timezone.now()
    stats = {
        'reminders_checked': 0,
        'reminders_sent': 0,
        'errors': 0,
    }
    
    try:
        # Get all users who want class reminders
        users = User.objects.filter(class_reminders=True)
        
        for user in users:
            try:
                import pytz
                user_tz = pytz.timezone(user.timezone)
                user_now = now.astimezone(user_tz)
                
                # Get this and next day's entries
                today_start = user_now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow_end = today_start + timedelta(days=2)
                
                entries = TimetableEntry.objects.filter(
                    user=user,
                    datetime__gte=today_start,
                    datetime__lt=tomorrow_end,
                )
                
                for entry in entries:
                    stats['reminders_checked'] += 1
                    
                    # Convert entry time to user's timezone
                    entry_time = entry.datetime.astimezone(user_tz)
                    time_until_entry = (entry_time - user_now).total_seconds()
                    
                    # 1-hour reminder: send if within 60 ± 10 minutes
                    if 3000 <= time_until_entry <= 4200:  # 50-70 minutes
                        reminder_key = f"{user.id}_{entry.id}_1h_{int(now.timestamp()/600)}"
                        if reminder_key not in _reminders_sent_this_minute:
                            send_class_reminder_email(user, entry, '1_hour', now)
                            _reminders_sent_this_minute[reminder_key] = True
                            stats['reminders_sent'] += 1
                    
                    # 1-day reminder: send if within 24h ± 30 minutes
                    elif 85200 <= time_until_entry <= 87600:  # 23h 40m - 24h 20m
                        reminder_key = f"{user.id}_{entry.id}_1d_{int(now.timestamp()/3600)}"
                        if reminder_key not in _reminders_sent_this_minute:
                            send_class_reminder_email(user, entry, '1_day', now)
                            _reminders_sent_this_minute[reminder_key] = True
                            stats['reminders_sent'] += 1
                            
            except Exception as e:
                logger.error(f"Error processing class reminders for user {user.id}: {str(e)}")
                stats['errors'] += 1
        
        if stats['reminders_sent'] > 0:
            logger.info(f"Class reminders: {stats['reminders_sent']} sent")
        
    except Exception as e:
        logger.error(f"Error in send_class_reminders: {str(e)}")
        stats['errors'] += 1
    
    return stats


def send_class_reminder_email(user, entry, reminder_type, scheduled_time):
    """
    Send individual class reminder email.
    """
    try:
        reminder_label = "1 Hour Before" if reminder_type == '1_hour' else "1 Day Before"
        
        context = {
            'user': user,
            'entry': entry,
            'reminder_type': reminder_label,
            'subject': entry.subject,
            'classroom': entry.classroom or 'TBA',
            'lecturer': entry.lecturer or 'TBA',
            'start_time': entry.datetime.strftime('%H:%M'),
        }
        
        html_content = render_to_string('emails/class_reminder.html', context)
        text_content = strip_tags(html_content)
        
        # Send email
        send_mail(
            subject=f'Class Reminder ({reminder_label}): {entry.subject}',
            message=text_content,
            from_email='study-planner@example.com',
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        
        # Log the notification
        NotificationLog.objects.create(
            user=user,
            notification_type='class_reminder',
            subject=f'Class Reminder ({reminder_label}): {entry.subject}',
            message_preview=f'{reminder_label} reminder for {entry.subject}',
            status='sent',
            scheduled_for=scheduled_time,
            sent_at=timezone.now(),
            related_class_id=entry.id,
        )
        
        logger.debug(f"Class reminder ({reminder_type}) sent to {user.email} for {entry.subject}")
        
    except Exception as e:
        logger.error(f"Failed to send class reminder email: {str(e)}")
        # Log failure
        try:
            NotificationLog.objects.create(
                user=user,
                notification_type='class_reminder',
                subject=f'Class Reminder: {entry.subject}',
                message_preview=f'Failed to send reminder',
                status='failed',
                scheduled_for=scheduled_time,
                error_message=str(e),
                related_class_id=entry.id,
            )
        except:
            pass


def register_class_schedulers(scheduler):
    """
    Register class reminder scheduler jobs with APScheduler.
    Called from timetable/apps.py with the scheduler instance.
    """
    try:
        # Send class reminders every 30 minutes
        scheduler.add_job(
            send_class_reminders,
            'cron',
            minute='*/30',  # Every 30 minutes
            id='send_class_reminders',
            name='Send class reminders',
            replace_existing=True,
            max_instances=1,
        )
        logger.info("✅ Registered: Class reminders (every 30 minutes)")
        
    except Exception as e:
        logger.error(f"Error registering class reminder schedulers: {str(e)}")

