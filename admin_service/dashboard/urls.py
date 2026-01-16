from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardStatsView, SiteConfigViewSet, PolicyViewSet, FAQViewSet

router = DefaultRouter()
router.register(r'config', SiteConfigViewSet, basename='site-config')
router.register(r'policies', PolicyViewSet)
router.register(r'faqs', FAQViewSet)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('', include(router.urls)),
]
