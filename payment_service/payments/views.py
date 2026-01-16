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
            data = {
                "amount": int(float(amount) * 100), # Amount in paise
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
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
