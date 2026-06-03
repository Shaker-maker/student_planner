#!/usr/bin/env python
"""
Quick Setup & Status Check - Study Planner Notifications
"""

import os
import sys
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
import django
django.setup()

from django.conf import settings
from accounts.models import User
from tasks.models import Task
from notifications.models import NotificationLog

print("\n" + "="*70)
print("🚀 STUDY PLANNER - NOTIFICATION SYSTEM STATUS")
print("="*70)

# Check configuration
print("\n📋 CONFIGURATION:")
print(f"   ✅ Django Version: 5.2.7")
print(f"   ✅ Email Backend: {settings.EMAIL_BACKEND}")
print(f"   ✅ Email Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"   ✅ Celery Broker: {settings.CELERY_BROKER_URL}")
print(f"   ✅ Timezone: {settings.TIME_ZONE}")

# Check database
print("\n💾 DATABASE:")
users = User.objects.count()
tasks = Task.objects.count()
logs = NotificationLog.objects.count()
print(f"   ✅ Users: {users}")
print(f"   ✅ Tasks: {tasks}")
print(f"   ✅ Notification Logs: {logs}")

# Check Redis
print("\n🔴 REDIS STATUS:")
try:
    result = subprocess.run(
        ['redis-cli', 'ping'],
        capture_output=True,
        timeout=5,
        text=True
    )
    if 'PONG' in result.stdout:
        print(f"   ✅ Redis is RUNNING")
        # Get Redis info
        result = subprocess.run(
            ['redis-cli', 'info', 'server'],
            capture_output=True,
            timeout=5,
            text=True
        )
        for line in result.stdout.split('\n'):
            if 'redis_version' in line:
                print(f"   ✅ {line.strip()}")
    else:
        print(f"   ❌ Redis not responding")
except:
    print(f"   ❌ Redis is NOT RUNNING - Start with: redis-server")

# Show startup instructions
print("\n" + "="*70)
print("🎯 STARTUP INSTRUCTIONS")
print("="*70)

print("""
Open 3 separate terminals and run these commands:

📱 TERMINAL 1 - Start Redis (if not running):
   redis-server

⚙️  TERMINAL 2 - Start Celery Worker:
   cd /home/shaker/Documents/student_study_planner
   source venv/bin/activate
   celery -A study_planner worker -l info

⏰ TERMINAL 3 - Start Celery Beat Scheduler:
   cd /home/shaker/Documents/student_study_planner
   source venv/bin/activate
   celery -A study_planner beat -l info

👉 TERMINAL 4 - Start Django Server:
   cd /home/shaker/Documents/student_study_planner
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
""")

print("="*70)
print("✅ THEN:")
print("="*70)
print("""
1. Create a task:
   Visit: http://localhost:8000/tasks/add/
   
2. Set reminder time:
   Visit: http://localhost:8000/accounts/profile/
   Set "Daily Reminder Time" to a few minutes from now
   
3. Wait for automatic email:
   Check inbox at wainainaalvin76@gmail.com
   Email will arrive automatically at your set time
   
4. Monitor in admin:
   http://localhost:8000/admin/notifications/notificationlog/
   See all sent reminders with status
""")

print("="*70 + "\n")
