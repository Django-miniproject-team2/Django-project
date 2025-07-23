# from django.test import TestCase

# # Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Transaction

User = get_user_model()


class TransactionAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        success = self.client.login(username="testuser", password="testpass123")
        print("Login success?", success)

        self.client.login(email="test@example.com", password="testpass123")

        self.transaction = Transaction.objects.create(
            account=self.user,
            amount=10000,
            after=90000,
            account_details="ATM 입금",
            transaction_type="cash",
            deposit_withdrawal_type="deposit",
        )

        self.transaction_url = reverse("transaction-detail", args=[self.transaction.id])
        self.list_url = reverse("transaction-list")

    def test_transaction_create(self):
        data = {
            "amount": 5000,
            "after": 95000,
            "account_details": "올리브영",
            "transaction_type": "card_payment",
            "deposit_withdrawal_type": "withdrawal",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

    def test_transaction_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_transaction_filter(self):
        response = self.client.get(self.list_url + "?transaction_type=cash")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_transaction_update(self):
        data = {
            "amount": 12000,
            "after": 88000,
            "account_details": "올리브영",
            "transaction_type": "card_payment",
            "deposit_withdrawal_type": "withdrawal",
        }
        response = self.client.put(self.transaction_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, 12000)

    def test_transaction_delete(self):
        response = self.client.delete(self.transaction_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
