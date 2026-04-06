from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager

# CustomUserModel create inheriate abstract user

class User(AbstractUser):
    ADMIN = 'admin'
    STAFF = 'staff'
    USER = 'usesr'

    ROLE_CHOICES = (
        (ADMIN,"Admin"),
        (STAFF,'Staff'),
        (USER,'User')
    )
    username = 'None'
    email = models.EmailField(unique=True)
    first_name=models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100,null=True, blank=True)
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # username remove must be override objects manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email