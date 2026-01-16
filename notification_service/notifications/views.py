from rest_framework import generics, permissions
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin or owner
        # FIX: Check request.auth for role claims
        is_admin = False
        try:
             if hasattr(request, 'auth') and hasattr(request.auth, 'get'):
                 is_admin = request.auth.get('role') == 'admin'
        except:
             pass
        
        if is_admin:
            return True
        return obj.user_id == request.user.id or obj.user_id is None

class IsInternalService(permissions.BasePermission):
    """
    Allows access only to internal services with the correct secret key.
    """
    def has_permission(self, request, view):
        import os
        internal_key = os.getenv('INTERNAL_SERVICE_KEY')
        request_key = request.headers.get('X-Internal-Secret')
        return internal_key and request_key == internal_key

# ... (NotificationList remains same)

class SendEmailView(APIView):
    # FIX: Require Internal Service Authentication
    permission_classes = [IsInternalService]

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
