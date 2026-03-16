"""
Confidence Scoring for Extracted Timetable Entries
Calculates how confident we are that extraction is correct
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """
    Calculates confidence scores for extracted timetable entries.
    Combines multiple factors: table quality, entity recognition, patterns.
    """
    
    # Weights for different confidence factors
    WEIGHTS = {
        'table_confidence': 0.3,      # 30% - CV table detection quality
        'entity_completeness': 0.3,   # 30% - How many required fields extracted
        'pattern_matching': 0.2,      # 20% - Do extracted values match expected patterns
        'data_quality': 0.2,          # 20% - Overall data quality indicators
    }
    
    REQUIRED_FIELDS = ['unit_name', 'day', 'time_range']
    OPTIONAL_FIELDS = ['unit_code', 'lecturer', 'venue']
    
    def calculate_confidence(self, entry: Dict) -> float:
        """
        Calculate overall confidence score (0-1) for an entry.
        
        Args:
            entry: Dictionary with extracted entities
        
        Returns:
            Confidence score between 0 and 1
        """
        scores = {
            'table_confidence': self._table_confidence_score(entry),
            'entity_completeness': self._entity_completeness_score(entry),
            'pattern_matching': self._pattern_matching_score(entry),
            'data_quality': self._data_quality_score(entry),
        }
        
        # Weighted average
        total_score = sum(scores[key] * self.WEIGHTS[key] for key in scores)
        
        # Round to 2 decimal places
        confidence = round(total_score, 2)
        
        logger.debug(f"Confidence breakdown: {scores} → {confidence}")
        return confidence
    
    def _table_confidence_score(self, entry: Dict) -> float:
        """
        Score based on table extraction quality from CV.
        """
        return entry.get('table_confidence', 0.5)
    
    def _entity_completeness_score(self, entry: Dict) -> float:
        """
        Score based on how many required/optional fields were extracted.
        """
        # Check required fields
        required_count = sum(1 for field in self.REQUIRED_FIELDS if entry.get(field))
        required_score = required_count / len(self.REQUIRED_FIELDS)
        
        # Check optional fields (bonus)
        optional_count = sum(1 for field in self.OPTIONAL_FIELDS if entry.get(field))
        optional_score = optional_count / len(self.OPTIONAL_FIELDS)
        
        # 70% weight on required, 30% on optional
        return (required_score * 0.7) + (optional_score * 0.3)
    
    def _pattern_matching_score(self, entry: Dict) -> float:
        """
        Score based on whether extracted values match expected patterns.
        """
        score = 0.0
        checks = 0
        
        # Check unit code format
        if entry.get('unit_code'):
            checks += 1
            unit_code = entry['unit_code']
            # Should be like "CSC 301" or "MAT 201"
            if len(unit_code) >= 6 and ' ' in unit_code:
                score += 1.0
            elif len(unit_code) >= 5:
                score += 0.5
        
        # Check time range validity
        if entry.get('time_range'):
            checks += 1
            time_range = entry['time_range']
            duration = time_range.get('duration_minutes', 0)
            # Classes typically 1-4 hours (60-240 minutes)
            if 60 <= duration <= 240:
                score += 1.0
            elif 30 <= duration <= 300:
                score += 0.5
        
        # Check venue format
        if entry.get('venue'):
            checks += 1
            venue = entry['venue']
            # Should be short (< 20 chars)
            if len(venue) < 20:
                score += 1.0
        
        # Check day validity
        if entry.get('day'):
            checks += 1
            score += 1.0  # If day was extracted, it's valid
        
        return score / checks if checks > 0 else 0.5
    
    def _data_quality_score(self, entry: Dict) -> float:
        """
        Score based on overall data quality indicators.
        """
        score = 0.0
        
        # Check for suspicious patterns
        raw_text = entry.get('raw_text', '')
        
        # Penalty for very short text (likely extraction error)
        if len(raw_text) < 10:
            score += 0.0
        else:
            score += 0.5
        
        # Bonus for having lecturer (indicates complete row)
        if entry.get('lecturer'):
            score += 0.3
        
        # Bonus for having unit code (well-structured timetable)
        if entry.get('unit_code'):
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_confidence_label(self, confidence: float) -> str:
        """
        Get human-readable confidence label.
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Label like "High", "Medium", "Low"
        """
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.75:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        elif confidence >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def get_confidence_color(self, confidence: float) -> str:
        """
        Get Tailwind CSS color class for confidence.
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Tailwind color class
        """
        if confidence >= 0.9:
            return "text-green-600"
        elif confidence >= 0.75:
            return "text-green-500"
        elif confidence >= 0.6:
            return "text-yellow-500"
        elif confidence >= 0.4:
            return "text-orange-500"
        else:
            return "text-red-500"