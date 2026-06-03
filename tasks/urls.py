from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_dashboard, name='dashboard'),
    path('add/', views.add_task, name='add_task'),
    path('<uuid:task_id>/', views.task_detail, name='detail'),
    path('<uuid:task_id>/edit/', views.edit_task, name='edit_task'),
    path('<uuid:task_id>/delete/', views.delete_task, name='delete_task'),
    path('<uuid:task_id>/update-status/', views.update_task_status, name='update_status'),
]
