from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import PDFDocument, TimetableEntry
from .forms import PDFUploadForm, TimetableEntryForm
from .services import TimetableExtractionService
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """
    Main dashboard showing user's timetable.
    """
    user = request.user
    
    # Check if user has year_of_study set
    if not user.year_of_study:
        messages.warning(request, 'Please set your year of study in your profile before uploading timetables.')
        return redirect('accounts:edit_profile')
    
    # Get all timetable entries for user
    entries = TimetableEntry.objects.filter(user=user).order_by('day_of_week', 'start_time')
    
    # Organize by day
    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    timetable_by_day = {day: [] for day in days_order}
    
    for entry in entries:
        timetable_by_day[entry.day_of_week].append(entry)
    
    # Get recent PDFs
    recent_pdfs = PDFDocument.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Statistics
    stats = {
        'total_classes': entries.count(),
        'total_pdfs': PDFDocument.objects.filter(user=user).count(),
        'verified_entries': entries.filter(is_verified=True).count(),
        'pending_verification': entries.filter(is_verified=False).count(),
    }
    
    context = {
        'timetable_by_day': timetable_by_day,
        'days_order': days_order,
        'recent_pdfs': recent_pdfs,
        'stats': stats,
    }
    
    return render(request, 'timetable/dashboard.html', context)


@login_required
def upload_pdf_view(request):
    """
    Handle PDF upload and trigger extraction.
    """
    # Check if user has year_of_study
    if not request.user.year_of_study:
        messages.error(request, 'Please set your year of study in your profile before uploading timetables.')
        return redirect('accounts:edit_profile')
    
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save PDF document
            pdf_doc = form.save(commit=False)
            pdf_doc.user = request.user
            pdf_doc.original_filename = request.FILES['file'].name
            pdf_doc.file_size = request.FILES['file'].size
            pdf_doc.save()
            
            # Start extraction process
            try:
                logger.info(f"Starting extraction for PDF: {pdf_doc.original_filename}")
                service = TimetableExtractionService(pdf_doc)
                entries_count = service.extract()
                
                messages.success(
                    request,
                    f'🎉 Success! Extracted {entries_count} classes from your timetable. '
                    f'Please review and verify the entries below.'
                )
                return redirect('timetable:dashboard')
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"PDF processing failed: {error_msg}")
                messages.error(
                    request,
                    f'❌ Failed to process PDF: {error_msg}. '
                    f'You can try again or add classes manually.'
                )
                return redirect('timetable:upload_pdf')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PDFUploadForm()
    
    return render(request, 'timetable/upload_pdf.html', {'form': form})


@login_required
def add_entry_view(request):
    """
    Manually add a timetable entry.
    """
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.year_of_study = request.user.year_of_study
            entry.is_manually_added = True
            entry.is_verified = True  # Manually added entries are pre-verified
            entry.confidence_score = 1.0  # Manual entries have 100% confidence
            entry.save()
            
            messages.success(request, f'✅ {entry.unit_name} added to your timetable!')
            return redirect('timetable:dashboard')
    else:
        form = TimetableEntryForm()
    
    return render(request, 'timetable/add_entry.html', {'form': form})


@login_required
def edit_entry_view(request, entry_id):
    """
    Edit an existing timetable entry.
    """
    entry = get_object_or_404(TimetableEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST, instance=entry)
        if form.is_valid():
            # Store original data for ML training
            if not entry.is_manually_added:
                original_data = {
                    'unit_code': entry.unit_code,
                    'unit_name': entry.unit_name,
                    'venue': entry.venue,
                    'lecturer': entry.lecturer,
                }
                entry.user_corrections = original_data
            
            form.save()
            # Mark as verified when user edits/corrects it
            entry.is_verified = True
            entry.save()
            messages.success(request, f'✅ {entry.unit_name} updated successfully!')
            return redirect('timetable:dashboard')
    else:
        form = TimetableEntryForm(instance=entry)
    
    return render(request, 'timetable/edit_entry.html', {'form': form, 'entry': entry})


@login_required
def delete_entry_view(request, entry_id):
    """
    Delete a timetable entry.
    """
    entry = get_object_or_404(TimetableEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        unit_name = entry.unit_name
        entry.delete()
        messages.success(request, f'🗑️ {unit_name} removed from your timetable.')
        return redirect('timetable:dashboard')
    
    return render(request, 'timetable/delete_entry.html', {'entry': entry})


@login_required
def verify_entry_view(request, entry_id):
    """
    Mark an entry as verified.
    """
    entry = get_object_or_404(TimetableEntry, id=entry_id, user=request.user)
    entry.is_verified = True
    entry.save()
    
    messages.success(request, f'✅ {entry.unit_name} marked as verified!')
    return redirect('timetable:dashboard')


@login_required
def pdf_list_view(request):
    """
    List all uploaded PDFs.
    """
    pdfs = PDFDocument.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'pdfs': pdfs,
    }
    
    return render(request, 'timetable/pdf_list.html', context)


@login_required
def pdf_detail_view(request, pdf_id):
    """
    View details of a specific PDF and its extracted entries.
    """
    pdf = get_object_or_404(PDFDocument, id=pdf_id, user=request.user)
    entries = TimetableEntry.objects.filter(pdf_document=pdf).order_by('day_of_week', 'start_time')
    
    context = {
        'pdf': pdf,
        'entries': entries,
    }
    
    return render(request, 'timetable/pdf_detail.html', context)


@login_required
def delete_pdf_view(request, pdf_id):
    """
    Delete a PDF document and its associated entries.
    """
    pdf = get_object_or_404(PDFDocument, id=pdf_id, user=request.user)
    
    if request.method == 'POST':
        filename = pdf.original_filename
        # Delete associated entries
        TimetableEntry.objects.filter(pdf_document=pdf).delete()
        # Delete the PDF
        pdf.delete()
        messages.success(request, f'🗑️ PDF "{filename}" and its entries have been deleted.')
        return redirect('timetable:pdf_list')
    
    return render(request, 'timetable/delete_pdf.html', {'pdf': pdf})