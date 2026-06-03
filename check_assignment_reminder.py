#!/usr/bin/env python
import os
import django
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
django.setup()

from django.utils import timezone
from accounts.models import User
from tasks.models import Task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from notifications.models import NotificationLog

print("\n" + "="*70)
print("📧 ASSIGNMENT 1 - REMINDER EMAIL CHECK")
print("="*70)

# Get current time
now = timezone.now()
print(f"\n⏰ Current time: {now.strftime('%H:%M:%S')} ({now.tzname()})")

# Get user
user = User.objects.get(email='shakeralvin@gmail.com')
task = Task.objects.filter(user=user, name="Assignment 1").first()

if not task:
    print("❌ Task 'Assignment 1' not found")
else:
    print(f"\n✅ Task found: {task.name}")
    print(f"   Unit: {task.unit_name}")
    print(f"   Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Reminder set for: {user.reminder_time.strftime('%H:%M')} daily")
    
    current_time_int = int(now.strftime("%H%M"))
    reminder_time_int = int(user.reminder_time.strftime("%H%M"))
    
    print(f"\n⏳ Status:")
    print(f"   Current: {current_time_int}")
    print(f"   Reminder: {reminder_time_int}")
    
    if current_time_int < reminder_time_int:
        minutes_left = (reminder_time_int - current_time_int) // 100 * 60 + (reminder_time_int - current_time_int) % 100
        hours = minutes_left // 60
        mins = minutes_left % 60
        print(f"   ⏰ Will trigger automatically in: {hours}h {mins}m")
    else:
        print(f"   ✅ Time has passed! Will trigger at 18:46 tomorrow")
    
    # Send manual email now for testing
    print(f"\n📧 Sending test email now...")
    try:
        context = {
            'user': user,
            'task': task,
            'days_until_due': task.get_days_left(),
        }
        html_content = render_to_string('emails/task_reminder.html', context)
        text_content = strip_tags(html_content)
        
        sent = send_mail(
            subject=f'Task Reminder: {task.name}',
            message=text_content,
            from_email='study-planner@example.com',
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        
        print(f"   ✅ Email SENT! (Delivery result: {sent})")
        
        # Log it
        log = NotificationLog.objects.create(
            user=user,
            notification_type='task_reminder',
            subject=f'Task Reminder: {task.name}',
            message_preview=f'Reminder for {task.name}',
            status='sent',
            scheduled_for=now,
            sent_at=now,
            related_task_id=task.id,
        )
        print(f"   ✅ Logged in database (Log ID: {str(log.id)[:8]}...)")
        
    except Exception as e:
        print(f"   ❌ Error sending: {str(e)}")

print("\n" + "="*70)
print("📲 next steps:")
print("="*70)
print("""
1. Check your email inbox at: wainainaalvin76@gmail.com
   (Check spam folder if needed)
   
2. At 18:46 every day, Celery will AUTOMATICALLY send reminders
   
3. To change reminder time:
   - Go to: http://localhost:8000/accounts/profile/
   - Change "Reminder Time"
   - Click Save
""")
print("="*70 + "\n")
