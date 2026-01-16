from rest_framework import serializers
from .models import Product, Category, Partner

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    imageUrl = serializers.CharField(source='image_url', read_only=True)
    isNew = serializers.BooleanField(source='is_new', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'image_url', 'imageUrl', 'isNew', 'stock_quantity', 'b2b_price', 'moq', 'created_at')
        extra_kwargs = {
            'image_url': {'required': False, 'allow_blank': True}
        }

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'
        extra_kwargs = {
            'website_url': {'required': False, 'allow_blank': True}
        }
