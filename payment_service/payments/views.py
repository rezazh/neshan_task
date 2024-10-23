from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payment
from .serializers import PaymentSerializer
import uuid
from .tasks import check_pending_payment

class PaymentCreateView(APIView):
    def post(self, request):
        user = request.user
        amount = request.data.get('amount')

        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        if Payment.objects.filter(user=user, status='pending').exists():
            return Response({'error': 'You have a pending payment. Please wait for it to complete.'},
                            status=status.HTTP_400_BAD_REQUEST)

        transaction_id = str(uuid.uuid4())

        payment = Payment.objects.create(
            user=user,
            amount=amount,
            transaction_id=transaction_id,
            status='pending'
        )

        check_pending_payment.apply_async((payment.id,), countdown=10800)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class PaymentStatusView(APIView):
    def get(self, request, transaction_id):
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
