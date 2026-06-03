#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
sys.path.insert(0, '/home/shaker/Documents/student_study_planner')
django.setup()

from timetable.models import TimetableEntry

entry = TimetableEntry.objects.first()
if entry:
    print(f'\nSaved Entry:')
    print(f'  Code: {entry.unit_code}')
    print(f'  Name: {entry.unit_name}')
    print(f'  GROUP: {entry.extracted_entities.get("group")}')
    print(f'  User Course: {entry.user.course}')
    print(f'  User Year: {entry.user.year_of_study}')
    print(f'  User Semester: {entry.user.semester}')
    print(f'\n  User Expected GROUP: {entry.user.course[:3].upper()}_Y{entry.user.year_of_study}_S{entry.user.semester}')
    print(f'  Entry GROUP: {entry.extracted_entities.get("group")}')
    
    if entry.extracted_entities.get("group") != f'{entry.user.course[:3].upper()}_Y{entry.user.year_of_study}_S{entry.user.semester}':
        print(f'\n⚠️ GROUP MISMATCH!')
        print(f'   This entry was probably allowed through by mistake')
