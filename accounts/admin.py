from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerification

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model
    """
    list_display = ['email', 'first_name','last_name','year_of_study','is_email_verified','is_active','date_joined']
    list_filter = ['is_active', 'is_email_verified', 'year_of_study', 'date_joined']
    search_fields = ['email','first_name','last_name']
    ordering = ['date_joined']

    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name','last_name','year_of_study','course','profile_picture')
        }),
        ('Notifications', {
            'fields':('reminder_time', 'email_notifications')
        }),
        ('Permissions', {
            'fields':('is_active','is_staff','is_superuser', 'is_email_verified')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields' : ('email', 'first_name', 'last_name','password1','password2')

        }),
    )

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing email verification tokens
    """
    list_display = ['user','token','created_at','is_valid']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token','created_at']

    