from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial_paid', 'Partially Paid'), # New Status
        ('paid', 'Fully Paid'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    )

    user_id = models.IntegerField() # Stored from JWT token
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financials
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # B2B Specifics
    is_b2b = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=20, blank=True, null=True)

    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    shipping_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255) # Snapshot
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
