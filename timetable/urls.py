from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # PDF Management
    path('upload/', views.upload_pdf_view, name='upload_pdf'),
    path('pdfs/', views.pdf_list_view, name='pdf_list'),
    path('pdfs/<uuid:pdf_id>/', views.pdf_detail_view, name='pdf_detail'),
    path('pdfs/<uuid:pdf_id>/delete/', views.delete_pdf_view, name='delete_pdf'),
    
    # Entry Management
    path('add/', views.add_entry_view, name='add_entry'),
    path('edit/<uuid:entry_id>/', views.edit_entry_view, name='edit_entry'),
    path('delete/<uuid:entry_id>/', views.delete_entry_view, name='delete_entry'),
    path('verify/<uuid:entry_id>/', views.verify_entry_view, name='verify_entry'),
]