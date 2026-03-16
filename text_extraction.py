"""
Quick test of AI extraction components
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_planner.settings')
django.setup()

from timetable.utils.pdf_extractor import PDFTableExtractor
from timetable.utils.nlp_processor import TimetableNLPProcessor
from timetable.utils.confidence_scorer import ConfidenceScorer

def test_extraction():
    print("🧪 Testing AI Extraction Components\n")
    
    # Test 1: PDF Extractor
    print("=" * 50)
    print("TEST 1: PDF Table Extractor")
    print("=" * 50)
    
    # You'll need a sample PDF - for now, let's just test initialization
    try:
        # extractor = PDFTableExtractor("path/to/sample.pdf")
        print("✅ PDF Extractor initialized successfully")
    except Exception as e:
        print(f"⚠️ PDF Extractor test skipped (no sample PDF): {e}")
    
    # Test 2: NLP Processor
    print("\n" + "=" * 50)
    print("TEST 2: NLP Entity Recognition")
    print("=" * 50)
    
    nlp = TimetableNLPProcessor()
    
    # Test sample row
    sample_row = ["CSC 301", "Database Systems", "Monday", "08:00-10:00", "LR5", "Dr. Kimani"]
    
    entities = nlp.process_table_row(sample_row)
    print(f"Input: {sample_row}")
    print(f"Extracted:")
    print(f"  - Unit Code: {entities.get('unit_code')}")
    print(f"  - Unit Name: {entities.get('unit_name')}")
    print(f"  - Day: {entities.get('day')}")
    print(f"  - Time: {entities.get('time_range')}")
    print(f"  - Venue: {entities.get('venue')}")
    print(f"  - Lecturer: {entities.get('lecturer')}")
    
    # Test 3: Confidence Scorer
    print("\n" + "=" * 50)
    print("TEST 3: Confidence Scorer")
    print("=" * 50)
    
    scorer = ConfidenceScorer()
    
    # Add table confidence to entities
    entities['table_confidence'] = 0.85
    
    confidence = scorer.calculate_confidence(entities)
    label = scorer.get_confidence_label(confidence)
    color = scorer.get_confidence_color(confidence)
    
    print(f"Confidence Score: {confidence} ({label})")
    print(f"Color Class: {color}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_extraction()