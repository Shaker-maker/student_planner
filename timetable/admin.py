from django.contrib import admin
from .models import PDFDocument, TimetableEntry, ExtractionLog, MLTrainingData, UnitCatalog

# Register your models here.

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'extraction_method', 'processing_status','tables_detected', 'entries_extracted', 'average_confidence', 'created_at']
    list_filter  = ['timetable_type', 'processing_status', 'extraction_method']
    search_fields = ['original_filename', 'user__email', 'user__first_name']
    readonly_fields = ['id','updated_at', 'processing_time_seconds']


    fieldsets = (
        ('File Information', {
            'fields' : ('user', 'file', 'original_filename', 'file_size')
        }),
        ('Timetable Details', {
            'fields' : ('timetable_type', 'academic_year', 'semester')
        }),
        ('AI Processing', {
            'fields': ('extraction_method', 'processing_status', 'error_message', 'tables_detected', 'entries_extracted', 'average_confidence', 'processing_time_seconds')
        }),
        ('Timestamps', {
            'fields' : ('created_at', 'updated_at', 'processed_at')
        }),
        
    )


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['unit_name', 'user', 'day_of_week', 'start_time', 'end_time', 'confidence_score', 'is_verified', 'extraction_method']
    list_filter = ['day_of_week', 'is_verified', 'is_manually_added', 'year_of_study', 'created_at']
    search_fields = ['unit_name', 'unit_code', 'lecturer', 'venue', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'confidence_score', 'extracted_entities']

    fieldsets = (
        ('User & Source', {
            'fields': ('user', 'pdf_document', 'year_of_study')
        }),
        ('Class Details', {
            'fields': ('unit_code', 'unit_name', 'class_type', 'lecturer', 'venue')
        }),
        ('Timing', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('AI Metadata', {
            'fields': ('confidence_score', 'extraction_method', 'is_manually_added', 
                      'is_verified', 'extracted_entities', 'user_corrections')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    

@admin.register(UnitCatalog)
class UnitCatalogAdmin(admin.ModelAdmin):
    list_display = ['unit_code', 'unit_name', 'department', 'credits', 'is_active']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['unit_code', 'unit_name', 'department']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Unit Information', {
            'fields': ('unit_code', 'unit_name', 'department', 'credits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    

@admin.register(ExtractionLog)
class ExtractionLogAdmin(admin.ModelAdmin):
    list_display = ['pdf_document', 'extraction_method', 'success', 'entries_found', 
                    'processing_time', 'created_at']
    list_filter = ['success', 'extraction_method', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['pdf_document__original_filename']


@admin.register(MLTrainingData)
class MLTrainingDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'timetable_entry', 'used_for_training', 'created_at']
    list_filter = ['used_for_training', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['user__email', 'timetable_entry__unit_name']   
    
