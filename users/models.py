from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager

# CustomUserModel create inheriate abstract user

class User(AbstractUser):
    ADMIN = 'admin'
    STAFF = 'staff'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN,"Admin"),
        (STAFF,'Staff'),
        (USER,'User')
    )
    username = 'None'
    email = models.EmailField(unique=True)
    first_name=models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100,null=True, blank=True)
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER,db_index=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # username remove must be override objects manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        indexes = [
            models.Index(fields=['role', 'is_active']),
        ]

class Company(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Business Info
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name','email','address','country'])
        ]

class Profile(models.Model):
    GENDER_CHOICES=(
        ('male',"Male"),
        ('female','Female'),
        ('others','Others')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Company Relation
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    profile_image = models.ImageField(upload_to='profile/',blank=True, null=True)
    bio = models.TextField(blank=True,null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,default='male')

    # Address (optional personal)
    present_address=models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.email
    
    class Meta:
        indexes = [
            models.Index(fields=['city','country']),
        ]
