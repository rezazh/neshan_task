from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payment, TransactionLog
from .serializers import PaymentSerializer
import uuid
from rest_framework.permissions import IsAdminUser

from .services import make_bank_payment
from .tasks import check_pending_payment
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from rest_framework_simplejwt.authentication import JWTAuthentication


class PaymentCreateView(APIView):
    uthentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = request.data.get('amount')

        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        if Payment.objects.filter(user=user, status='pending').exists():
            return Response({'error': 'You have a pending payment.'}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            user=user,
            amount=amount,
            status='pending',
            transaction_id=str(uuid.uuid4())
        )

        TransactionLog.objects.create(
            user=user,
            transaction_id=payment.transaction_id,
            status=payment.status
        )

        initial_result = make_bank_payment()
        payment.status = initial_result
        payment.save()

        if initial_result == 'pending':
            check_pending_payment.apply_async((payment.id,), countdown=10800)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        TransactionLog.objects.create(
            user=request.user,
            transaction_id=transaction_id,
            status=payment.status
        )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)



class UserPaymentReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)



class PaymentReportByDateRangeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'error': 'Both start_date and end_date are required'}, status=status.HTTP_400_BAD_REQUEST)

        payments = Payment.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class AllRequestsReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        logs = TransactionLog.objects.all()
        log_data = [{'user': log.user.username, 'transaction_id': log.transaction_id, 'status': log.status, 'timestamp': log.timestamp} for log in logs]
        return Response(log_data)
