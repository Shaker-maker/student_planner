#!/usr/bin/env python
"""
Specialized extractor for day × time grid timetables.
Handles timetables where days are rows, time slots are columns, and cells contain course info.
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import time

logger = logging.getLogger(__name__)


class GridTimetableExtractor:
    """
    Extract timetable data from day×time grid format tables.
    Rows = Days, Columns = Time slots, Cells = Courses
    """
    
    # Patterns for parsing cell content: "CODE NAME (LECTURER) VENUE"
    CELL_PATTERN = r'([A-Z]{2,4}\s+\d{3,4})\s*(.*?)\s*\(([^)]*)\)\s*([A-Z\d\-]+)?'
    TIME_PATTERN = r'(\d{1,2}):(\d{2})\s*[–-]\s*(\d{1,2}):(\d{2})'
    
    DAY_NAMES = {
        'monday': 'Monday', 'tuesday': 'Tuesday', 'wednesday': 'Wednesday',
        'thursday': 'Thursday', 'friday': 'Friday', 'saturday': 'Saturday', 'sunday': 'Sunday'
    }
    
    def __init__(self, lookup_table: Optional[Dict] = None):
        """
        Initialize extractor with optional lookup table for unit enrichment.
        
        Args:
            lookup_table: Dictionary mapping unit_code → {'unit_name': ..., 'lecturer': ...}
        """
        self.lookup_table = lookup_table or {}
    
    def extract_from_grid_table(self, table_data: List[List[str]], table_day: Optional[str] = None) -> List[Dict]:
        """
        Extract entries from a day×time grid timetable.
        
        Args:
            table_data: 2D list where rows=days, columns=time slots
            table_day: Optional day to apply to all entries (if table represents single day)
        
        Returns:
            List of extracted timetable entries
        """
        entries = []
        
        if len(table_data) < 5:  # Need header rows
            logger.warning("Grid table too small to extract from")
            return entries
        
        # Row 4 typically has the time slots
        time_header_row = table_data[4] if len(table_data) > 4 else None
        if not time_header_row:
            logger.warning("Could not find time header row")
            return entries
        
        # Extract time slots from header
        time_slots = self._extract_time_slots(time_header_row)
        if not time_slots:
            logger.warning("Could not extract time slots from header")
            return entries
        
        logger.info(f"Found {len(time_slots)} time slots: {time_slots}")
        
        # Process data rows (starting from row 5, which is the first Monday)
        for row_idx in range(5, len(table_data)):
            row = table_data[row_idx]
            if not any(row):  # Skip empty rows
                continue
            
            # Determine the day for this row
            if table_day:
                # Use the provided table_day (table represents single day, so all rows are same day)
                day = table_day
            else:
                # Extract day from column 0 of this row
                day_cell = str(row[0]).strip().lower() if row else ""
                day = None
                for day_name in self.DAY_NAMES.keys():
                    if day_name in day_cell:
                        day = day_name
                        break
                
                # If no day found in column 0, use Monday as fallback
                if not day:
                    logger.debug(f"Row {row_idx}: Could not extract day from '{day_cell}', defaulting to 'monday'")
                    day = 'monday'
            
            # Column 1 has the program/group (e.g., "BCT_Y1_S2")
            group = str(row[1]).strip() if len(row) > 1 else ""
            
            # Process columns, merging consecutive columns with the same course code
            col_idx = 2
            processed_cols = set()
            
            while col_idx < len(row):
                if col_idx in processed_cols or col_idx - 2 >= len(time_slots):
                    col_idx += 1
                    continue
                
                cell = str(row[col_idx]).strip() if row[col_idx] else ""
                if not cell:
                    col_idx += 1
                    continue
                
                # Extract course code from this cell
                current_code = self._extract_course_code(cell)
                if not current_code:
                    col_idx += 1
                    continue
                
                # Look ahead for consecutive columns with the same course code
                consecutive_cols = [col_idx]
                next_col = col_idx + 1
                
                while (next_col < len(row) and 
                       next_col - 2 < len(time_slots) and 
                       next_col not in processed_cols):
                    next_cell = str(row[next_col]).strip() if row[next_col] else ""
                    next_code = self._extract_course_code(next_cell)
                    
                    # Check if it's the same course
                    if next_code == current_code and next_cell:
                        consecutive_cols.append(next_col)
                        next_col += 1
                    else:
                        break
                
                # Merge consecutive columns into a single entry with combined time range
                if len(consecutive_cols) == 1:
                    # Single column - use as is
                    time_range = time_slots[col_idx - 2]
                    entry = self._parse_cell_content(cell, day, group, time_range)
                else:
                    # Multiple consecutive columns - merge into one entry
                    start_col_idx = consecutive_cols[0]
                    end_col_idx = consecutive_cols[-1]
                    
                    start_time_range = time_slots[start_col_idx - 2]
                    end_time_range = time_slots[end_col_idx - 2]
                    
                    # Merge time ranges: start time from first column, end time from last column
                    merged_time_range = {
                        'start_time': start_time_range['start_time'],
                        'end_time': end_time_range['end_time'],
                        # Calculate duration across all columns
                        'duration_minutes': sum(
                            time_slots[i - 2]['duration_minutes'] 
                            for i in consecutive_cols 
                            if i - 2 < len(time_slots)
                        )
                    }
                    
                    entry = self._parse_cell_content(cell, day, group, merged_time_range)
                    logger.debug(f"Merged {current_code} across {len(consecutive_cols)} columns: "
                               f"{merged_time_range['start_time']}-{merged_time_range['end_time']} "
                               f"({merged_time_range['duration_minutes']}min)")
                
                if entry:
                    entries.append(entry)
                
                # Mark all processed columns
                for c in consecutive_cols:
                    processed_cols.add(c)
                
                col_idx = max(consecutive_cols) + 1
        
        logger.info(f"Extracted {len(entries)} entries from grid table")
        return entries
    
    def _extract_time_slots(self, header_row: List[str]) -> List[Dict]:
        """Extract time slot information from header row."""
        time_slots = []
        
        for cell_idx, cell in enumerate(header_row[2:], start=2):  # Skip day/group columns
            if not cell:
                continue
            
            cell_str = str(cell).strip()
            time_match = re.search(self.TIME_PATTERN, cell_str)
            
            if time_match:
                start_hour = int(time_match.group(1))
                start_min = int(time_match.group(2))
                end_hour = int(time_match.group(3))
                end_min = int(time_match.group(4))
                
                start_time = time(hour=start_hour, minute=start_min)
                end_time = time(hour=end_hour, minute=end_min)
                
                # Calculate duration
                duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
                
                time_slots.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_minutes': duration_minutes
                })
        
        return time_slots
    
    def _extract_course_code(self, cell: str) -> Optional[str]:
        """
        Extract course code from a cell.
        Returns the course code (e.g., "BCT 2105") or None if not found.
        """
        if not cell:
            return None
        
        match = re.search(r'([A-Z]{2,4}\s+\d{3,4})', cell)
        if match:
            return match.group(1).strip()
        return None
    
    def _parse_cell_content(self, cell: str, day: Optional[str], 
                          group: str, time_range: Dict) -> Optional[Dict]:
        """
        Parse a cell containing course information.
        Format: "CODE NAME (LECTURER) VENUE"
        Example: "BCT 2105 (MANGO) EG-28" or "BIT 2123 () LAB A-06"
        """
        if not cell:
            return None
        
        # Try to match the pattern: CODE NAME (LECTURER) VENUE
        match = re.search(self.CELL_PATTERN, cell)
        
        if match:
            unit_code = match.group(1).strip()
            unit_name = match.group(2).strip() or unit_code  # Use code as name if name is empty
            lecturer = match.group(3).strip() or ""
            venue = match.group(4).strip() or ""
            
            # Enrich with lookup table if available
            if unit_code in self.lookup_table:
                lookup_data = self.lookup_table[unit_code]
                if lookup_data.get('unit_name'):
                    unit_name = lookup_data['unit_name']
                if lookup_data.get('lecturer') and not lecturer:  # Don't override if we have lecturer from PDF
                    lecturer = lookup_data['lecturer']
        else:
            # If pattern doesn't match, try simple extraction
            # Just assume the whole cell is unit code + venue
            parts = cell.rsplit(' ', 1)
            unit_code = parts[0].strip() if parts else cell
            venue = parts[1] if len(parts) > 1 else ""
            
            # Try to extract unit code
            code_match = re.search(r'([A-Z]{2,4}\s+\d{3,4})', unit_code)
            if code_match:
                unit_code = code_match.group(1)
                unit_name = unit_code
            else:
                logger.debug(f"Could not parse unit code from: {cell}")
                return None
            
            lecturer = ""
        
        # Enrich with lookup table if available
        entry = {
            'unit_code': unit_code,
            'unit_name': unit_name,
            'lecturer': lecturer,
            'venue': venue,
            'day': day or 'monday',
            'time_range': time_range,
            'group': group,
            'raw_text': cell,
            'confidence': 0.0
        }
        
        # Check lookup table for enriched unit name and lecturer
        if unit_code in self.lookup_table:
            lookup_data = self.lookup_table[unit_code]
            if lookup_data.get('unit_name'):
                entry['unit_name'] = lookup_data['unit_name']
                entry['unit_name_source'] = 'lookup_table'
            if lookup_data.get('lecturer') and not lecturer:  # Don't override if we have lecturer from PDF
                entry['lecturer'] = lookup_data['lecturer']
                entry['lecturer_source'] = 'lookup_table'
        
        return entry
