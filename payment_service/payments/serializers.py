from rest_framework import serializers
from .models import PaymentConfig, Transaction

class PaymentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentConfig
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
