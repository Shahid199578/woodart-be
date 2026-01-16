from rest_framework import views, status, permissions, viewsets
from rest_framework.response import Response
from .models import SiteConfig, Policy, FAQ
from .serializers import SiteConfigSerializer, PolicySerializer, FAQSerializer

class IsAdminUser(permissions.BasePermission):
    """
    Strict Admin-only access.
    """
    def has_permission(self, request, view):
        try:
             # FIX: Use request.auth
             if hasattr(request, 'auth') and isinstance(request.auth, dict):
                 return request.auth.get('role') == 'admin'
             if request.auth and hasattr(request.auth, 'get'):
                  return request.auth.get('role') == 'admin'
             return False
        except:
             return False

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Read-only for everyone, Admin for unsafe methods.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
             if hasattr(request, 'auth') and hasattr(request.auth, 'get'):
                 return request.auth.get('role') == 'admin'
        except:
             pass
        return False

class DashboardStatsView(views.APIView):
    permission_classes = [IsAdminUser] # Strict

    def get(self, request):
        # In a real microservice, this would query api-gateway or other services
        data = {
            "totalUsers": 0,
            "totalOrders": 0,
            "revenue": 0,
            "lowStockProducts": 0
        }
        return Response(data)

class SiteConfigViewSet(viewsets.ModelViewSet):
    queryset = SiteConfig.objects.all()
    serializer_class = SiteConfigSerializer
    permission_classes = [IsAdminOrReadOnly] # Public Read

    def get_object(self):
        # Singleton pattern for SiteConfig
        obj, created = SiteConfig.objects.get_or_create(pk=1)
        return obj

    def list(self, request, *args, **kwargs):
        # Always return the single object
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAdminOrReadOnly]

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]

