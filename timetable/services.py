"""
Timetable Extraction Service
Orchestrates the entire AI pipeline: CV → NLP → Scoring → Database
"""
import os
import logging
import time
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from .models import PDFDocument, TimetableEntry, ExtractionLog
from .utils.pdf_extractor import PDFTableExtractor
from .utils.enhanced_pdf_extractor import EnhancedPDFExtractor
from .utils.nlp_processor import TimetableNLPProcessor
from .utils.confidence_scorer import ConfidenceScorer
from .utils.grid_extractor import GridTimetableExtractor

logger = logging.getLogger(__name__)


# Course to Degree Code Mapping
# Maps full course names (as entered by users) to their degree codes (as in GROUP column)
# GROUP column format: CODE_YYEAR_SSEMESTER (e.g., BCS_Y1_S2, BCT_Y1_S2)
COURSE_CODE_MAP = {
    # Full degree names
    'bachelor of science in computer science': 'BCS',
    'bachelor of science in software engineering': 'BSE',
    'bachelor of science in information technology': 'BIT',
    'bachelor of science in computer technology': 'BCT',
    
    # Shorter variations
    'computer science': 'BCS',
    'software engineering': 'BSE',
    'information technology': 'BIT',
    'computer technology': 'BCT',
    
    # Abbreviations
    'cs': 'BCS',
    'se': 'BSE',
    'it': 'BIT',
    'ct': 'BCT',
    'bcs': 'BCS',
    'bse': 'BSE',
    'bit': 'BIT',
    'bct': 'BCT',
}


class TimetableExtractionService:
    """
    Main service for extracting timetables from PDFs.
    Coordinates CV, NLP, and ML components.
    """
    
    def __init__(self, pdf_document: PDFDocument):
        """
        Initialize service with a PDFDocument instance.
        
        Args:
            pdf_document: PDFDocument model instance
        """
        self.pdf_document = pdf_document
        self.user = pdf_document.user
        self.pdf_path = pdf_document.file.path
        
        # Initialize AI components
        # Try enhanced extractor first to get lookup table (pages 6-8)
        self.lookup_table = {}
        self.use_enhanced = False
        
        try:
            # Only extract lookup table from enhanced extractor, not main tables
            # because enhanced table format is incompatible with NLP processor
            import pdfplumber
            with pdfplumber.open(self.pdf_path) as pdf:
                enhanced_extractor = EnhancedPDFExtractor(self.pdf_path)
                enhanced_extractor._extract_lookup_tables(pdf)
                self.lookup_table = enhanced_extractor.lookup_table
            
            if len(self.lookup_table) > 0:
                logger.info(f"✅ Extracted lookup table with {len(self.lookup_table)} units from pages 6-8")
        except Exception as e:
            logger.debug(f"Lookup table extraction not available: {str(e)}")
            self.lookup_table = {}
        
        # Use standard extractor for main tables (pages 1-5)
        # because it returns correct format for NLP processor
        self.extractor = PDFTableExtractor(self.pdf_path)
        
        self.nlp_processor = TimetableNLPProcessor(lookup_table=self.lookup_table)
        self.confidence_scorer = ConfidenceScorer()
        
        # Initialize grid extractor with lookup table for enrichment
        self.grid_extractor = GridTimetableExtractor(lookup_table=self.lookup_table)
        
        # Metrics
        self.start_time = None
        self.processing_time = 0.0
    
    def extract(self) -> int:
        """
        Main extraction method - runs the full AI pipeline.
        
        Returns:
            Number of entries successfully extracted and saved
        
        Raises:
            Exception: If extraction fails
        """
        self.start_time = time.time()
        
        try:
            # Update status
            self.pdf_document.processing_status = 'processing'
            self.pdf_document.save()
            
            logger.info(f"🚀 Starting extraction for: {self.pdf_document.original_filename}")
            logger.info(f"   Using lookup enrichment: {len(self.lookup_table)} units loaded")
            
            # Stage 1: Extract tables using Computer Vision
            logger.info("📊 Stage 1: Computer Vision - Extracting tables...")
            
            # Use standard extractor (returns proper format for NLP)
            tables = self.extractor.extract_tables()
            
            if not tables:
                logger.error("❌ No tables extracted from PDF!")
                raise ValueError("No tables could be extracted from PDF. The file may be corrupted, image-based, or have an unusual format.")
            
            logger.info(f"✅ Found {len(tables)} tables using {self.extractor.extraction_method}")
            for i, table in enumerate(tables, 1):
                logger.info(f"   Table {i}: {table.get('rows', 0)} rows × {table.get('columns', 0)} columns")
            
            # Stage 2: Filter tables by student's year
            user_year = self.user.year_of_study
            if not user_year:
                raise ValueError("Student's year_of_study not set. Please update your profile first.")
            
            logger.info(f"🔍 Stage 2: Filtering tables for Year {user_year}...")
            filtered_tables = self.extractor.filter_tables_by_year(tables, user_year)
            if len(filtered_tables) == len(tables):
                logger.info(f"ℹ️ Using all {len(filtered_tables)} tables (no year-specific headers found)")
            else:
                logger.info(f"✅ {len(filtered_tables)} tables match Year {user_year} headers")
            
            # Stage 3: Extract entities using NLP
            logger.info("🧠 Stage 3: NLP - Extracting entities from tables...")
            raw_entries = self.nlp_processor.batch_process_tables(filtered_tables)
            logger.info(f"✅ Extracted {len(raw_entries)} potential timetable entries")
            
            if not raw_entries:
                logger.warning("⚠️ No entries extracted from tables. This might indicate:")
                logger.warning("   - Tables have unusual formatting")
                logger.warning("   - Missing unit codes or names")
                logger.warning("   - Check PDF structure and format")
            
            # Stage 4: Calculate confidence scores
            logger.info("📈 Stage 4: Calculating confidence scores...")
            scored_entries = self._score_entries(raw_entries)
            logger.info(f"✅ Scored {len(scored_entries)} entries")
            
            # Stage 4.5: Personalize - filter entries for the user's course
            logger.info("👤 Stage 4.5: Personalizing for user's course...")
            personalized_entries = self._filter_for_user_course(scored_entries)
            logger.info(f"✅ Personalized: {len(personalized_entries)} entries for {self.user.course} Year {self.user.year_of_study}")
            
            if len(personalized_entries) == 0:
                logger.warning("⚠️ No entries found for user's course and year")
                logger.warning(f"   User course: {self.user.course}")
                logger.warning(f"   User year: {self.user.year_of_study}")
                logger.warning("   Check that course name matches course codes in PDF")
            
            # Stage 5: Save to database
            logger.info("💾 Stage 5: Saving to database...")
            saved_count = self._save_entries(personalized_entries)
            logger.info(f"✅ Saved {saved_count} entries to database")
            
            # Stage 6: Log extraction for debugging
            self._log_extraction(
                success=True,
                tables=tables,
                entries=personalized_entries,
                method=self.extractor.extraction_method
            )
            
            # Update PDF document with results
            self._update_pdf_document(
                status='completed',
                tables_count=len(tables),
                entries_count=saved_count,
                method=self.extractor.extraction_method
            )
            
            # Calculate processing time
            self.processing_time = time.time() - self.start_time
            self.pdf_document.processing_time_seconds = self.processing_time
            self.pdf_document.save()
            
            logger.info(f"🎉 Extraction completed in {self.processing_time:.2f}s")
            return saved_count
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Extraction failed: {error_msg}")
            
            # Log failed extraction
            self._log_extraction(
                success=False,
                tables=[],
                entries=[],
                method='failed',
                error=error_msg
            )
            
            # Update PDF document status
            self._update_pdf_document(
                status='failed',
                error_message=error_msg
            )
            
            raise
    
    def _score_entries(self, entries: list) -> list:
        """
        Calculate confidence scores for all entries.
        
        Args:
            entries: List of extracted entries
        
        Returns:
            List of entries with confidence scores added
        """
        for entry in entries:
            confidence = self.confidence_scorer.calculate_confidence(entry)
            entry['confidence_score'] = confidence
            entry['confidence_label'] = self.confidence_scorer.get_confidence_label(confidence)
        
        return entries
    
    def _get_user_group_key(self) -> str:
        """
        Get the GROUP key for the user based on their course, year, and semester.
        
        Returns the fully qualified group identifier like 'BCS_Y1_S2'
        used to match against the GROUP column in the timetable.
        
        Returns:
            Group key (e.g., 'BCS_Y1_S2') or empty string if not enough info
        """
        if not self.user.course:
            logger.warning("⚠️ User has no course set. Cannot generate group key.")
            return ""
        
        if not self.user.year_of_study:
            logger.warning("⚠️ User year of study not set. Cannot generate group key.")
            return ""
        
        if not self.user.semester:
            logger.warning("⚠️ User semester not set. Cannot generate group key.")
            return ""
        
        # Normalize and look up degree code
        course_name = self.user.course.lower().strip()
        degree_code = None
        
        # Direct lookup
        if course_name in COURSE_CODE_MAP:
            degree_code = COURSE_CODE_MAP[course_name]
        else:
            # Try various matching strategies
            for key, code in COURSE_CODE_MAP.items():
                if key in course_name or course_name in key:
                    degree_code = code
                    logger.info(f"📚 Matched course '{self.user.course}' to code '{code}'")
                    break
        
        if not degree_code:
            logger.warning(f"⚠️ Course '{self.user.course}' not found in COURSE_CODE_MAP")
            return ""
        
        # Build and return the group key
        group_key = f"{degree_code}_Y{self.user.year_of_study}_S{self.user.semester}"
        logger.info(f"🔍 User group key: {group_key}")
        return group_key
    
    def _extract_course_code(self, unit_code: str) -> str:
        """
        Extract the course code from a unit code.
        
        Supports both formats:
        - Old: "BCT 2105" or "BCT2105" → "BCT"
        - New: "BCT_Y1_S2" or "BCT_Y1" → "BCT"
        
        Args:
            unit_code: The unit code string
        
        Returns:
            The course code (e.g., 'BCT', 'BIT'), or empty string if not found
        """
        if not unit_code:
            return ""
        
        unit_code = unit_code.upper()
        
        # Extract alphabetic prefix (usually 2-4 letters)
        course_code = ""
        for char in unit_code:
            if char.isalpha():
                course_code += char
            else:
                # Stop at first non-letter
                break
        
        return course_code
    
    def _extract_year_from_unit_code(self, unit_code: str) -> int:
        """
        Extract the year of study from a unit code.
        
        Example: "BCT 2105" → 2 (Year 2, since digit is 2)
        
        Args:
            unit_code: The unit code string
        
        Returns:
            The year of study (1-5), or 0 if not found
        """
        if not unit_code:
            return 0
        
        # Look for first digit that indicates year
        for char in unit_code:
            if char.isdigit():
                year = int(char)
                if 1 <= year <= 5:
                    return year
        return 0
    
    def _filter_for_user_course(self, entries: list) -> list:
        """
        Filter entries to only include those matching the user's GROUP.
        
        Uses GROUP column (e.g., BCS_Y1_S2) to match entries instead of
        parsing individual unit codes.
        
        Args:
            entries: List of all extracted entries
        
        Returns:
            List of personalized entries for the user's GROUP
        """
        user_group = self._get_user_group_key()
        
        if not user_group:
            logger.warning("⚠️ Cannot determine user's GROUP. Check course, year, and semester settings.")
            logger.warning(f"   Course: {self.user.course}")
            logger.warning(f"   Year: {self.user.year_of_study}")
            logger.warning(f"   Semester: {self.user.semester}")
            return []
        
        # Filter entries by GROUP column
        personalized = []
        entries_with_group = 0
        entries_matched = 0
        
        for entry in entries:
            entry_group = entry.get('group', '')
            
            if entry_group:
                entries_with_group += 1
            
            # Match by GROUP
            if entry_group == user_group:
                personalized.append(entry)
                entries_matched += 1
        
        # Log statistics
        total = len(entries)
        kept = len(personalized)
        logger.info(f"📊 GROUP-based filtering:")
        logger.info(f"   Total entries: {total}")
        logger.info(f"   Entries with GROUP: {entries_with_group}")
        logger.info(f"   User GROUP: {user_group}")
        logger.info(f"   Matched entries: {kept}")
        
        if kept > 0:
            logger.info(f"✅ Found {kept} entries for {self.user.course} (Year {self.user.year_of_study}, Sem {self.user.semester})")
        else:
            logger.info(f"ℹ️ Found 0 entries for GROUP '{user_group}'")
        
        return personalized
    
    def _save_entries(self, entries: list) -> int:
        """
        Save extracted entries to database.
        Saves each entry in its own transaction to prevent rolling back partial saves.
        
        Args:
            entries: List of scored entries
        
        Returns:
            Number of entries saved
        """
        saved_count = 0
        
        for entry in entries:
            try:
                # Validate required fields and apply defaults
                try:
                    if not self._validate_entry(entry):
                        logger.warning(f"⚠️ Skipping invalid entry: {entry.get('unit_name', 'Unknown')}")
                        continue
                except Exception as e:
                    logger.error(f"❌ Error validating entry: {str(e)}")
                    logger.debug(f"Entry data: {entry}")
                    continue
                
                # Check for duplicates
                if self._is_duplicate(entry):
                    logger.debug(f"ℹ️ Skipping duplicate: {entry.get('unit_name', 'Unknown')}")
                    continue
                
                # Create TimetableEntry in its own transaction
                with transaction.atomic():
                    # Create TimetableEntry
                    time_range = entry.get('time_range', {})
                    
                    # Convert time objects to strings for JSON serialization
                    start_time_str = None
                    end_time_str = None
                    if time_range.get('start_time'):
                        start_time_obj = time_range.get('start_time')
                        start_time_str = start_time_obj.strftime('%H:%M:%S') if hasattr(start_time_obj, 'strftime') else str(start_time_obj)
                    if time_range.get('end_time'):
                        end_time_obj = time_range.get('end_time')
                        end_time_str = end_time_obj.strftime('%H:%M:%S') if hasattr(end_time_obj, 'strftime') else str(end_time_obj)
                    
                    timetable_entry = TimetableEntry.objects.create(
                        user=self.user,
                        pdf_document=self.pdf_document,
                        
                        # Basic info
                        unit_code=entry.get('unit_code', ''),
                        unit_name=entry.get('unit_name', 'Unknown Unit'),
                        venue=entry.get('venue', ''),
                        lecturer=entry.get('lecturer', ''),
                        
                        # Timing
                        day_of_week=entry.get('day', 'monday'),
                        start_time=time_range.get('start_time'),
                        end_time=time_range.get('end_time'),
                        duration_minutes=time_range.get('duration_minutes', 60),
                        duration_hours=round(time_range.get('duration_minutes', 60) / 60, 2),  # Exact decimal hours
                        
                        # Metadata
                        year_of_study=self.user.year_of_study,
                        
                        # AI metadata
                        confidence_score=entry.get('confidence_score', 0.0),
                        extraction_method=entry.get('extraction_method', 'unknown'),
                        is_manually_added=False,
                        is_verified=False,
                        
                        # Debug info - include GROUP and convert time to strings for JSON
                        extracted_entities={
                            'group': entry.get('group', 'NO_GROUP'),
                            'unit_code': entry.get('unit_code', ''),
                            'unit_name': entry.get('unit_name', ''),
                            'raw_text': entry.get('raw_text', ''),
                            'table_number': entry.get('table_number', 0),
                            'confidence_label': entry.get('confidence_label', 'Unknown'),
                            'time_range': {
                                'start_time': start_time_str,
                                'end_time': end_time_str,
                                'duration_minutes': time_range.get('duration_minutes', 60)
                            } if time_range else None
                        }
                    )
                
                saved_count += 1
                logger.debug(f"✅ Saved: {timetable_entry}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save entry: {str(e)}")
                logger.error(f"Entry data: {entry}")
                # Continue to next entry instead of failing the whole process
                continue
        
        return saved_count
    
    def _validate_entry(self, entry: dict) -> bool:
        """
        Validate that entry has required fields.
        Apply defaults for missing data to be more lenient.
        
        Args:
            entry: Entry dictionary
        
        Returns:
            True if valid (after applying defaults), False only if completely empty
        """
        # Must have unit code
        unit_code = entry.get('unit_code', '').strip()
        if not unit_code:
            logger.warning(f"⚠️ Entry missing unit_code, skipping")
            return False
        
        # If unit_name is missing or identical to unit_code, set a placeholder
        unit_name = entry.get('unit_name', '').strip()
        
        if not unit_name or unit_name == unit_code:
            # Use unit code as the name if no name was extracted
            # (better than having it empty)
            entry['unit_name'] = unit_code
            logger.debug(f"ℹ️ No separate unit name found for '{unit_code}', using code as name")
        
        
        # Ensure time_range exists and is valid
        time_range = entry.get('time_range', {})
        if not time_range or not time_range.get('start_time') or not time_range.get('end_time'):
            # No valid times found, assign defaults (9 AM - 10 AM)
            from datetime import time as datetime_time
            entry['time_range'] = {
                'start_time': datetime_time(9, 0),
                'end_time': datetime_time(10, 0),
                'duration_minutes': 60
            }
            logger.debug(f"⚠️ No time found for '{entry.get('unit_name', 'Unknown')}', using default 09:00-10:00")
        
        # Ensure day exists, default to Monday if missing
        if not entry.get('day'):
            entry['day'] = 'monday'
            logger.debug(f"⚠️ No day found for '{entry.get('unit_name', 'Unknown')}', using default Monday")
        
        return True
    
    def _is_duplicate(self, entry: dict) -> bool:
        """
        Check if entry already exists in database.
        
        Args:
            entry: Entry to check
        
        Returns:
            True if duplicate exists
        """
        time_range = entry.get('time_range', {})
        
        exists = TimetableEntry.objects.filter(
            user=self.user,
            unit_name=entry.get('unit_name'),
            day_of_week=entry.get('day'),
            start_time=time_range.get('start_time')
        ).exists()
        
        return exists
    
    def _log_extraction(self, success: bool, tables: list, entries: list, 
                       method: str, error: str = ''):
        """
        Log extraction attempt for debugging.
        
        Args:
            success: Whether extraction succeeded
            tables: List of extracted tables
            entries: List of extracted entries
            method: Extraction method used
            error: Error message if failed
        """
        try:
            # Prepare raw text (sample from tables)
            raw_text = ''
            if tables:
                for table in tables[:2]:  # First 2 tables only
                    table_text = '\n'.join([str(row) for row in table.get('data', [])[:5]])
                    raw_text += f"Table {table.get('table_number')}:\n{table_text}\n\n"
            
            # Limit raw text size
            if len(raw_text) > 5000:
                raw_text = raw_text[:5000] + "\n... [truncated]"
            
            # Prepare confidence scores
            confidence_scores = [e.get('confidence_score', 0) for e in entries]
            
            # Sanitize entries for JSON serialization (convert time objects to strings)
            sanitized_entries = []
            for entry in entries[:5]:
                sanitized = dict(entry)
                # Convert time objects in time_range to strings
                if 'time_range' in sanitized and sanitized['time_range']:
                    time_range = sanitized['time_range']
                    if 'start_time' in time_range and hasattr(time_range['start_time'], 'strftime'):
                        time_range['start_time'] = time_range['start_time'].strftime('%H:%M:%S')
                    if 'end_time' in time_range and hasattr(time_range['end_time'], 'strftime'):
                        time_range['end_time'] = time_range['end_time'].strftime('%H:%M:%S')
                sanitized_entries.append(sanitized)
            
            ExtractionLog.objects.create(
                pdf_document=self.pdf_document,
                extraction_method=method,
                raw_text=raw_text,
                detected_tables=[{
                    'table_number': t.get('table_number'),
                    'rows': t.get('rows'),
                    'columns': t.get('columns'),
                    'confidence': t.get('confidence')
                } for t in tables],
                parsed_entities={
                    'sample_entries': sanitized_entries,
                    'total_count': len(entries)
                },
                success=success,
                confidence_scores=confidence_scores,
                entries_found=len(entries),
                processing_time=time.time() - self.start_time if self.start_time else 0,
                error_details=error
            )
            
            logger.info("✅ Extraction logged successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to log extraction: {str(e)}")
    
    def _update_pdf_document(self, status: str, tables_count: int = 0, 
                            entries_count: int = 0, method: str = '', 
                            error_message: str = ''):
        """
        Update PDF document with extraction results.
        
        Args:
            status: Processing status
            tables_count: Number of tables detected
            entries_count: Number of entries extracted
            method: Extraction method used
            error_message: Error message if failed
        """
        self.pdf_document.processing_status = status
        self.pdf_document.is_processed = (status == 'completed')
        
        if status == 'completed':
            self.pdf_document.tables_detected = tables_count
            self.pdf_document.entries_extracted = entries_count
            self.pdf_document.extraction_method = method
            self.pdf_document.processed_at = timezone.now()
            
            # Calculate average confidence
            entries = TimetableEntry.objects.filter(pdf_document=self.pdf_document)
            if entries.exists():
                avg_confidence = sum(e.confidence_score for e in entries) / entries.count()
                self.pdf_document.average_confidence = avg_confidence
        
        if error_message:
            self.pdf_document.error_message = error_message
        
        self.pdf_document.save()