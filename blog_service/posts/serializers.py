from rest_framework import serializers
from .models import BlogPost

from django.utils.html import escape

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'

    def validate_content(self, value):
        # FIX: Escape HTML to prevent XSS
        return escape(value)
    
    def validate_title(self, value):
        return escape(value)
