from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid, os
from  PIL import Image

# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom manager for User Model where email is the unique identifier instead of username
    """

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email and password
        """
        if not email:
            raise ValueError('Users must have an email address!')
        
        email = self.normalize_email(email) # Converts email to lowercase
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password) #Hashes the password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Creates and saves a superuser with admin privileges.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, first_name, last_name, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that uses email instead of username for authentication
    """

    #unique identifier for each user
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #Authentication fields
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    #profile fields
    year_of_study = models.IntegerField(
        null=True,
        blank=True,
        choices=[
            (1, 'Year 1'),
            (2, 'Year 2'),
            (3, 'Year 3'),
            (4, 'Year 4'),
            (5, 'Year 5'),
        ]
    )
    course = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text='Upload a profile picture(max 5MB)'
    )

    #Notification preferences 
    reminder_time = models.TimeField(
        default=timezone.now().replace(hour=8, minute=0, second=0, microsecond=0).time(),
        help_text="Time of the day to receive daily assignment reminders(e.g, 08:00 AM)"
    )
    email_notifications = models.BooleanField(default=True)

    #Account status
    is_active = models.BooleanField(default=False) # False until email verified
    is_staff =models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    #Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    #Tell Django which fields to use for login

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] #Required when creating a superuser

    #Use our custom manager
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']


    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    def get_initials(self):
        """Retur User initials """
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None

    def save(self, *args, **kwargs):
        """Override save to rsize profile picture and deleteold ones"""
        try:
            """Check if thi is anupdate(Object exists in the db)"""
            old_instance = User.objects.get(pk=self.pk)

            #if profile picture changed, delete the old one
            if old_instance.profile_picture and old_instance.profile_picture != self.profile_picture:
                if os.path.isfile(old_instance.profile_picture.path):
                    os.remove(old_instance.profile_picture.path)

        except User.DoesNotExist:
            #New user no old profil pictureto delete
            pass
        super().save(*args,**kwargs)

        #Resize profile pcture if it exists

        if self.profile_picture:
            self._resize_profile_picture()
    

    def _resize_profile_picture(self):
        """Resize profil pictre to 300*3000 pixwl to sav storage"""
        try:
            img = Image.open(self.profile_picture.path)

            #convrt RGBA T RGBif necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255,255,255))
                background.paste(img,mask=img.split()[-1] if img.mode == 'RGB' else None)
                img = background

            #Resize maintaining aspet ratio
            max_size = (300,300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            #SAVE BACK
            img.save(self.profile_picture.path, quality=85, optimize=True)

        except Exception as e:
            #log error but don't cruhsh
            print(f'Error resizing profile picture: {str(e)}')


    def delete(self, *args,**kwargs):
        """Overwrite delete to remove profile picture file when user is deleted"""

        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)

        super().delete(*args, **kwargs)
        

class EmailVerification(models.Model):
    """
    Stores tokens for email verificatio.
    Tokens expires after 24 hours
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'


    def __str__(self):
        return f"Token for {self.user.email}"
    
    def is_valid(self):
        """Check if token is still valid(within 24 hours)"""
        expiry_time = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() < expiry_time