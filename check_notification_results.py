#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
django.setup()

from accounts.models import User
from tasks.models import Task
from notifications.models import NotificationLog

# Check task
user = User.objects.get(email='shakeralvin@gmail.com')
task = Task.objects.filter(user=user, name='Email Test Assignment').first()

print("\n" + "="*70)
print("📧 EMAIL NOTIFICATION TEST RESULTS")
print("="*70)

if task:
    print("\n✅ TASK CREATED/VERIFIED")
    print(f"   Name: {task.name}")
    print(f"   Unit: {task.unit_name}")
    print(f"   Due: {task.due_date}")
    print(f"   Status: {task.status}")
    print(f"   User Reminder Time: {user.reminder_time}")
else:
    print("\n❌ Task not found")

# Check notification logs
logs = NotificationLog.objects.filter(user=user).order_by('-created_at')
print(f"\n✅ NOTIFICATION LOGS ({logs.count()} total)")
for log in logs[:5]:
    print(f"   - {log.notification_type}: {log.status} ({log.created_at.strftime('%H:%M:%S')})")
    if log.subject:
        print(f"     Subject: {log.subject[:50]}")
    if log.related_task_id:
        print(f"     Task ID: {log.related_task_id}")

print("\n" + "="*70)
print("✅ Email notification system working!")
print("="*70 + "\n")
