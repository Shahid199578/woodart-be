from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, MeView, UserListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('me/', MeView.as_view(), name='auth_me'),
    path('users/', UserListView.as_view(), name='user_list'),
]
