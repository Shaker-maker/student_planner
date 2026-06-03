from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from timetable.models import PDFDocument
from timetable.services import TimetableExtractionService
import os
from pathlib import Path

User = get_user_model()


class Command(BaseCommand):
    help = 'Re-extract a timetable PDF with the latest extraction fixes'

    def add_arguments(self, parser):
        parser.add_argument(
            'pdf_path',
            type=str,
            help='Path to the PDF file to extract'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Email of user to assign timetable to',
            default='shakeralvin@gmail.com'
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year of study (1-5)',
            default=1
        )
        parser.add_argument(
            '--semester',
            type=int,
            help='Semester (1-2)',
            default=2
        )

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        user_email = options['user']
        year = options['year']
        semester = options['semester']

        # Verify PDF exists
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'❌ PDF not found: {pdf_path}'))
            return

        # Get or create user
        try:
            user = User.objects.get(email=user_email)
            self.stdout.write(f"✅ Using user: {user_email}")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User not found: {user_email}'))
            return

        # Create PDFDocument
        filename = Path(pdf_path).name
        self.stdout.write(f"\n📄 Creating PDF document: {filename}")
        
        pdf_doc = PDFDocument.objects.create(
            user=user,
            file=pdf_path,  # Store path for now
            original_filename=filename,
            file_size=os.path.getsize(pdf_path),
            processing_status='processing'
        )

        try:
            self.stdout.write(f"🚀 Starting extraction with bug fixes applied...")
            self.stdout.write(f"   - Lookup table extraction (pages 6-8)")
            self.stdout.write(f"   - Multi-hour cell detection")
            
            # Initialize service
            service = TimetableExtractionService(pdf_doc)
            
            # Update user profile for filtering
            user.year_of_study = year
            user.save()
            
            # Run extraction
            count = service.extract()
            
            self.stdout.write(self.style.SUCCESS(f"\n✅ Extraction complete!"))
            self.stdout.write(f"   {count} entries extracted")
            self.stdout.write(f"   Processing time: {service.processing_time:.2f}s")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Extraction failed: {e}"))
            import traceback
            traceback.print_exc()
            pdf_doc.processing_status = 'failed'
            pdf_doc.error_message = str(e)
            pdf_doc.save()
