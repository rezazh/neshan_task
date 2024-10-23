from celery import shared_task
from .models import Payment



@shared_task
def check_pending_payment(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        # Simulate checking with the bank's API here (e.g., via a request to the bank's API)
        # For simplicity, we will mark it as successful after 3 hours
        payment.status = 'successful'
        payment.save()
    except Payment.DoesNotExist:
        pass