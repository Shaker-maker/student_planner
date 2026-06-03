#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
sys.path.insert(0, '/home/shaker/Documents/student_study_planner')
django.setup()

from accounts.models import User

users = User.objects.filter(is_active=True)

for user in users:
    print(f"\nUser: {user.email if hasattr(user, 'email') else 'N/A'}")
    print(f"  Course: {user.course}")
    print(f"  Year: {user.year_of_study}")
    print(f"  Semester: {user.semester}")
    
    if all([user.course, user.year_of_study, user.semester]):
        course_prefix = user.course[:3].upper() if user.course else '?'
        group = f"{course_prefix}_Y{user.year_of_study}_S{user.semester}"
        print(f"  Expected GROUP: {group}")
