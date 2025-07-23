from rest_framework import serializers

from apps.transactions.models import Transaction


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "amount",
            "description",
            "io_type",
            "transaction_type",
            "transaction_date",
        ]
        read_only_fields = ["id", "balance_after", "transaction_date"]


class TransactionsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "amount",
            "balance_after",
            "description",
            "io_type",
            "transaction_type",
            "transaction_date",
        ]
        read_only_fields = ["id"]
