from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import NotificationPreference

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize notification preferences for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace existing notification preferences',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        
        users = User.objects.all()
        created_count = 0
        skipped_count = 0
        
        for user in users:
            notification_pref, created = NotificationPreference.objects.get_or_create(
                user=user,
                defaults={
                    'email_notifications': user.email_notifications,
                    'task_reminders_enabled': True,
                    'class_reminders_enabled': True,
                    'reminder_time': user.reminder_time,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created notification preferences for {user.email}')
                )
            else:
                skipped_count += 1
                if replace:
                    notification_pref.email_notifications = user.email_notifications
                    notification_pref.reminder_time = user.reminder_time
                    notification_pref.save()
                    self.stdout.write(
                        self.style.WARNING(f'Updated notification preferences for {user.email}')
                    )
        
        summary = f'\n✅ Created: {created_count}'
        if replace:
            summary += f'\n⚠️  Updated: {skipped_count}'
        else:
            summary += f'\n⏭️  Skipped (already exist): {skipped_count}'
        
        self.stdout.write(self.style.SUCCESS(summary))
