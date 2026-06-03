from django import forms
from django.utils import timezone
from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks
    """
    class Meta:
        model = Task
        fields = ['name', 'unit_name', 'task_type', 'description', 'due_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., Assignment 1',
            }),
            'unit_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., Database Systems',
            }),
            'task_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none',
                'rows': 4,
                'placeholder': 'Optional description...',
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
        }
        labels = {
            'name': 'Task Name',
            'unit_name': 'Unit Name',
            'task_type': 'Task Type',
            'description': 'Description (Optional)',
            'due_date': 'Due Date',
            'status': 'Status',
        }

    def clean_due_date(self):
        """Validate that due date is in the future"""
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            # Allow editing of past tasks, but warn on creation
            if not self.instance.pk:  # New task
                raise forms.ValidationError("Due date cannot be in the past.")
        return due_date


class TaskFilterForm(forms.Form):
    """
    Form for filtering tasks
    """
    STATUS_FILTER_CHOICES = [
        ('', 'All Statuses'),
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('not_submitted', 'Not Submitted'),
    ]
    
    TYPE_FILTER_CHOICES = [
        ('', 'All Types'),
        ('assignment', 'Assignments'),
        ('cat', 'CATs'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        })
    )
    task_type = forms.ChoiceField(
        choices=TYPE_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        })
    )
