from django import forms
from .models import PDFDocument, TimetableEntry


class PDFUploadForm(forms.ModelForm):
    """
    Form for uploading timetable PDFs.
    """
    class Meta:
        model = PDFDocument
        fields = ['file', 'timetable_type', 'academic_year', 'semester']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': '.pdf',
                'id': 'pdf-upload'
            }),
            'timetable_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '2024/2025'
            }),
            'semester': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Semester 1'
            }),
        }
    
    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data.get('file')
        
        if file:
            # Check file extension
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
        
        return file


class TimetableEntryForm(forms.ModelForm):
    """
    Form for manually adding or editing timetable entries.
    """
    class Meta:
        model = TimetableEntry
        fields = [
            'unit_code', 'unit_name', 'venue', 'lecturer',
            'day_of_week', 'start_time', 'end_time', 'class_type'
        ]
        widgets = {
            'unit_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'CSC 301'
            }),
            'unit_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Database Systems'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'LR5'
            }),
            'lecturer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Dr. Kimani'
            }),
            'day_of_week': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'class_type': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Lecture, Lab, Tutorial'
            }),
        }
    
    def clean(self):
        """Validate that end_time is after start_time."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError('End time must be after start time.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Calculate duration before saving."""
        instance = super().save(commit=False)
        
        # Calculate duration
        if instance.start_time and instance.end_time:
            start_minutes = instance.start_time.hour * 60 + instance.start_time.minute
            end_minutes = instance.end_time.hour * 60 + instance.end_time.minute
            instance.duration_minutes = end_minutes - start_minutes
        
        if commit:
            instance.save()
        
        return instance