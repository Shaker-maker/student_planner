"""
Management command to send daily schedule emails immediately (for testing).

Usage:
    python manage.py send_schedule_emails        # Send to all users
    python manage.py send_schedule_emails --user=email@example.com   # Send to specific user
    python manage.py send_schedule_emails --date=2026-06-03  # Send for specific date
    python manage.py send_schedule_emails --tomorrow  # Send for tomorrow
    python manage.py send_schedule_emails --all-days  # Send for all 7 days of week
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
import pytz


class Command(BaseCommand):
    help = 'Send daily schedule emails (useful for testing)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default=None,
            help='Send to specific user email (e.g., user@example.com)'
        )
        parser.add_argument(
            '--date',
            type=str,
            default=None,
            help='Send schedule for specific date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--tomorrow',
            action='store_true',
            help='Send for tomorrow (default behavior)'
        )
        parser.add_argument(
            '--today',
            action='store_true',
            help='Send for today'
        )
        parser.add_argument(
            '--all-days',
            action='store_true',
            help='Send for all 7 days of the week'
        )

    def handle(self, *args, **options):
        from accounts.models import User
        from tasks.schedulers import send_schedule_email
        from timetable.models import TimetableEntry
        from django.utils import timezone

        # Determine which users to send to
        if options['user']:
            try:
                users = [User.objects.get(email=options['user'])]
                self.stdout.write(f"✅ Found user: {options['user']}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ User not found: {options['user']}"))
                return
        else:
            users = User.objects.filter(schedule_reminders=True, is_active=True, is_email_verified=True)
            self.stdout.write(f"✅ Found {users.count()} users with schedule reminders enabled")

        # Determine date(s) to send for
        dates_to_send = []
        now_utc = timezone.now()

        if options['all_days']:
            # Send for all 7 days
            for i in range(7):
                dates_to_send.append(now_utc.date() + timedelta(days=i))
            self.stdout.write(f"📅 Sending for all 7 days")
        elif options['date']:
            # Parse specific date
            try:
                date_obj = datetime.strptime(options['date'], '%Y-%m-%d').date()
                dates_to_send.append(date_obj)
                self.stdout.write(f"📅 Sending for specific date: {options['date']}")
            except ValueError:
                self.stdout.write(self.style.ERROR(f"❌ Invalid date format. Use YYYY-MM-DD"))
                return
        elif options['today']:
            # Today
            dates_to_send.append(now_utc.date())
            self.stdout.write(f"📅 Sending for today")
        else:
            # Default: tomorrow
            dates_to_send.append(now_utc.date() + timedelta(days=1))
            self.stdout.write(f"📅 Sending for tomorrow")

        # Day name mapping
        day_names = {
            0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
            4: 'friday', 5: 'saturday', 6: 'sunday'
        }

        # Send emails
        total_sent = 0
        total_errors = 0

        for user in users:
            for schedule_date in dates_to_send:
                try:
                    day_name = day_names[schedule_date.weekday()]
                    
                    # Get classes for that day
                    classes = TimetableEntry.objects.filter(
                        user=user,
                        day_of_week=day_name,
                    ).order_by('start_time')
                    
                    # Send email
                    send_schedule_email(user, schedule_date, classes, now_utc)
                    total_sent += 1
                    
                    class_count = classes.count()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {user.email} - {schedule_date.strftime('%A, %B %d')} ({class_count} classes)"
                        )
                    )
                except Exception as e:
                    total_errors += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ {user.email} - {schedule_date.strftime('%A, %B %d')}: {str(e)}"
                        )
                    )

        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"✅ Sent: {total_sent}"))
        if total_errors > 0:
            self.stdout.write(self.style.ERROR(f"❌ Errors: {total_errors}"))
        self.stdout.write("="*60)
