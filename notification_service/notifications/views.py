from rest_framework import generics, permissions
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin or owner
        if getattr(request.user, 'token', {}).get('role') == 'admin':
            return True
        return obj.user_id == request.user.id or obj.user_id is None

class NotificationList(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        # Return User's notifications OR Broadcasts (user_id=None)
        return Notification.objects.filter(Q(user_id=user_id) | Q(user_id__isnull=True)).order_by('-created_at')

class NotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOrAdmin]

from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import status

from .models import NotificationConfig
from .serializers import NotificationConfigSerializer
from django.core.mail.backends.smtp import EmailBackend

class NotificationConfigView(generics.RetrieveUpdateAPIView):
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer
    permission_classes = [IsOwnerOrAdmin] # Ideally Admin only

    def get_object(self):
        obj, created = NotificationConfig.objects.get_or_create(pk=1)
        return obj

class SendEmailView(APIView):
    def post(self, request):
        to_email = request.data.get('to_email')
        subject = request.data.get('subject')
        template_name = request.data.get('template_name')
        context = request.data.get('context', {})

        if not all([to_email, subject, template_name]):
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch Config
            config, _ = NotificationConfig.objects.get_or_create(pk=1)
            
            # Helper to get connection
            connection = EmailBackend(
                host=config.email_host,
                port=config.email_port,
                username=config.email_host_user,
                password=config.email_host_password,
                use_tls=config.email_use_tls,
                fail_silently=False
            )

            html_message = render_to_string(f'emails/{template_name}.html', context)
            
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(
                subject, 
                '', # plain text 
                config.default_from_email, 
                [to_email], 
                connection=connection
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()

            return Response({'status': 'Email Sent'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
