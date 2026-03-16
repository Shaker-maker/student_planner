from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import User, EmailVerification


def register_view(request):
    """
    Handles user registration and sends verification email.
    """
    if request.user.is_authenticated:
        return redirect('timetable:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # User can't login until email verified
            user.save()
            
            # Create verification token
            token = EmailVerification.objects.create(user=user)
            
            # Build verification URL
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': str(token.token)})
            )
            
            # Send verification email
            subject = 'Verify Your Email - Student Study Planner'
            message = f"""
            Hi {user.first_name} 👋🏽,
            
            Welcome to Student Study Planner! Please verify your email by clicking the link below:
            
            {verification_url}
            
            This link expires in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            Student Study Planner Team.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, f'Account created! Please check {user.email} to verify your account.')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request, token):
    """
    Verifies user's email using the token sent to their email.
    """
    try:
        verification_token = EmailVerification.objects.get(token=token)
        
        if verification_token.is_valid():
            user = verification_token.user
            user.is_active = True
            user.is_email_verified = True
            user.save()
            
            # Delete the used token
            verification_token.delete()
            
            messages.success(request, 'Email verified successfully! You can now login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Verification link has expired. Please register again.')
            return redirect('accounts:register')
    
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('accounts:register')


def login_view(request):
    """
    Handles user login.
    """
    if request.user.is_authenticated:
        return redirect('timetable:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # It's called username in the form but holds email
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}! 👋🏽')
                    
                    # Redirect to 'next' parameter if exists, else dashboard
                    next_url = request.GET.get('next', 'timetable:dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Please verify your email before logging in.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Logs out the user.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Displays user profile.
    """
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    """
    Handles profile editing including profile picture upload
    """

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def delete_profile_picture_view(request):
    """
    Delete user's profile picture
    
    """
    if request.method == 'POST':
        user = request.user
        if user.profile_picture:
            #Delete the file
            user.profile_picture.delete(save=False)
            user.profile_picture = None
            user.save(update_fields=['profile_picture'])
            
            messages.success(request, '🗑️ Profile picture deleted successfully.')
        else:
            messages.info(request, 'You don\'t have a profile picture to delete.')

        return redirect('accounts:edit_profile')

    return redirect('accounts:profile')