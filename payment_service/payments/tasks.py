from celery import shared_task
from .models import Payment
import random



@shared_task
def check_pending_payment(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        result = random.choice(['successful', 'failed'])
        payment.status = result
        payment.save()
    except Payment.DoesNotExist:
        pass