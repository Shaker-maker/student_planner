from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from tasks.models import Task, ReminderLog
from tasks.email_service import ReminderEmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send daily personalized reminders for pending tasks to all users at their preferred time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sending reminders even if already sent today',
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Send reminder only to a specific user email',
        )

    def handle(self, *args, **options):
        force = options['force']
        user_email = options.get('user_email')
        
        now = timezone.now()
        today = now.date()
        current_hour = now.hour
        current_minute = now.minute
        
        self.stdout.write(self.style.SUCCESS(f"Starting reminder service at {now.strftime('%Y-%m-%d %H:%M:%S')}"))
        
        try:
            # Get all active users with email notifications enabled
            if user_email:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                users = User.objects.filter(email=user_email, email_notifications=True)
            else:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                users = User.objects.filter(email_notifications=True, is_active=True)
            
            stats = {
                'total_users_checked': 0,
                'reminders_sent': 0,
                'reminders_failed': 0,
                'users_eligible': 0,
            }
            
            for user in users:
                stats['total_users_checked'] += 1
                
                # Check if current time matches user's reminder time
                user_reminder_hour = user.reminder_time.hour
                user_reminder_minute = user.reminder_time.minute
                
                # Allow a 10-minute window for reminder sending
                time_window_start = user_reminder_hour * 60 + user_reminder_minute
                time_window_end = time_window_start + 10
                current_time = current_hour * 60 + current_minute
                
                # For testing, you can force send reminders regardless of time
                should_send = force or (time_window_start <= current_time < time_window_end)
                
                if should_send:
                    stats['users_eligible'] += 1
                    
                    # Get all pending/not_submitted tasks for this user that haven't passed yet
                    tasks = Task.objects.filter(
                        user=user,
                        due_date__date__gte=today,
                        status__in=['pending', 'not_submitted']
                    )
                    
                    for task in tasks:
                        # Check if reminder already sent today (unless forcing)
                        reminder_exists = ReminderLog.objects.filter(
                            task=task,
                            user=user,
                            sent_date=today
                        ).exists()
                        
                        if not reminder_exists or force:
                            if ReminderEmailService.send_reminder_email(task, user):
                                stats['reminders_sent'] += 1
                            else:
                                stats['reminders_failed'] += 1
            
            # Display results
            self.stdout.write(self.style.SUCCESS("\n" + "="*60))
            self.stdout.write(self.style.SUCCESS("📊 REMINDER SERVICE SUMMARY"))
            self.stdout.write(self.style.SUCCESS("="*60))
            self.stdout.write(f"Total users checked: {stats['total_users_checked']}")
            self.stdout.write(f"Users eligible for reminders: {stats['users_eligible']}")
            self.stdout.write(self.style.SUCCESS(f"✅ Reminders sent: {stats['reminders_sent']}"))
            if stats['reminders_failed'] > 0:
                self.stdout.write(self.style.ERROR(f"❌ Reminders failed: {stats['reminders_failed']}"))
            self.stdout.write(self.style.SUCCESS("="*60))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending reminders: {str(e)}"))
            logger.exception("Error in send_daily_reminders command")
