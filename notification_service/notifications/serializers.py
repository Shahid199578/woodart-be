from rest_framework import serializers
from .models import Notification, NotificationConfig

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class NotificationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationConfig
        fields = '__all__'
