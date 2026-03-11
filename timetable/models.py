from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# Create your models here.
class PDFDocument(models.Model):
    """
    Stores uploaded timetable PDFs with AI processing metadata
    """
    TIMETABLE_TYPE_CHOICES = [
        ('classes', 'Regular Classes'),
        ('exams', 'Exams')

    ]

    PROCESSING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed")

    ]

    EXTRACTION_METHOD_CHOICES = [
        ("camelot_lattice", "Camelot(Lattice)"),
        ("camelot_stream", "Camelot(Stream)"),
        ("tabula", "Tabula"),
        ("pdfplumber", "PDFPlumber"),
        ("ocr", "OCR (Tesseract)")

    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timetable_pdfs')

    #file info
    file = models.FileField(upload_to='timetables/%Y/%m')
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")

    #Metadata
    timetable_type = models.CharField(max_length=10, choices = TIMETABLE_TYPE_CHOICES, default="classes")
    academic_year = models.CharField(max_length=20, blank=True, help_text="e.g., 2025/2026")
    semester = models.CharField(max_length=50, blank=True, help_text="e.g., Semester 1")

    #AI Processing info
    extraction_method = models.CharField(max_length=20, choices=EXTRACTION_METHOD_CHOICES, default='camelot_lattice')
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending')
    is_processed = models.BooleanField(default=False)
    error_message =models.TextField(blank=True)

    #AI Metrics
    tables_detected = models.IntegerField(default=0,help_text="Number of tables found by cv")
    entries_extracted = models.IntegerField(default=0)
    average_confidence = models.FloatField(default=0.0, help_text="Average  confidence score (0-1)")
    processing_time_seconds = models.FloatField(default=0.0)


    #Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        #ordering = ['-uploaded_at']
        verbose_name = 'PDF Document'
        verbose_name_plural = 'PDF Documents'
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.get_full_name()}"
    
    def get_file_size_display(self):
        """Returns human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

   

class TimetableEntry(models.Model):
    """
    Individual timetable entries with AI confidence scores.
    """
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday') 
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timetable_entries')
    pdf_document = models.ForeignKey(PDFDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    
    # Extracted data
    unit_code = models.CharField(max_length=20, blank=True, help_text="e.g., CSC 301")
    unit_name = models.CharField(max_length=200, help_text="e.g., Database Systems")
    venue = models.CharField(max_length=100, help_text="e.g., LR5, Lab 2")
    lecturer = models.CharField(max_length=200, blank=True)
    
    # Timing
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField(help_text="e.g., 08:00")
    end_time = models.TimeField(help_text="e.g., 10:00")
    duration_hours = models.IntegerField(help_text="Duration in hours")
    
    # Additional info
    class_type = models.CharField(max_length=50, blank=True, help_text="e.g., Lecture, Lab, Tutorial")
    year_of_study = models.IntegerField(help_text="Academic year this entry belongs to")
    
    # AI Metadata
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence (0-1)")
    extraction_method = models.CharField(max_length=50, blank=True)
    is_manually_added = models.BooleanField(default=False, help_text="True if added manually")
    is_verified = models.BooleanField(default=False, help_text="User confirmed accuracy")
    
    # NLP extracted entities (JSON for debugging)
    extracted_entities = models.JSONField(default=dict, blank=True)
    
    # User feedback for ML
    user_corrections = models.JSONField(default=dict, blank=True, help_text="What user changed")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Timetable Entry'
        verbose_name_plural = 'Timetable Entries'
        unique_together = ['user', 'day_of_week', 'start_time', 'unit_code']
    
    def __str__(self):
        return f"{self.unit_name} - {self.get_day_of_week_display()} {self.start_time}"
    
    def get_time_range(self):
        """Returns formatted time range (e.g., '08:00 - 10:00')."""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    def get_duration_display(self):
        """Returns human-readable duration."""
        hours = self.duration_hours
        minutes = 0
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def get_confidence_display(self):
        """Returns confidence as percentage."""
        return f"{self.confidence_score * 100:.1f}%"
    
    def get_confidence_color(self):
        """Returns Tailwind color class based on confidence."""
        if self.confidence_score >= 0.9:
            return "text-green-600"
        elif self.confidence_score >= 0.7:
            return "text-yellow-600"
        else:
            return "text-red-600"


class ExtractionLog(models.Model):
    """
    Detailed logs of AI extraction for debugging and improvement.
    """
    pdf_document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='extraction_logs')
    
    # Extraction details
    extraction_method = models.CharField(max_length=50)
    raw_text = models.TextField(blank=True, help_text="Raw extracted text")
    detected_tables = models.JSONField(default=list, help_text="Tables found by CV")
    parsed_entities = models.JSONField(default=dict, help_text="NLP entities")
    
    # AI Metrics
    success = models.BooleanField(default=False)
    confidence_scores = models.JSONField(default=list)
    entries_found = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0)
    error_details = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Log: {self.pdf_document.original_filename} - {self.extraction_method}"


class MLTrainingData(models.Model):
    """
    Stores user corrections for ML model training.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE)
    
    # Original AI extraction
    original_extraction = models.JSONField(help_text="What AI extracted")
    
    # User's correction
    user_correction = models.JSONField(help_text="What user changed it to")
    
    # Feature vectors for ML
    features = models.JSONField(default=dict, help_text="Features for training")
    
    # Usage tracking
    used_for_training = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Training: {self.user.email} - {self.timetable_entry.unit_name}"

    