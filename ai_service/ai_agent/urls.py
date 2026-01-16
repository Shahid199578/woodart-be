from django.urls import path
from .views import ChatView, AIConfigView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='ai_chat'),
    path('config/', AIConfigView.as_view(), name='ai_config'),
]
