from django.db import models

class PaymentConfig(models.Model):
    key_id = models.CharField(max_length=255)
    key_secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Razorpay Config ({'Active' if self.is_active else 'Inactive'})"

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    order_id = models.CharField(max_length=255) # Razorpay Order ID
    payment_id = models.CharField(max_length=255, blank=True, null=True) # Razorpay Payment ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.status}"
