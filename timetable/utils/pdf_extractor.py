"""
PDF Table Extraction using Computer Vision
Uses Camelot-py for intelligent table detection
"""
import camelot
import tabula
import pdfplumber
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class PDFTableExtractor:
    """
    Intelligent PDF table extractor using multiple methods.
    Tries Camelot first, falls back to Tabula, then pdfplumber.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize extractor with PDF file path.
        
        Args:
            pdf_path: Full path to PDF file
        """
        self.pdf_path = pdf_path
        self.extraction_method = None
        self.tables = []
    
    def extract_tables(self) -> List[Dict]:
        """
        Main extraction method - tries multiple approaches.
        
        Returns:
            List of dictionaries containing table data and metadata
        """
        # Try Camelot (lattice method) first - best for bordered tables
        try:
            logger.info(f"Attempting Camelot lattice extraction: {self.pdf_path}")
            tables = self._extract_with_camelot_lattice()
            if tables and len(tables) > 0:
                self.extraction_method = 'camelot_lattice'
                self.tables = tables
                logger.info(f"✅ Camelot lattice found {len(tables)} tables")
                return tables
        except Exception as e:
            logger.warning(f"Camelot lattice failed: {str(e)}")
        
        # Try Camelot (stream method) - for borderless tables
        try:
            logger.info(f"Attempting Camelot stream extraction: {self.pdf_path}")
            tables = self._extract_with_camelot_stream()
            if tables and len(tables) > 0:
                self.extraction_method = 'camelot_stream'
                self.tables = tables
                logger.info(f"✅ Camelot stream found {len(tables)} tables")
                return tables
        except Exception as e:
            logger.warning(f"Camelot stream failed: {str(e)}")
        
        # Try Tabula as fallback
        try:
            logger.info(f"Attempting Tabula extraction: {self.pdf_path}")
            tables = self._extract_with_tabula()
            if tables and len(tables) > 0:
                self.extraction_method = 'tabula'
                self.tables = tables
                logger.info(f"✅ Tabula found {len(tables)} tables")
                return tables
        except Exception as e:
            logger.warning(f"Tabula failed: {str(e)}")
        
        # Try pdfplumber as last resort
        try:
            logger.info(f"Attempting pdfplumber extraction: {self.pdf_path}")
            tables = self._extract_with_pdfplumber()
            if tables and len(tables) > 0:
                self.extraction_method = 'pdfplumber'
                self.tables = tables
                logger.info(f"✅ PDFPlumber found {len(tables)} tables")
                return tables
        except Exception as e:
            logger.error(f"All extraction methods failed: {str(e)}")
        
        logger.error("❌ No tables could be extracted from PDF")
        return []
    
    def _extract_with_camelot_lattice(self) -> List[Dict]:
        """
        Extract tables using Camelot lattice method (for bordered tables).
        
        Returns:
            List of table dictionaries with data and confidence scores
        """
        # Camelot extracts tables from PDF
        tables = camelot.read_pdf(
            self.pdf_path,
            flavor='lattice',  # Use lattice for bordered tables
            pages='all'
        )
        
        result = []
        for i, table in enumerate(tables):
            # Get table as 2D list
            table_data = table.data
            
            # Camelot provides accuracy score (0-100)
            accuracy = table.parsing_report.get('accuracy', 0)
            
            result.append({
                'table_number': i + 1,
                'data': table_data,
                'rows': len(table_data),
                'columns': len(table_data[0]) if table_data else 0,
                'confidence': accuracy / 100,  # Convert to 0-1 scale
                'method': 'camelot_lattice',
                'page': table.page
            })
        
        return result
    
    def _extract_with_camelot_stream(self) -> List[Dict]:
        """
        Extract tables using Camelot stream method (for borderless tables).
        """
        tables = camelot.read_pdf(
            self.pdf_path,
            flavor='stream',  # Use stream for borderless tables
            pages='all'
        )
        
        result = []
        for i, table in enumerate(tables):
            table_data = table.data
            accuracy = table.parsing_report.get('accuracy', 0)
            
            result.append({
                'table_number': i + 1,
                'data': table_data,
                'rows': len(table_data),
                'columns': len(table_data[0]) if table_data else 0,
                'confidence': accuracy / 100,
                'method': 'camelot_stream',
                'page': table.page
            })
        
        return result
    
    def _extract_with_tabula(self) -> List[Dict]:
        """
        Extract tables using Tabula (Java-based extractor).
        """
        # Tabula returns list of DataFrames
        dfs = tabula.read_pdf(
            self.pdf_path,
            pages='all',
            multiple_tables=True,
            lattice=True  # Try lattice mode first
        )
        
        result = []
        for i, df in enumerate(dfs):
            # Convert DataFrame to 2D list
            table_data = [df.columns.tolist()] + df.values.tolist()
            
            result.append({
                'table_number': i + 1,
                'data': table_data,
                'rows': len(table_data),
                'columns': len(table_data[0]) if table_data else 0,
                'confidence': 0.7,  # Tabula doesn't provide confidence, use default
                'method': 'tabula',
                'page': i + 1  # Approximate page number
            })
        
        return result
    
    def _extract_with_pdfplumber(self) -> List[Dict]:
        """
        Extract tables using pdfplumber (last resort).
        """
        result = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract tables from page
                tables = page.extract_tables()
                
                for i, table in enumerate(tables):
                    if table:
                        result.append({
                            'table_number': len(result) + 1,
                            'data': table,
                            'rows': len(table),
                            'columns': len(table[0]) if table else 0,
                            'confidence': 0.6,  # Default confidence
                            'method': 'pdfplumber',
                            'page': page_num
                        })
        
        return result
    
    def filter_tables_by_year(self, tables: List[Dict], target_year: int) -> List[Dict]:
        """
        Filter tables to only include those relevant to target year.
        
        Args:
            tables: List of extracted tables
            target_year: Student's year of study (1-5)
        
        Returns:
            Filtered list of tables
        """
        # Year detection patterns
        year_patterns = [
            rf'\b[Yy]ear\s*{target_year}\b',
            rf'\b{target_year}(?:st|nd|rd|th)\s*[Yy]ear\b',
            rf'\b[Ll]evel\s*{target_year}\b',
            rf'\bY{target_year}\b',
            rf'\bYr\s*{target_year}\b',
        ]
        
        filtered_tables = []
        
        for table in tables:
            # Convert table to text for searching
            table_text = ' '.join([' '.join([str(cell) for cell in row]) for row in table['data']])
            
            # Check if any year pattern matches
            for pattern in year_patterns:
                if re.search(pattern, table_text, re.IGNORECASE):
                    filtered_tables.append(table)
                    logger.info(f"✅ Table {table['table_number']} matches Year {target_year}")
                    break
        
        if not filtered_tables:
            # No explicit year markers found - this is common if PDF doesn't have "Year 1", "Year 2" headers
            # Fall back to all tables and let downstream personalization filter by course+year at entry level
            logger.info(f"ℹ️ No explicit year markers found in tables (no 'Year {target_year}' headers)")
            logger.info(f"   → Using all {len(tables)} tables; course-level filtering will apply later")
            return tables
        
        return filtered_tables
    
    def get_extraction_stats(self) -> Dict:
        """
        Get statistics about the extraction process.
        
        Returns:
            Dictionary with extraction statistics
        """
        return {
            'method_used': self.extraction_method,
            'total_tables': len(self.tables),
            'tables_data': self.tables,
            'average_confidence': sum(t['confidence'] for t in self.tables) / len(self.tables) if self.tables else 0
        }