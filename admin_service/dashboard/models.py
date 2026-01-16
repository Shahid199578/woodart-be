from django.db import models

class SiteConfig(models.Model):
    hero_title = models.CharField(max_length=255, default="A TO Z WoodArt")
    hero_subtitle = models.CharField(max_length=255, default="Timeless Elegance in Wood")
    hero_image_url = models.ImageField(upload_to='site_config/', blank=True, null=True)
    hero_background_url = models.ImageField(upload_to='site_config/', blank=True, null=True)
    
    contact_email = models.EmailField(default="contact@atozwoodart.com")
    contact_phone = models.CharField(max_length=20, default="+91 9876543210")
    business_address = models.TextField(default="123, Wood Street, Bangalore")
    
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    # B2B Settings
    b2b_partial_payment_percentage = models.IntegerField(default=50, help_text="Percentage of total amount to be paid upfront for B2B orders")

    def __str__(self):
        return "Site Configuration"

class Policy(models.Model):
    title = models.CharField(max_length=100) # e.g., Return Policy, Warranty
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class FAQ(models.Model):
    question = models.CharField(max_length=512)
    answer = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question
