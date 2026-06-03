"""
Management command to manually send schedule reminders immediately.
Useful for testing and demos.

Usage:
    python manage.py send_schedule_reminders_now
    python manage.py send_schedule_reminders_now --user email@example.com
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.schedulers import send_daily_schedule_emails
from accounts.models import User


class Command(BaseCommand):
    help = 'Manually send tomorrow\'s schedule reminders now (for testing/demos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Send reminder for specific user email only',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n📧 Sending schedule reminders NOW...\n'))
        
        if options['user']:
            # Send for specific user
            try:
                user = User.objects.get(email=options['user'])
                
                # Calculate tomorrow
                from datetime import timedelta
                import pytz
                
                user_tz = pytz.timezone(user.timezone)
                now = timezone.now().astimezone(user_tz)
                tomorrow = now.date() + timedelta(days=1)
                
                # Get tomorrow's classes
                from timetable.models import TimetableEntry
                
                day_name_map = {
                    0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
                    4: 'friday', 5: 'saturday', 6: 'sunday',
                }
                tomorrow_day_name = day_name_map[tomorrow.weekday()]
                
                classes = TimetableEntry.objects.filter(
                    user=user,
                    day_of_week=tomorrow_day_name,
                ).order_by('start_time')
                
                self.stdout.write(f"  User: {user.email} ({user.first_name} {user.last_name})")
                self.stdout.write(f"  Date: {tomorrow.strftime('%A, %B %d, %Y')}")
                self.stdout.write(f"  Classes found: {classes.count()}")
                
                if classes.count() == 0:
                    self.stdout.write(self.style.WARNING('\n  ⚠️  No classes scheduled for tomorrow!'))
                else:
                    self.stdout.write('\n  Classes for tomorrow:')
                    for cls in classes:
                        self.stdout.write(f"    • {cls.unit_code} - {cls.unit_name} @ {cls.start_time}")
                
                # Send email
                from tasks.schedulers import send_schedule_email
                send_schedule_email(user, tomorrow, classes, timezone.now())
                
                self.stdout.write(self.style.SUCCESS(f'\n✅ Reminder sent to {user.email}\n'))
                
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ User not found: {options["user"]}\n'))
        
        else:
            # Send for all users
            stats = send_daily_schedule_emails()
            
            self.stdout.write(f"  Total users: {stats['total_users']}")
            self.stdout.write(f"  ✅ Reminders sent: {stats['emails_sent']}")
            if stats['errors'] > 0:
                self.stdout.write(self.style.ERROR(f"  ❌ Errors: {stats['errors']}"))
            
            self.stdout.write(self.style.SUCCESS('\n✅ All reminders sent!\n'))
