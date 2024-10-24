from .models import Payment
from celery import shared_task
from django.utils.timezone import now, timedelta
from django.db.models import Count
from .models import RequestLog, RequestLogSummary
from django.contrib.auth.models import User
from django.db import transaction
from .services import track_bank_payment


@shared_task
def check_pending_payment(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)

        if payment.status == 'pending':
            final_result = track_bank_payment(payment)
            payment.status = final_result
            payment.save()
    except Payment.DoesNotExist:
        pass



@shared_task
def summarize_request_logs():
    """
    Task that summarizes the request logs per user every 30 days.
    It stores the summarized data in RequestLogSummary and deletes old RequestLog entries.
    """
    current_date = now()
    first_day_of_current_month = current_date.replace(day=1)

    last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_month.replace(day=1)

    summary_data = (
        RequestLog.objects
            .filter(timestamp__gte=first_day_of_last_month, timestamp__lt=first_day_of_current_month)
            .values('user')
            .annotate(request_count=Count('id'))
    )

    with transaction.atomic():
        for data in summary_data:
            user_id = data['user']
            request_count = data['request_count']

            user = User.objects.get(id=user_id)

            RequestLogSummary.objects.create(
                user=user,
                month=first_day_of_last_month,
                request_count=request_count
            )

        RequestLog.objects.filter(timestamp__lt=first_day_of_current_month).delete()