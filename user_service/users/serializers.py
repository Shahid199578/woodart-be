from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

from django.utils.html import escape

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(read_only=True) # FIX: Prevent Privilege Escalation

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'role', 'brand_name', 'gst_number', 'mobile', 'business_address', 'warehouse_address', 'password')

    def validate_username(self, value): return escape(value)
    def validate_full_name(self, value): return escape(value)
    def validate_brand_name(self, value): return escape(value)
    def validate_business_address(self, value): return escape(value)
    def validate_warehouse_address(self, value): return escape(value)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'full_name')

    def validate_username(self, value): return escape(value)
    def validate_full_name(self, value): return escape(value)

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        return data
