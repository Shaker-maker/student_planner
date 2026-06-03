#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
sys.path.insert(0, '/home/shaker/Documents/student_study_planner')
django.setup()

from timetable.models import ExtractionLog

log = ExtractionLog.objects.first()

if log and log.parsed_entities:
    print(f"\n{'='*80}")
    print(f"GROUPS IN EXTRACTED ENTRIES")
    print(f"{'='*80}\n")
    
    groups = {}
    for entity_key, entity_data in log.parsed_entities.items():
        if isinstance(entity_data, dict):
            group = entity_data.get('group', 'NO_GROUP')
            unit_code = entity_data.get('unit_code', 'Unknown')
            unit_name = entity_data.get('unit_name', '(no name)')
            
            if group not in groups:
                groups[group] = []
            groups[group].append((unit_code, unit_name))
    
    for group, units in sorted(groups.items()):
        print(f"GROUP: {group}")
        for code, name in units[:3]:  # Show first 3
            print(f"  - {code}: {name}")
        if len(units) > 3:
            print(f"  ... and {len(units)-3} more")
        print()
