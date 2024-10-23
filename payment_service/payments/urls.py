from django.urls import path
from .views import PaymentCreateView, PaymentStatusView


urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('status/<str:transaction_id>/', PaymentStatusView.as_view(), name='payment-status'),
]
