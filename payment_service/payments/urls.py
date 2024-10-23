from django.urls import path
from .views import PaymentCreateView, PaymentStatusView, UserPaymentReportView, PaymentReportByDateRangeView, \
    AllRequestsReportView

urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('status/<str:transaction_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('reports/user/', UserPaymentReportView.as_view(), name='user-payment-report'),
    path('reports/date-range/', PaymentReportByDateRangeView.as_view(), name='date-range-report'),
    path('reports/all-requests/', AllRequestsReportView.as_view(), name='all-requests-report'),

]
