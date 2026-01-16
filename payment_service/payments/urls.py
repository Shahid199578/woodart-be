from django.urls import path
from .views import AdminPaymentConfigView, InitiatePaymentView, PaymentCallbackView

urlpatterns = [
    path('admin/config/', AdminPaymentConfigView.as_view(), name='payment-config'),
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]
