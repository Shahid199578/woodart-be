from django.urls import path
from .views import CreateOrderView, ConfirmOrderPaymentView, OrderList, OrderDetail, InvoiceView

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('confirm-payment/', ConfirmOrderPaymentView.as_view(), name='confirm-payment'),
    path('orders/', OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
    path('orders/<int:pk>/invoice/', InvoiceView.as_view(), name='order-invoice'),
]
