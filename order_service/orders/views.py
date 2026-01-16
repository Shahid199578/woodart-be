from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.conf import settings
from .models import Order, OrderItem
from .utils import get_product_details
from decimal import Decimal

class CreateOrderView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        items = request.data.get('items', [])
        shipping_address = request.data.get('shippingAddress', '')
        
        # B2B Fields
        is_b2b = request.data.get('isB2B', False)
        gst_number = request.data.get('gstNumber', None)
        partial_percentage = Decimal(str(request.data.get('partialPercentage', 100)))

        if not items:
            return Response({'error': 'No items in cart'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = Decimal('0.00')
        order_items_data = []

        # Validate Prices & Stock
        for item in items:
            product_id = item.get('id') or item.get('product_id')
            quantity = item.get('quantity', 1)
            
            product_data = get_product_details(product_id)
            if not product_data:
                return Response({'error': f'Product {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            price = Decimal(str(product_data['price']))
            line_total = price * quantity
            total_amount += line_total
            
            order_items_data.append({
                'product_id': product_id,
                'product_name': product_data['name'],
                'quantity': quantity,
                'price': price
            })

        # Calculate Payment Amount
        charge_amount = total_amount
        if is_b2b:
            charge_amount = (total_amount * partial_percentage) / 100
        
        try:
            # Create Order Record with Pending Status
            order = Order.objects.create(
                user_id=request.user.id,
                total_amount=total_amount,
                paid_amount=charge_amount, # Expected payment
                balance_due=total_amount - charge_amount,
                is_b2b=is_b2b,
                gst_number=gst_number,
                shipping_address=shipping_address,
                status='pending' # Waiting for payment
            )

            for item in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    price_at_purchase=item['price']
                )

            return Response({
                'orderId': order.id,
                'totalAmount': total_amount,
                'payableAmount': charge_amount,
                'currency': 'INR'
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConfirmOrderPaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('orderId')
        payment_id = request.data.get('paymentId') # Razorpay Payment ID or Transaction ID

        if not order_id or not payment_id:
             return Response({'error': 'Missing orderId or paymentId'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user_id=request.user.id)
            
            # Update Status
            order.status = 'partial_paid' if order.is_b2b else 'paid'
            order.stripe_payment_id = payment_id # Storing Razorpay ID in existing field for now (rename later if needed)
            order.save()

            # Send Invoice Email
            try:
                import requests
                items_list = [{'name': i.product_name, 'quantity': i.quantity, 'price': str(i.price_at_purchase)} for i in order.items.all()]
                requests.post(f'{settings.NOTIFICATION_SERVICE_URL}/api/send-email/', json={
                    'to_email': request.user.token.get('email'), 
                    'subject': f'Invoice #{order.id} - A TO Z WoodArt',
                    'template_name': 'invoice',
                    'context': {
                        'order_id': order.id,
                        'date': order.created_at.strftime('%Y-%m-%d'),
                        'name': getattr(request.user, 'token', {}).get('full_name', 'Customer'),
                        'items': items_list,
                        'total': str(order.total_amount)
                    }
                }, timeout=3)
            except Exception as e:
                print(f"Failed to send email: {e}")

            return Response({'status': 'Order Confirmed'})

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework import generics, permissions
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Order
from .serializers import OrderSerializer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io

class InvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            # Check permission
            is_admin = getattr(request.user, 'token', {}).get('role') == 'admin'
            if order.user_id != request.user.id and not is_admin:
                return HttpResponse("Unauthorized", status=403)

            # Generate PDF
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Header
            p.setFont("Helvetica-Bold", 24)
            p.drawString(50, height - 50, "A TO Z WoodArt")
            
            p.setFont("Helvetica", 12)
            p.drawString(50, height - 80, f"Invoice #{order.id}")
            p.drawString(50, height - 100, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
            if order.gst_number:
                p.drawString(50, height - 120, f"GSTIN: {order.gst_number}")
            
            # Financial Summary
            p.setFont("Helvetica-Bold", 12)
            p.drawString(400, height - 60, "Financials (INR)")
            p.setFont("Helvetica", 12)
            p.drawString(400, height - 80, f"Total: Rs. {order.total_amount}")
            p.drawString(400, height - 100, f"Paid: Rs. {order.paid_amount}")
            p.drawString(400, height - 120, f"Due: Rs. {order.balance_due}")
            
            status_color = colors.green if order.balance_due == 0 else colors.red
            p.setFillColor(status_color)
            p.drawString(400, height - 140, f"Status: {order.status.upper().replace('_', ' ')}")
            p.setFillColor(colors.black)

            # Items
            y = height - 180
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Item")
            p.drawString(300, y, "Qty")
            p.drawString(400, y, "Price")
            p.drawString(500, y, "Total")
            
            y -= 20
            p.line(50, y+10, 550, y+10)
            
            p.setFont("Helvetica", 10)
            for item in order.items.all():
                if y < 50:
                    p.showPage()
                    y = height - 50
                
                p.drawString(50, y, item.product_name[:40])
                p.drawString(300, y, str(item.quantity))
                p.drawString(400, y, f"{item.price_at_purchase}")
                p.drawString(500, y, f"{item.quantity * item.price_at_purchase}")
                y -= 20

            # Footer
            p.line(50, y+10, 550, y+10)
            y -= 30
            p.setFont("Helvetica-Oblique", 10)
            p.drawString(50, y, "Thank you for choosing A TO Z WoodArt.")

            p.showPage()
            p.save()

            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
            return response

        except Order.DoesNotExist:
            return HttpResponse("Order not found", status=404)


class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'token', {}).get('role') == 'admin':
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user_id=user.id).order_by('-created_at')

class OrderDetail(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        is_admin = getattr(user, 'token', {}).get('role') == 'admin'
        if obj.user_id != user.id and not is_admin:
            self.permission_denied(self.request)
        return obj

