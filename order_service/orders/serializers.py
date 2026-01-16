from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_id', 'product_name', 'quantity', 'price_at_purchase')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user_id', 'status', 'total_amount', 'paid_amount', 'balance_due', 'is_b2b', 'gst_number', 'stripe_payment_id', 'shipping_address', 'created_at', 'items')
