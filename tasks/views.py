from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Task, ReminderLog
from .forms import TaskForm, TaskFilterForm


@login_required(login_url='accounts:login')
def task_dashboard(request):
    """
    Dashboard view showing all tasks for the logged-in user,
    with filtering and sorting options
    """
    user = request.user
    tasks = Task.objects.filter(user=user)
    
    # Get filter parameters from the request
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('task_type', '')
    
    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if type_filter:
        tasks = tasks.filter(task_type=type_filter)
    
    # Separate tasks: upcoming and completed
    now = timezone.now()
    upcoming_tasks = tasks.filter(due_date__gte=now).order_by('due_date')
    completed_tasks = tasks.filter(due_date__lt=now).order_by('-due_date')
    
    # Get filter form
    filter_form = TaskFilterForm(request.GET if request.GET else None)
    
    context = {
        'upcoming_tasks': upcoming_tasks,
        'completed_tasks': completed_tasks,
        'all_tasks': tasks,
        'filter_form': filter_form,
        'task_count': {
            'pending': tasks.filter(status='pending').count(),
            'done': tasks.filter(status='done').count(),
            'not_submitted': tasks.filter(status='not_submitted').count(),
        }
    }
    
    return render(request, 'timetable/tasks_dashboard.html', context)


@login_required(login_url='accounts:login')
def add_task(request):
    """
    View to create a new task
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f"Task '{task.name}' created successfully! Daily reminders will start immediately.")
            return redirect('tasks:dashboard')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'timetable/add_task.html', context)


@login_required(login_url='accounts:login')
def edit_task(request, task_id):
    """
    View to edit an existing task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f"Task '{task.name}' updated successfully!")
            return redirect('tasks:dashboard')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'action': 'Edit',
    }
    return render(request, 'timetable/edit_task.html', context)


@login_required(login_url='accounts:login')
def delete_task(request, task_id):
    """
    View to delete a task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task_name = task.name
        task.delete()
        messages.success(request, f"Task '{task_name}' deleted successfully!")
        return redirect('tasks:dashboard')
    
    context = {
        'task': task,
    }
    return render(request, 'timetable/delete_task.html', context)


@login_required(login_url='accounts:login')
def task_detail(request, task_id):
    """
    View to display detailed information about a task
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    reminder_logs = ReminderLog.objects.filter(task=task).order_by('-sent_at')[:10]
    
    context = {
        'task': task,
        'days_left': task.get_days_left(),
        'reminder_message': task.get_reminder_message(),
        'is_overdue': task.is_overdue(),
        'reminder_logs': reminder_logs,
    }
    return render(request, 'timetable/task_detail.html', context)


@login_required(login_url='accounts:login')
def update_task_status(request, task_id):
    """
    Quick update for task status without opening the edit form
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'done', 'not_submitted']:
            task.status = new_status
            task.save()
            messages.success(request, f"Task status updated to {new_status}!")
    
    return redirect('tasks:dashboard')
