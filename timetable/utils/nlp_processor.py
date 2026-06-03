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
    
    def __init__(self, lookup_table: Optional[Dict] = None):
        """
        Initialize NLP processor with spaCy model.
        
        Args:
            lookup_table: Optional dictionary for unit code → name enrichment
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded successfully")
        except OSError:
            logger.error("❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            raise
        
        self.lookup_table = lookup_table or {}
    
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
        
        # Try positional/column-based extraction first for structured tables
        unit_code, unit_name = self._extract_unit_code_and_name_from_columns(row)
        
        # Fallback to text parsing if column-based didn't work
        if not unit_code:
            unit_code = self.extract_unit_code(row_text)
        
        if not unit_name and unit_code:
            # Try to extract unit name from text between unit code and (lecturer)
            unit_name = self._extract_unit_name_from_text(row_text, unit_code)
        
        # If still no unit name, try NLP
        if not unit_name:
            unit_name = self.extract_unit_name(row_text, row)
        
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
    
    def _extract_unit_name_from_text(self, text: str, unit_code: str) -> Optional[str]:
        """
        Extract unit name from text between unit code and lecturer name (in parentheses).
        
        Handles format: "CCS 2424 [UnitName] (Lecturer) Venue"
        
        Example:
        - "CCS 2400 PROJECT ( ) LAB A-06" → "PROJECT"
        - "CCS 2424 (MOKODIR) A-03" → None (no unit name, just lecturer)
        
        Args:
            text: Full text containing unit code, unit name, lecturer
            unit_code: The extracted unit code (e.g., "CCS 2424")
        
        Returns:
            Unit name or None
        """
        if not text or not unit_code:
            return None
        
        # Find where the unit code appears in the text
        # Use case-insensitive search
        import re as regex_module
        unit_code_match = regex_module.search(regex_module.escape(unit_code), text, regex_module.IGNORECASE)
        
        if not unit_code_match:
            return None
        
        # Get text AFTER the unit code
        after_code = text[unit_code_match.end():]
        
        # Look for text between unit code and opening parenthesis (lecturer)
        # Format: "UnitName (Lecturer)"
        paren_match = regex_module.search(r'\(', after_code)
        
        if not paren_match:
            # No lecturer in parentheses, maybe the rest is the unit name
            # But only if it's not just venue
            remainder = after_code.strip()
            if remainder and not regex_module.search(r'^[A-Z]-\d|^LR\s*\d|^Lab', remainder):
                return remainder
            return None
        
        # Extract text between unit code and opening parenthesis
        before_paren = after_code[:paren_match.start()].strip()
        
        # Filter out common venue patterns
        if before_paren:
            # Skip if it looks like a venue (LR5, Lab 2, A-03, etc.)
            if regex_module.search(r'^(?:LR|Lab|Room|Hall|[A-Z]-\d|[A-Z]\d{2,3})\b', before_paren, regex_module.IGNORECASE):
                return None
            
            # This looks like a unit name
            logger.debug(f"Extracted unit name from text: '{before_paren}' from '{text}'")
            return before_paren
        
        return None
    
    def _extract_unit_code_and_name_from_columns(self, row: List[str]) -> tuple:
        """
        Extract unit code and unit name from column-based structure.
        
        Intelligently identifies which cell is the unit name by:
        1. Finding the unit code cell
        2. Looking at adjacent cells to find actual course names (multi-word entries)
        3. Filtering out lecturer names, times, venues
        
        Args:
            row: List of cell values from table row
        
        Returns:
            Tuple of (unit_code, unit_name) or (None, None) if not found
        """
        if not row or len(row) < 2:
            return None, None
        
        unit_code = None
        unit_name = None
        
        # Step 1: Find the unit code in the row
        code_cell_index = None
        for i, cell in enumerate(row):
            if not cell:
                continue
            cell_str = str(cell).strip()
            # Check if this cell matches unit code pattern (e.g., "CCS 2424", "BCT_Y1_S2")
            match = re.search(self.UNIT_CODE_PATTERN, cell_str)
            if match:
                unit_code = match.group(0)
                code_cell_index = i
                logger.debug(f"Found unit code at index {i}: {unit_code}")
                break
        
        # Step 2: If we found a unit code, search for the unit name in nearby cells
        if code_cell_index is not None:
            # Search in the next 2-3 cells after the unit code
            for offset in range(1, 4):
                check_index = code_cell_index + offset
                if check_index >= len(row):
                    break
                
                cell_str = str(row[check_index]).strip()
                if not cell_str or len(cell_str) < 3:
                    # Skip empty or very short cells
                    continue
                
                # Check if this looks like a unit name (not a code, time, venue, or lecturer)
                # Unit names are typically multi-word descriptive phrases
                is_unit_code = bool(re.search(self.UNIT_CODE_PATTERN, cell_str))
                is_lecturer = bool(re.search(r'\b(?:Dr|Prof|Mr|Mrs|Ms|Miss)\.?\b', cell_str, re.IGNORECASE))
                is_time = bool(re.search(r'\d{1,2}:\d{2}', cell_str))
                is_venue = bool(re.search(r'\b(?:LR|Lab|Room|Hall|A|B|C|D)\s*\d+\b', cell_str))
                
                # Accept this cell as unit name if it doesn't look like other entities
                if not any([is_unit_code, is_lecturer, is_time, is_venue]):
                    unit_name = cell_str
                    logger.debug(f"Found unit name at index {check_index}: {unit_name}")
                    break
        
        # Step 3: Also check BEFORE the unit code (in case structure is different)
        if not unit_name and code_cell_index is not None and code_cell_index > 0:
            # Check the cell before the unit code
            prev_cell = str(row[code_cell_index - 1]).strip()
            if prev_cell and len(prev_cell) > 3:
                is_unit_code = bool(re.search(self.UNIT_CODE_PATTERN, prev_cell))
                is_lecturer = bool(re.search(r'\b(?:Dr|Prof|Mr|Mrs|Ms|Miss)\.?\b', prev_cell, re.IGNORECASE))
                is_time = bool(re.search(r'\d{1,2}:\d{2}', prev_cell))
                
                if not any([is_unit_code, is_lecturer, is_time]):
                    unit_name = prev_cell
                    logger.debug(f"Found unit name before code at index {code_cell_index-1}: {unit_name}")
        
        return unit_code, unit_name
    
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
        Extract unit name using intelligent heuristics and NLP.
        
        Prioritizes substantial text (multi-word phrases) that look like course names.
        
        Args:
            text: Full row text
            row: Individual cells (for column-based extraction)
        
        Returns:
            Unit name or None
        """
        candidates = []
        
        # Method 1: Find cells with substantial text that aren't other entities
        for idx, cell in enumerate(row):
            cell_str = str(cell).strip()
            
            # Skip short cells, empty cells
            if not cell_str or len(cell_str) < 4:
                continue
            
            # Skip if it's clearly not a unit name
            if (re.search(self.UNIT_CODE_PATTERN, cell_str) or
                re.search(r'\b(?:Dr|Prof|Mr|Mrs|Ms|Miss)\.?\b', cell_str, re.IGNORECASE) or
                re.search(r'\d{1,2}:\d{2}', cell_str) or
                re.search(r'\b(?:LR|Lab|Room|Hall|A|B|C|D)\s*\d+\b', cell_str)):
                continue
            
            # This looks like it could be a unit name
            candidates.append((idx, cell_str, len(cell_str.split())))  # Index, text, word count
        
        # Filter to prefer longer, multi-word candidates (typical unit names)
        multi_word_candidates = [c for c in candidates if c[2] >= 2]
        
        if multi_word_candidates:
            # Pick the longest multi-word candidate
            unit_name = max(multi_word_candidates, key=lambda x: x[1])[1]
            logger.debug(f"Found unit name via cell extraction: {unit_name}")
            return unit_name
        
        # Fallback to single candidates if no multi-word options
        if candidates:
            unit_name = max(candidates, key=lambda x: len(x[1]))[1]
            logger.debug(f"Found unit name via single-word cell: {unit_name}")
            return unit_name
        
        # Method 2: Use spaCy NER as last resort
        doc = self.nlp(text)
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            # Skip unit codes
            if chunk_text and not re.search(self.UNIT_CODE_PATTERN, chunk_text):
                if len(chunk_text) > 4:  # Minimum length
                    logger.debug(f"Found unit name via NLP: {chunk_text}")
                    return chunk_text
        
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
        grid_extractor = GridTimetableExtractor(lookup_table=self.lookup_table)
        
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