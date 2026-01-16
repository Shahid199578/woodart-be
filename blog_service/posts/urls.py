from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import BlogPostList, BlogPostDetail, UploadImage

urlpatterns = [
    path('posts/', BlogPostList.as_view(), name='post-list'),
    path('posts/<slug:slug>/', BlogPostDetail.as_view(), name='post-detail'),
    path('upload/', UploadImage.as_view(), name='image-upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
