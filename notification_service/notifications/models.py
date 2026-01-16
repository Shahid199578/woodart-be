from django.db import models

class Notification(models.Model):
    TYPES = (
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )

    user_id = models.IntegerField(null=True, blank=True) # Null for broadcast
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user_id or 'Broadcast'}"

class NotificationConfig(models.Model):
    email_host = models.CharField(max_length=255, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.CharField(max_length=255, blank=True)
    email_host_password = models.CharField(max_length=255, blank=True)
    default_from_email = models.CharField(max_length=255, default='noreply@atozwoodart.com')
    
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1 # Singleton
        super(NotificationConfig, self).save(*args, **kwargs)

    def __str__(self):
        return "Email Configuration"
