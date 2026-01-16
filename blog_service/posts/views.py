from rest_framework import generics, permissions
from .models import BlogPost
from .serializers import BlogPostSerializer

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check simplejwt token role
        try:
             # FIX: Use request.auth
             if hasattr(request, 'auth') and hasattr(request.auth, 'get'):
                 return request.auth.get('role') == 'admin'
             return False
        except:
             return False

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

        # FIX: Randomize filename
        new_filename = f"{uuid.uuid4()}{ext}"
        
        file_name = default_storage.save(new_filename, file_obj)
        file_url = default_storage.url(file_name)
        
        return Response({"url": file_url}, status=status.HTTP_201_CREATED)

class BlogPostList(generics.ListCreateAPIView):
    queryset = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = BlogPostSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # Admin sees all, users see published
        is_admin = False
        try:
            if self.request.auth and hasattr(self.request.auth, 'get'):
                is_admin = self.request.auth.get('role') == 'admin'
        except:
            pass
            
        if is_admin:
            return BlogPost.objects.all().order_by('-created_at')
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')

class BlogPostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
