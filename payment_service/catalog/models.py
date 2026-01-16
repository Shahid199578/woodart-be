from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50) 
    image_url = models.CharField(max_length=500, blank=True) # Changed from URLField
    stock_quantity = models.IntegerField(default=0)
    is_new = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Partner(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.CharField(max_length=500) # Changed from URLField
    website_url = models.CharField(max_length=500, blank=True) # Changed from URLField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
