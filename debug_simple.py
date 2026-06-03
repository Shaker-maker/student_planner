#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
sys.path.insert(0, '/home/shaker/Documents/student_study_planner')
django.setup()

from timetable.models import TimetableEntry, ExtractionLog

print(f"\n{'='*80}")
print(f"EXTRACTION SUMMARY")
print(f"{'='*80}\n")

logs = ExtractionLog.objects.all()

for log in logs:
    print(f"Extraction Log:")
    print(f"  Entries Found in PDF: {log.entries_found}")
    print(f"  Success: {log.success}")
    
entries = TimetableEntry.objects.all()
print(f"\nEntries Saved to Database: {entries.count()}")

# Show the one saved entry
if entries.count() > 0:
    entry = entries.first()
    print(f"\nSaved Entry:")
    print(f"  Code: {entry.unit_code}")
    print(f"  Name: {entry.unit_name}")
    print(f"  GROUP: {entry.extracted_entities.get('group')}")

# The problem: Only 1 of 15 entries were saved!
print(f"\n⚠️ PROBLEM: Only {entries.count()} of {logs.first().entries_found if logs.exists() else 0} extracted entries were saved!")
print(f"   This means ~{logs.first().entries_found - entries.count() if logs.exists() else 0} entries were filtered out")
