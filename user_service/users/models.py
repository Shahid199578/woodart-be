from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Profile Fields
    brand_name = models.CharField(max_length=100, blank=True)
    gst_number = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    business_address = models.TextField(blank=True)
    warehouse_address = models.TextField(blank=True)

    # Use email as default username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.email
