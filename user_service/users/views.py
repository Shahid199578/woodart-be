from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import AnonRateThrottle
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = UserSerializer.Meta.model.objects.all()
    # FIX: Throttling to prevent Email Bombing
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [AnonRateThrottle]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Trigger Welcome Email (Async ideally, but sync for now)
        try:
            import requests
            email = request.data.get('email')
            name = request.data.get('full_name') or request.data.get('username')
            # Safe internal communication
            import os
            notification_url = os.getenv('NOTIFICATION_SERVICE_URL', 'http://woodcraft-notification-service:8006')
            internal_key = os.getenv('INTERNAL_SERVICE_KEY')
            requests.post(f'{notification_url}/api/send-email/', json={
                'to_email': email,
                'subject': 'Welcome to A TO Z WoodArt',
                'template_name': 'welcome',
                'context': {'name': name}
            }, headers={'Content-Type': 'application/json', 'X-Internal-Secret': internal_key}, timeout=5) # FIX: Added Auth Header
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            
        return response

class CustomTokenObtainPairView(TokenObtainPairView):
    # FIX: Rate Limit Login to prevent Brute Force
    throttle_classes = [AnonRateThrottle]
    serializer_class = CustomTokenObtainPairSerializer

class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = UserSerializer.Meta.model.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
