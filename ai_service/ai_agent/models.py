from django.db import models

class AIConfig(models.Model):
    google_api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super(AIConfig, self).save(*args, **kwargs)

    def __str__(self):
        return "AI Configuration"
