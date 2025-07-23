from django.urls import path

from .views import (
    TransactionCreateView,
    TransactionHistoryDetailView,
    TransactionView,
)

app_name = "transactions"
urlpatterns = [
    path("", TransactionView.as_view(), name="transaction-list"),
    path("create/", TransactionCreateView.as_view(), name="transaction-create"),
    path(
        "<int:pk>/", TransactionHistoryDetailView.as_view(), name="transaction-detail"
),
]
