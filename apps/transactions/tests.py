from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Account
from apps.transactions.models import Transaction

User = get_user_model()


class TransactionHistoryAPITestCase(APITestCase):
    def setUp(self):
        # 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

        # email 기반 로그인
        login_successful = self.client.login(
            email="test@example.com", password="testpass123"
        )
        assert login_successful, "로그인 실패"

        # 계좌 생성
        self.account = Account.objects.create(
            user=self.user,
            balance=Decimal("100000.00"),
        )

        # 거래 내역 1건 생성
        self.transaction = Transaction.objects.create(
            account=self.account,
            amount=Decimal("10000.00"),
            io_type="DEPOSIT",
            transaction_type="ATM",
            balance_after=Decimal("110000.00"),
            description="초기 입금",
        )
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # URL 세팅 (urls.py에 아래 이름이 맞는지 확인 필수)
        self.list_url = reverse("transactions:transaction-list")  # GET 전체 조회
        self.create_url = reverse("transactions:transaction-create")  # POST 생성
        self.detail_url = reverse(
            "transactions:transaction-detail", args=[self.transaction.id]
        )  # PUT/DELETE 대상

    def test_transaction_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 거래 내역 1건 존재

    def test_transaction_create(self):
        data = {
            "account": self.account.id,
            "amount": "5000.00",
            "io_type": "WITHDRAW",
            "transaction_type": "CARD",
            "description": "편의점 결제",
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

    def test_transaction_update(self):
        data = {
            "amount": "20000.00",
            "transaction_type": "TRANSFER",
            "description": "수정된 거래 내역",
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(str(self.transaction.amount), "20000.00")
        self.assertEqual(self.transaction.transaction_type, "TRANSFER")
        self.assertEqual(self.transaction.description, "수정된 거래 내역")

    def test_transaction_delete(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
