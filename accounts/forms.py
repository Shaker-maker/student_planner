from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class RegistrationForm(UserCreationForm):
    """
    Form for user registration with email verification
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'your.email@student.ac.ke'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'John'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs= {
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Doe'

        })
    )
    year_of_study = forms.ChoiceField(
        choices=[
            ('', 'Select Year'),
            (1, 'Year 1'),
            (2, 'Year 2'),
            (3, 'Year 3'),
            (4, 'Year 4'),
            (5, 'Year 5'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

    course = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'e.g., Computer Science, Information Technology'
        })
    )
    semester = forms.ChoiceField(
        choices=[
            ('', 'Select Semester'),
            (1, 'Semester 1'),
            (2, 'Semester 2'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        required=True
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '.........'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder' :'.........'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'year_of_study', 'course', 'semester', 'password1', 'password2']

    
    def clean_email(self):
        """
        Validate that the email is unique
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def clean_year_of_study(self):
        """Convert year to integer"""
        year = self.cleaned_data.get('year_of_study')
        if year:
            return int(year)
        return year
    
    def clean_semester(self):
        """Convert semester to integer"""
        semester = self.cleaned_data.get('semester')
        if semester:
            return int(semester)
        return semester
    
class LoginForm(AuthenticationForm):
    """
    Custom login form with email instead of username
    """
    username = forms.EmailField(
        label='Email',
        widget= forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'your.email@student.ac.ke'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '..........'
        })
    )



class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user Profile information
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name','email','year_of_study','semester','course','profile_picture','reminder_time','email_notifications']
        widgets = {
            'first_name': forms.TextInput(attrs={
               'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
               }),

            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                }),

            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',

                }),

            'year_of_study': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                }),
            'semester': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                }),
            'course': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',

                }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
                'accept': 'image/*',

                }),
            'remainder_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',

                }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500',

                }),
            }

    def clean_mail(self):
        '''
        Validate that email is unique ( except for the current user)
        '''
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this email already exists')
        return email

    def clean_profile_picture(self):
        """
        Validate profile picture size and format
        """
        picture = self.cleaned_data.get('profile_picture')

        if picture:
            #Check file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file too large (max 5MB)')

            #Check file extension
            allowed_extensions = ['jpg','jpeg','png','gif']
            ext = picture.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f'Only {", ".join(allowed_extensions)} files are allowed. ')

        return picture     