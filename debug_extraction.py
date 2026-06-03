#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
sys.path.insert(0, '/home/shaker/Documents/student_study_planner')
django.setup()

from timetable.models import PDFDocument, TimetableEntry, ExtractionLog
from accounts.models import User

# Check PDFs
pdfs = PDFDocument.objects.all()
print(f"\n{'='*80}")
print(f"PDF EXTRACTION RESULTS ({pdfs.count()} PDFs)")
print(f"{'='*80}\n")

for pdf in pdfs:
    print(f"PDF: {pdf.original_filename}")
    print(f"  Status: {pdf.processing_status}")
    print(f"  Tables Detected: {pdf.tables_detected}")
    print(f"  Entries Extracted: {pdf.entries_extracted}")
    print(f"  Method: {pdf.extraction_method}")
    print()

# Check extraction logs
logs = ExtractionLog.objects.all()
print(f"\n{'='*80}")
print(f"EXTRACTION LOGS ({logs.count()} logs)")
print(f"{'='*80}\n")

for log in logs:
    print(f"Log ID: {log.id}")
    print(f"  Success: {log.success}")
    print(f"  Method: {log.extraction_method}")
    print(f"  Entries Found: {log.entries_found}")
    print(f"  Detected Tables: {len(log.detected_tables)}")
    print(f"  Parsed Entities: {len(log.parsed_entities)}")
    print()

# Check user
user = User.objects.filter(year_of_study__isnull=False).first()
if user:
    print(f"{'='*80}")
    print(f"USER INFO")
    print(f"{'='*80}")
    print(f"User: {user.username}")
    print(f"Course: {user.course}")
    print(f"Year: {user.year_of_study}")
    print(f"Semester: {user.semester}")
    print(f"Expected GROUP: {user.course[:3].upper()}_Y{user.year_of_study}_S{user.semester if user.semester else '?'}")
