"""
NLP Entity Recognition for Timetable Data
Uses spaCy and regex patterns to extract structured information
"""
import spacy
import re
from typing import Dict, List, Optional
from datetime import time
import logging

logger = logging.getLogger(__name__)


class TimetableNLPProcessor:
    """
    Natural Language Processing for extracting entities from timetable text.
    Identifies: unit codes, unit names, lecturers, venues, times, days.
    """
    
    # Regex patterns for common entities
    # Supports both formats:
    # - Old: "BCT 2105" or "BCT2105" 
    # - New: "BCT_Y1_S2" or "BCT_Y1"
    UNIT_CODE_PATTERN = r'\b[A-Z]{2,4}(?:[\s_]*\d{3,4}|[\s_]*Y[1-5](?:[\s_]*S[1-2])?)\b'
    GROUP_PATTERN = r'\b[A-Z]{2,4}_Y[1-5]_S[1-2]\b'  # Matches: BCS_Y1_S2, BCT_Y2_S1, etc.
    TIME_PATTERN = r'(\d{1,2}):(\d{2})\s*(?:AM|PM|am|pm)?'
    VENUE_PATTERNS = [
        r'\bLR\s*\d+\b',           # LR5, LR 5
        r'\bLab\s*\d+\b',          # Lab 2, Lab2
        r'\bRoom\s*\d+\b',         # Room 101
        r'\bHall\s*[A-Z]?\b',      # Hall A
        r'\b[A-Z]\d{2,3}\b',       # A101, B23
    ]
    
    DAY_PATTERNS = {
        'monday': r'\b(?:Mon|Monday)\b',
        'tuesday': r'\b(?:Tue|Tuesday)\b',
        'wednesday': r'\b(?:Wed|Wednesday)\b',
        'thursday': r'\b(?:Thu|Thursday)\b',
        'friday': r'\b(?:Fri|Friday)\b',
        'saturday': r'\b(?:Sat|Saturday)\b',
        'sunday': r'\b(?:Sun|Sunday)\b',
    }
    
    def __init__(self):
        """Initialize NLP processor with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded successfully")
        except OSError:
            logger.error("❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            raise
    
    def process_table_row(self, row: List[str], row_index: int = 0) -> Dict:
        """
        Process a single table row to extract timetable entities.
        Handles both concatenated text and column-based extraction.
        
        Args:
            row: List of cell values from table row
            row_index: Row number (for debugging)
        
        Returns:
            Dictionary of extracted entities
        """
        # Combine row cells into text for entity extraction
        row_text = ' '.join([str(cell).strip() for cell in row if cell])
        
        # Extract entities from concatenated text
        # Try GROUP first (BCS_Y1_S2 format) - this takes precedence
        group = self.extract_group(row_text)
        
        unit_code = self.extract_unit_code(row_text)
        unit_name = self.extract_unit_name(row_text, row)
        
        # Fallback: if no unit name but we have unit code, use unit code as name
        if not unit_name and unit_code:
            unit_name = unit_code
        
        # Try to extract times from column-based structure first
        time_range = self.extract_time_range_from_columns(row) or self.extract_time_range(row_text)
        
        entities = {
            'group': group,  # GROUP column value (e.g., BCS_Y1_S2)
            'unit_code': unit_code,
            'unit_name': unit_name,
            'lecturer': self.extract_lecturer(row_text),
            'venue': self.extract_venue(row_text),
            'day': self.extract_day(row_text),
            'time_range': time_range,
            'raw_text': row_text,
            'confidence': 0.0  # Will be calculated later
        }
        
        logger.debug(f"Row {row_index}: Extracted {entities}")
        return entities
    
    def extract_time_range_from_columns(self, row: List[str]) -> Optional[Dict]:
        """
        Extract start and end times from separate columns in a table.
        Handles timetables where times are in distinct columns.
        
        Args:
            row: List of cell values from table row
        
        Returns:
            Dict with 'start_time', 'end_time', 'duration_minutes' or None
        """
        times = []
        
        # Find cells that contain time patterns (HH:MM format)
        for cell in row:
            if not cell:
                continue
            
            cell_str = str(cell).strip()
            match = re.search(self.TIME_PATTERN, cell_str, re.IGNORECASE)
            if match:
                parsed_time = self._parse_time(match)
                if parsed_time:
                    times.append(parsed_time)
        
        # If we found exactly 2 times, use them as start and end
        if len(times) >= 2:
            start_time = times[0]
            end_time = times[1]
            
            # Calculate duration in minutes
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            duration = end_minutes - start_minutes
            
            if duration < 0:  # Handle overnight (shouldn't happen for classes)
                duration += 24 * 60
            
            logger.debug(f"Extracted times from columns: {start_time} - {end_time} ({duration}min)")
            
            return {
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration
            }
        
        return None
    
    def extract_unit_code(self, text: str) -> Optional[str]:
        """
        Extract unit code (e.g., CSC 301, MAT201).
        
        Args:
            text: Text to search
        
        Returns:
            Unit code or None
        """
        match = re.search(self.UNIT_CODE_PATTERN, text, re.IGNORECASE)
        if match:
            code = match.group(0)
            # Normalize: add space if missing (CSC301 → CSC 301)
            if not ' ' in code and len(code) > 3:
                code = code[:3] + ' ' + code[3:]
            return code.upper()
        return None
    
    def extract_group(self, text: str) -> Optional[str]:
        """
        Extract GROUP identifier from timetable (e.g., BCS_Y1_S2, BCT_Y2_S1).
        
        GROUP identifies a specific cohort/program:
        - BCS = Bachelor of Science in Computer Science
        - Y1 = Year 1 (1-5)
        - S2 = Semester 2 (1-2)
        
        Args:
            text: Text to search
        
        Returns:
            GROUP code or None
        """
        match = re.search(self.GROUP_PATTERN, text, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return None
    
    def extract_unit_name(self, text: str, row: List[str]) -> Optional[str]:
        """
        Extract unit name using heuristics and NLP.
        
        Args:
            text: Full row text
            row: Individual cells (for column-based extraction)
        
        Returns:
            Unit name or None
        """
        # Try to find the longest text chunk (likely unit name)
        candidates = []
        
        # Method 1: Look for cells with multiple words
        for cell in row:
            cell_str = str(cell).strip()
            if cell_str and len(cell_str.split()) >= 2:
                # Exclude if it looks like lecturer (has title) or venue
                if not re.search(r'\b(?:Dr|Prof|Mr|Mrs|Ms|Miss)\.?\b', cell_str, re.IGNORECASE):
                    if not re.search(r'\b(?:LR|Lab|Room|Hall)\b', cell_str, re.IGNORECASE):
                        candidates.append(cell_str)
        
        # Method 2: Use spaCy to find noun phrases
        doc = self.nlp(text)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                candidates.append(chunk.text)
        
        # Return longest candidate
        if candidates:
            unit_name = max(candidates, key=len)
            # Clean up
            unit_name = re.sub(r'\s+', ' ', unit_name).strip()
            return unit_name
        
        return None
    
    def extract_lecturer(self, text: str) -> Optional[str]:
        """
        Extract lecturer name using spaCy NER and pattern matching.
        
        Args:
            text: Text to search
        
        Returns:
            Lecturer name or None
        """
        # Pattern 1: Look for titles
        title_pattern = r'\b(?:Dr|Prof|Mr|Mrs|Ms|Miss)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*'
        match = re.search(title_pattern, text)
        if match:
            return match.group(0).strip()
        
        # Pattern 2: Use spaCy NER to find PERSON entities
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
        
        return None
    
    def extract_venue(self, text: str) -> Optional[str]:
        """
        Extract venue/room using pattern matching.
        
        Args:
            text: Text to search
        
        Returns:
            Venue or None
        """
        for pattern in self.VENUE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def extract_day(self, text: str) -> Optional[str]:
        """
        Extract day of week.
        
        Args:
            text: Text to search
        
        Returns:
            Day in lowercase (e.g., 'monday') or None
        """
        for day, pattern in self.DAY_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return day
        
        return None
    
    def extract_time_range(self, text: str) -> Optional[Dict]:
        """
        Extract start and end times.
        
        Args:
            text: Text to search
        
        Returns:
            Dict with 'start_time', 'end_time', 'duration_minutes' or None
        """
        # Find all time patterns
        matches = list(re.finditer(self.TIME_PATTERN, text, re.IGNORECASE))
        
        if len(matches) >= 2:
            # First match is start time, second is end time
            start_match = matches[0]
            end_match = matches[1]
            
            start_time = self._parse_time(start_match)
            end_time = self._parse_time(end_match)
            
            if start_time and end_time:
                # Calculate duration
                start_minutes = start_time.hour * 60 + start_time.minute
                end_minutes = end_time.hour * 60 + end_time.minute
                duration = end_minutes - start_minutes
                
                if duration < 0:  # Handle overnight (shouldn't happen for classes)
                    duration += 24 * 60
                
                return {
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_minutes': duration
                }
        
        return None
    
    def _parse_time(self, match) -> Optional[time]:
        """
        Parse time from regex match.
        Handles various formats: 8:00, 08:00, 8:00 AM, 8:00 PM, etc.
        
        Args:
            match: Regex match object
        
        Returns:
            time object or None
        """
        try:
            hour = int(match.group(1))
            minute = int(match.group(2))
            
            # Validate hour and minute ranges
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                logger.warning(f"Invalid time values: hour={hour}, minute={minute}")
                return None
            
            # Handle AM/PM if present in the full matched string
            full_match = match.group(0).upper()
            
            # Check for PM designation
            if 'PM' in full_match and hour < 12 and hour >= 1:
                hour += 12
            # Check for AM designation
            elif 'AM' in full_match and hour == 12:
                hour = 0
            
            # For times without AM/PM in early morning (before 7 AM), assume it's actually PM
            # unless explicitly marked as AM (e.g., "02:00 PM" but written as "2:00" could be 2 PM)
            # However, if it's between 7-11, it's likely morning
            # If it's between 12-6 without AM/PM marker, it could be either - don't assume
            
            return time(hour=hour if hour < 24 else min(hour, 23), minute=minute)
        except (ValueError, AttributeError, IndexError) as e:
            logger.warning(f"Failed to parse time from match '{match.group(0) if match else 'None'}': {str(e)}")
            return None
    
    def batch_process_tables(self, tables: List[Dict]) -> List[Dict]:
        """
        Process multiple tables to extract all timetable entries.
        Automatically detects grid-based (day×time) vs. record-based (course list) tables.
        
        Args:
            tables: List of table dictionaries from PDF extractor
        
        Returns:
            List of processed entries with extracted entities
        """
        from .grid_extractor import GridTimetableExtractor
        
        all_entries = []
        total_rows = 0
        total_cells_processed = 0
        grid_extractor = GridTimetableExtractor()
        
        for table in tables:
            table_data = table['data']
            rows_count = len(table_data)
            columns_count = max(len(row) for row in table_data) if table_data else 0
            
            logger.info(f"📄 Processing table {table.get('table_number', '?')}: {rows_count} rows × {columns_count} cols")
            
            # Try to detect which day this table represents from its header
            table_day = self._detect_table_day(table_data, table.get('table_number', 0))
            if table_day:
                logger.info(f"  📅 Detected day from table header: {table_day}")
            
            # Try to detect if this is a grid-based timetable (days × time slots)
            is_grid_table = self._is_grid_timetable(table_data)
            
            if is_grid_table:
                logger.info(f"  🔲 Detected GRID FORMAT (day × time) - using specialized extractor")
                try:
                    grid_entries = grid_extractor.extract_from_grid_table(table_data, table_day)
                    if grid_entries:
                        for entry in grid_entries:
                            entry['table_number'] = table.get('table_number', 0)
                            entry['table_confidence'] = table.get('confidence', 0)
                            entry['extraction_method'] = 'grid_extractor'
                        all_entries.extend(grid_entries)
                        logger.info(f"  ✅ Extracted {len(grid_entries)} entries from grid table")
                except Exception as e:
                    logger.warning(f"  ⚠️ Grid extraction failed: {str(e)}, falling back to standard extraction")
                    # Fall through to standard extraction
            
            # Standard row-by-row processing (for course lists or if not grid format)
            if not is_grid_table:
                logger.info(f"  📋 Using standard ROW-BASED extraction")
                
                # Skip header row (index 0)
                for row_index, row in enumerate(table_data[1:], start=1):
                    total_rows += 1
                    total_cells_processed += len(row) if row else 0
                    
                    # Skip empty rows
                    if not any(row):
                        logger.debug(f"  Row {row_index}: Skipped (empty row)")
                        continue
                    
                    # Process row
                    entities = self.process_table_row(row, row_index)
                    
                    # Apply table day if detected
                    if table_day and not entities.get('day'):
                        entities['day'] = table_day
                    
                    # Keep entries if they have ANY meaningful data
                    has_meaningful_data = (
                        entities.get('unit_name') or 
                        entities.get('unit_code') or 
                        entities.get('lecturer') or 
                        entities.get('venue')
                    )
                    
                    if has_meaningful_data:
                        entities['table_number'] = table.get('table_number', 0)
                        entities['table_confidence'] = table.get('confidence', 0)
                        entities['extraction_method'] = table.get('method', 'unknown')
                        all_entries.append(entities)
                        
                        # Log with details
                        unit_display = entities.get('unit_name') or entities.get('unit_code') or 'Unknown'
                        day_display = entities.get('day', 'unknown day')
                        time_range = entities.get('time_range')
                        time_display = f"{time_range.get('start_time', '?')} - {time_range.get('end_time', '?')}" if time_range else "No time"
                        
                        logger.info(f"  ✅ Row {row_index}: {unit_display} | {day_display} | {time_display}")
                    else:
                        logger.debug(f"  ⚠ Row {row_index}: Skipped (no meaningful data found)")
                        logger.debug(f"     Raw: {entities.get('raw_text', '')[:100]}")
        
        logger.info(f"✅ Processed {total_rows} rows ({total_cells_processed} cells) from {len(tables)} tables")
        logger.info(f"✅ Extracted {len(all_entries)} timetable entries")
        
        if len(all_entries) == 0 and total_rows > 0:
            logger.warning("⚠️ ZERO entries extracted! Check:")
            logger.warning("   - Are unit codes/names present in the table?")
            logger.warning("   - Are times in correct format (e.g., 09:00)?")
            logger.warning("   - Is the table structure recognized?")
        
        return all_entries
    
    def _is_grid_timetable(self, table_data: List[List[str]]) -> bool:
        """
        Detect if a table is in day×time grid format.
        
        Characteristics:
        - Header row (usually row 4) contains time patterns (HH:MM – HH:MM)
        - Column 0 contains day names
        - Column 1 contains program/group names
        - Large number of columns (7+)
        
        Args:
            table_data: 2D table data
        
        Returns:
            True if detected as grid format, False otherwise
        """
        if len(table_data) < 5:
            return False
        
        # Check row 4 for time patterns
        if len(table_data) > 4:
            header_row = table_data[4]
            time_pattern = r'\d{1,2}:\d{2}\s*[–-]\s*\d{1,2}:\d{2}'
            time_count = sum(1 for cell in header_row if cell and re.search(time_pattern, str(cell)))
            
            # If we find 5+ time slots in the header, it's likely a grid table
            if time_count >= 5:
                logger.debug(f"  Detected {time_count} time slots in header - likely grid format")
                return True
        
        # Also check if column 0 of data rows contains day names
        day_pattern = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
        day_count = 0
        for row_idx in range(5, min(15, len(table_data))):  # Check first 10 data rows
            if table_data[row_idx] and str(table_data[row_idx][0]).lower():
                if re.search(day_pattern, str(table_data[row_idx][0]).lower()):
                    day_count += 1
        
        if day_count >= 2:
            logger.debug(f"  Found {day_count} rows with day names - likely grid format")
            return True
        
        return False
    
    def _detect_table_day(self, table_data: List[List[str]], table_number: int) -> Optional[str]:
        """
        Detect which day a table represents from its header information.
        
        Checks:
        1. Table header rows (0-3) for day names like "MONDAY", "TUESDAY", etc.
        2. Column 0 of first few data rows
        3. Fallback to table_number mapping for grid tables
        
        Args:
            table_data: 2D table data
            table_number: Table number (1-indexed)
        
        Returns:
            Day name (lowercase) or None
        """
        # Check header rows (rows 0-3)
        for row_idx in range(min(4, len(table_data))):
            row = table_data[row_idx]
            if not row:
                continue
            
            # Combine all cells in row into text
            row_text = ' '.join(str(cell).lower() for cell in row if cell)
            
            # Check for day names
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                if day in row_text:
                    logger.debug(f"  Found '{day}' in table header row {row_idx}")
                    return day
        
        # Check column 0 of first few data rows
        for row_idx in range(5, min(10, len(table_data))):
            if table_data[row_idx] and table_data[row_idx][0]:
                cell_text = str(table_data[row_idx][0]).lower()
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    if day in cell_text:
                        logger.debug(f"  Found '{day}' in row {row_idx}, col 0")
                        return day
        
        # Fallback to table ordering for grid tables (table 1=monday, table 2=tuesday, etc.)
        # Table numbers are 1-indexed, days start from Monday (1)
        days_mapping = {
            1: 'monday', 2: 'tuesday', 3: 'wednesday',
            4: 'thursday', 5: 'friday'
        }
        
        if table_number in days_mapping:
            logger.debug(f"  Using fallback mapping: table {table_number} -> {days_mapping[table_number]}")
            return days_mapping[table_number]
        
        return None