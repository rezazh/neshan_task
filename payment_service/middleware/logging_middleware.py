import logging

from neshan_task.payment_service.payments.models import RequestLog

logger = logging.getLogger(__name__)
from django.utils.timezone import now

class RequestLoggingMiddleware:
    """
    Middleware to log every request, including the user, request type, and other relevant information.
    Logs are saved to the database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            RequestLog.objects.create(
                user=request.user,
                method=request.method,
                path=request.get_full_path(),
                timestamp=now(),
                ip_address=self.get_client_ip(request)
            )

        return response

    def get_client_ip(self, request):
        """
        Get the IP address of the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip