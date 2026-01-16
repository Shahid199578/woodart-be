from rest_framework import views, status, permissions, generics
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.conf import settings
from google import genai
from google.genai import types
from .constants import SYSTEM_INSTRUCTION
from .models import AIConfig
from .serializers import AIConfigSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # FIX: Check request.auth for role claims
        try:
             if hasattr(request, 'auth') and hasattr(request.auth, 'get'):
                 return request.auth.get('role') == 'admin'
        except:
             pass
        return False

class AIConfigView(generics.RetrieveUpdateAPIView):
    queryset = AIConfig.objects.all()
    serializer_class = AIConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_object(self):
        obj, created = AIConfig.objects.get_or_create(pk=1)
        return obj

class ChatView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        message = request.data.get('message', '')

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            config = AIConfig.objects.filter(pk=1).first()
            if not config or not config.google_api_key:
                return Response({'response': "AI brain is currently offline."}, status=200)

            client = genai.Client(api_key=config.google_api_key)
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
            
            return Response({'response': response.text})
        except Exception as e:
            # Fallback if API fails or quota exceeded
            # FIX: Do not leak exception details to user
            print(f"AI Service Error: {e}") 
            return Response({'response': "Forgive me, my tools are momentarily misplaced. (Service Busy)"}, status=200)
