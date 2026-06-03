#!/usr/bin/env python
"""Debug script to inspect raw PDF table structure."""

import os
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, '/home/shaker/Documents/student_study_planner')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')

import django
django.setup()

from timetable.utils.pdf_extractor import PDFTableExtractor

def debug_pdf():
    # Find the most recent uploaded PDF
    media_timetables_dir = Path('/home/shaker/Documents/student_study_planner/media/timetables')
    
    if not media_timetables_dir.exists():
        print("❌ Timetables directory not found")
        return
    
    # Find PDF files
    pdfs = list(media_timetables_dir.glob('2026/**/*.pdf'))
    if not pdfs:
        print("❌ No PDF files found")
        return
    
    # Get the most recent
    latest_pdf = max(pdfs, key=lambda f: f.stat().st_mtime)
    print(f"📄 Analyzing: {latest_pdf}")
    print("=" * 80)
    
    # Extract tables
    extractor = PDFTableExtractor(str(latest_pdf))
    tables = extractor.extract_tables()
    
    if not tables:
        print("❌ No tables extracted")
        return
    
    print(f"\n✅ Found {len(tables)} tables\n")
    
    # Show first few tables with raw data
    for table_idx, table in enumerate(tables[:3], 1):
        print(f"\n{'='*80}")
        print(f"TABLE {table_idx}")
        print(f"{'='*80}")
        print(f"Method: {table.get('method', 'unknown')}")
        print(f"Confidence: {table.get('confidence', 'unknown')}")
        print(f"Rows: {len(table['data'])}\n")
        
        # Show all rows
        for row_idx, row in enumerate(table['data']):
            print(f"Row {row_idx}: {row}")
            if row_idx >= 10:  # Limit output
                print(f"... ({len(table['data']) - 10} more rows)")
                break

if __name__ == '__main__':
    debug_pdf()
