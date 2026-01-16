from rest_framework import generics, permissions, filters
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Partner
from .serializers import ProductSerializer, CategorySerializer, PartnerSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
             # FIX: Use request.auth to access token claims, or request.user.role if user is loaded
             # Ideally check request.user.is_staff if backed by DB
             # But assuming stateless token auth with 'role' claim:
             if hasattr(request, 'auth') and isinstance(request.auth, dict):
                 return request.auth.get('role') == 'admin'
             # Fallback if request.auth is the token object (SimpleJWT 5.x+)
             if request.auth and hasattr(request.auth, 'get'):
                  return request.auth.get('role') == 'admin'
             return False
        except:
             return False

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage

class UploadImage(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # FIX: Validate extension
        import os
        import uuid
        ext = os.path.splitext(file_obj.name)[1].lower()
        allowed_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if ext not in allowed_exts:
             return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)

        # FIX: Randomize filename to prevent path traversal/overwrites
        new_filename = f"{uuid.uuid4()}{ext}"
        
        file_name = default_storage.save(new_filename, file_obj)
        file_url = default_storage.url(file_name)
        
        return Response({"url": file_url}, status=status.HTTP_201_CREATED)

class PartnerList(generics.ListCreateAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]

class PartnerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]

class IsInternalService(permissions.BasePermission):
    """
    Allows access only to internal services with the correct secret key.
    """
    def has_permission(self, request, view):
        import os
        internal_key = os.getenv('INTERNAL_SERVICE_KEY')
        request_key = request.headers.get('X-Internal-Secret')
        return internal_key and request_key == internal_key

class DeductStockView(APIView):
    permission_classes = [IsInternalService]

    def post(self, request, pk):
        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Atomic Update
        updated_rows = Product.objects.filter(id=pk, stock_quantity__gte=quantity).update(stock_quantity=F('stock_quantity') - quantity)
        
        if updated_rows == 0:
            return Response({'error': 'Out of stock'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'status': 'Stock deducted'})

class RefundStockView(APIView):
    permission_classes = [IsInternalService]
    
    def post(self, request, pk):
        quantity = int(request.data.get('quantity', 1))
        # Atomic Refund
        Product.objects.filter(id=pk).update(stock_quantity=F('stock_quantity') + quantity)
        return Response({'status': 'Stock refunded'})
