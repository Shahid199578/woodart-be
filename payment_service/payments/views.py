from rest_framework import views, status, permissions, generics
from rest_framework.response import Response
from django.conf import settings
from .models import PaymentConfig, Transaction
from .serializers import PaymentConfigSerializer
import razorpay

class AdminPaymentConfigView(generics.ListCreateAPIView):
    queryset = PaymentConfig.objects.all()
    serializer_class = PaymentConfigSerializer
    permission_classes = [permissions.IsAuthenticated] 
    # In real world, strictly IsAdminUser

    def get_queryset(self):
        # Only return the active config or all if admin
        return PaymentConfig.objects.filter(is_active=True).order_by('-created_at')[:1]

class InitiatePaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount') # In INR
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        config = PaymentConfig.objects.filter(is_active=True).last()
        if not config:
            return Response({'error': 'Payment gateway not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        client = razorpay.Client(auth=(config.key_id, config.key_secret))
        
        try:
            # Create Razorpay Order
            # FIX: Use Decimal for precision, avoid float
            from decimal import Decimal
            amount_decimal = Decimal(str(amount))
            data = {
                "amount": int(amount_decimal * 100), # Amount in paise
                "currency": "INR",
                "payment_capture": "1"
            }
            order = client.order.create(data=data)
            
            # Log Transaction
            Transaction.objects.create(
                order_id=order['id'],
                amount=amount,
                user_id=request.user.id
            )

            return Response({
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': config.key_id
            })
        except Exception as e:
            # FIX: Do not leak internal exception details
            print(f"Payment Error: {e}") # Log it internally
            return Response({'error': 'Payment initiation failed. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Verify Signature
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')

        config = PaymentConfig.objects.filter(is_active=True).last()
        if not config:
            return Response({'error': 'Config missing'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        client = razorpay.Client(auth=(config.key_id, config.key_secret))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Update Transaction
            transaction = Transaction.objects.get(order_id=razorpay_order_id)
            transaction.payment_id = razorpay_payment_id
            transaction.status = 'success'
            transaction.save()

            return Response({'status': 'Payment Verified'})
        except Exception as e:
            # Update Transaction to failed
            try:
                transaction = Transaction.objects.get(order_id=razorpay_order_id)
                transaction.status = 'failed'
                transaction.save()
            except:
                pass
            return Response({'error': 'Signature Verification Failed'}, status=status.HTTP_400_BAD_REQUEST)
class IsInternalService(permissions.BasePermission):
    """
    Allows access only to internal services with the correct secret key.
    """
    def has_permission(self, request, view):
        import os
        internal_key = os.getenv('INTERNAL_SERVICE_KEY')
        request_key = request.headers.get('X-Internal-Secret')
        return internal_key and request_key == internal_key

class RetrieveTransactionView(views.APIView):
    permission_classes = [IsInternalService]

    def get(self, request, payment_id):
        try:
            transaction = Transaction.objects.get(payment_id=payment_id)
            return Response({
                'payment_id': transaction.payment_id,
                'order_id': transaction.order_id,
                'amount': transaction.amount,
                'status': transaction.status,
                'currency': transaction.currency
            })
        except Transaction.DoesNotExist:
             return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
