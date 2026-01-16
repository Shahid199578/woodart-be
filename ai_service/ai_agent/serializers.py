from rest_framework import serializers
from .models import AIConfig

class AIConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConfig
        fields = '__all__'
