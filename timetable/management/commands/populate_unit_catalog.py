"""
Management command to populate Unit Catalog from existing timetable entries.

Usage:
    python manage.py populate_unit_catalog           # Populate from DB entries
    python manage.py populate_unit_catalog --from-file=units.csv  # From CSV file
"""
from django.core.management.base import BaseCommand
from timetable.models import TimetableEntry, UnitCatalog
import csv


class Command(BaseCommand):
    help = 'Populate unit catalog from existing timetable entries or CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-file',
            type=str,
            default=None,
            help='CSV file with columns: unit_code,unit_name,department,credits'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing catalog entries'
        )

    def handle(self, *args, **options):
        if options['from_file']:
            self._populate_from_file(options['from_file'], options.get('update', False))
        else:
            self._populate_from_database(options.get('update', False))

    def _populate_from_database(self, update=False):
        """Extract unique units from existing timetable entries."""
        # Get unique unit codes from timetable
        entries = TimetableEntry.objects.values('unit_code', 'unit_name').distinct()
        
        created = 0
        updated = 0
        
        self.stdout.write(f"📚 Found {entries.count()} unique units in timetable\n")
        
        for entry in entries:
            unit_code = entry['unit_code'].strip()
            unit_name = entry['unit_name'].strip()
            
            if not unit_code:
                continue
            
            # Skip if code matches name exactly (incomplete extraction)
            if unit_code.upper() == unit_name.upper():
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  {unit_code:15} → {unit_name:40} (incomplete - will need manual entry)"
                    )
                )
                continue
            
            try:
                catalog_entry, is_created = UnitCatalog.objects.get_or_create(
                    unit_code=unit_code,
                    defaults={'unit_name': unit_name}
                )
                
                if is_created:
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Created: {unit_code:15} → {unit_name}"
                        )
                    )
                elif update and catalog_entry.unit_name != unit_name:
                    catalog_entry.unit_name = unit_name
                    catalog_entry.save()
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"🔄 Updated: {unit_code:15} → {unit_name}"
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Error with {unit_code}: {str(e)}"
                    )
                )
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"✅ Created: {created}"))
        self.stdout.write(self.style.SUCCESS(f"🔄 Updated: {updated}"))
        self.stdout.write(f"{'='*60}")

    def _populate_from_file(self, filepath, update=False):
        """Load units from CSV file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames or 'unit_code' not in reader.fieldnames:
                    self.stdout.write(self.style.ERROR("CSV must have 'unit_code' column"))
                    return
                
                created = 0
                updated = 0
                
                for row in reader:
                    unit_code = row['unit_code'].strip()
                    unit_name = row.get('unit_name', unit_code).strip()
                    department = row.get('department', '').strip()
                    credits = row.get('credits', '')
                    
                    if not unit_code or not unit_name:
                        continue
                    
                    try:
                        catalog_entry, is_created = UnitCatalog.objects.get_or_create(
                            unit_code=unit_code,
                            defaults={
                                'unit_name': unit_name,
                                'department': department,
                                'credits': int(credits) if credits and credits.isdigit() else None
                            }
                        )
                        
                        if is_created:
                            created += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✅ Created: {unit_code:15} → {unit_name}"
                                )
                            )
                        elif update:
                            catalog_entry.unit_name = unit_name
                            if department:
                                catalog_entry.department = department
                            if credits and credits.isdigit():
                                catalog_entry.credits = int(credits)
                            catalog_entry.save()
                            updated += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ Error with {unit_code}: {str(e)}"
                            )
                        )
                
                self.stdout.write(f"\n{'='*60}")
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {created}"))
                self.stdout.write(self.style.SUCCESS(f"🔄 Updated: {updated}"))
                self.stdout.write(f"{'='*60}")
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {filepath}"))
