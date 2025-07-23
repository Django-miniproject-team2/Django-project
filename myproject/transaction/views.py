# from django.shortcuts import render

# # Create your views here.
# transactions/views.py

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["transaction_type", "deposit_withdrawal_type"]
    ordering_fields = ["transaction_date", "amount"]

    def get_queryset(self):
        return Transaction.objects.filter(account=self.request.user)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)
