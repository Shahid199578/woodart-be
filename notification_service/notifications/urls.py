from django.urls import path
from .views import NotificationList, NotificationDetail, SendEmailView, NotificationConfigView

urlpatterns = [
    path('notifications/', NotificationList.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetail.as_view(), name='notification-detail'),
    path('config/email/', NotificationConfigView.as_view(), name='email-config'),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]
