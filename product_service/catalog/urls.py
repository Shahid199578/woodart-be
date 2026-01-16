from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ProductList, ProductDetail, CategoryList, CategoryDetail, PartnerList, PartnerDetail, UploadImage, DeductStockView, RefundStockView

urlpatterns = [
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('partners/', PartnerList.as_view(), name='partner-list'),
    path('partners/<int:pk>/', PartnerDetail.as_view(), name='partner-detail'),
    path('upload/', UploadImage.as_view(), name='image-upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
