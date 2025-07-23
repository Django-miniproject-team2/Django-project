from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Account
from apps.users.models import User


class AccountAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
            nickname="testuser",
            name="Test User",
            phone_number="01012345678",
        )
        self.client.force_authenticate(user=self.user)
        self.account_list_create_url = reverse("account-list-create")
        self.account_detail_url = lambda pk: reverse(
            "account-detail", kwargs={"pk": pk}
        )

    def test_create_account(self):
        """
        새로운 계좌를 생성하는 테스트
        """
        data = {
            "account_number": "1234567890",
            "bank_code": "004",  # 국민은행
            "account_type": "CHECKING",
        }
        response = self.client.post(self.account_list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().account_number, "1234567890")
        self.assertEqual(Account.objects.get().user, self.user)

    def test_create_account_without_authentication(self):
        """
        인증 없이 계좌 생성 시도 시 실패하는 테스트
        """
        self.client.force_authenticate(user=None)
        data = {
            "account_number": "1234567890",
            "bank_code": "004",
            "account_type": "CHECKING",
        }
        response = self.client.post(self.account_list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_accounts(self):
        """
        계좌 목록을 조회하는 테스트
        """
        Account.objects.create(
            user=self.user,
            account_number="1111111111",
            bank_code="004",
            account_type="CHECKING",
            balance=1000.00,
        )
        Account.objects.create(
            user=self.user,
            account_number="2222222222",
            bank_code="088",  # 신한은행
            account_type="SAVING",
            balance=2000.00,
        )
        response = self.client.get(self.account_list_create_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["account_number"], "1111111111")
        self.assertEqual(response.data[1]["account_number"], "2222222222")

    def test_retrieve_account(self):
        """
        특정 계좌를 상세 조회하는 테스트
        """
        account = Account.objects.create(
            user=self.user,
            account_number="1111111111",
            bank_code="004",
            account_type="CHECKING",
            balance=1000.00,
        )
        response = self.client.get(self.account_detail_url(account.pk), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_number"], "1111111111")

    def test_retrieve_non_existent_account(self):
        """
        존재하지 않는 계좌를 조회 시도 시 실패하는 테스트
        """
        response = self.client.get(self.account_detail_url(999), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_other_user_account(self):
        """
        다른 사용자의 계좌를 조회 시도 시 실패하는 테스트
        """
        other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="otherpassword123",
            nickname="otheruser",
            name="Other User",
            phone_number="01098765432",
        )
        other_account = Account.objects.create(
            user=other_user,
            account_number="3333333333",
            bank_code="004",
            account_type="CHECKING",
            balance=500.00,
        )
        response = self.client.get(
            self.account_detail_url(other_account.pk), format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # 권한이 없으므로 404 반환

    def test_delete_account(self):
        """
        계좌를 삭제하는 테스트
        """
        account = Account.objects.create(
            user=self.user,
            account_number="1111111111",
            bank_code="004",
            account_type="CHECKING",
            balance=1000.00,
        )
        response = self.client.delete(
            self.account_detail_url(account.pk), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.count(), 0)

    def test_delete_non_existent_account(self):
        """
        존재하지 않는 계좌를 삭제 시도 시 실패하는 테스트
        """
        response = self.client.delete(self.account_detail_url(999), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_other_user_account(self):
        """
        다른 사용자의 계좌를 삭제 시도 시 실패하는 테스트
        """
        other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="otherpassword123",
            nickname="otheruser",
            name="Other User",
            phone_number="01098765432",
        )
        other_account = Account.objects.create(
            user=other_user,
            account_number="3333333333",
            bank_code="004",
            account_type="CHECKING",
            balance=500.00,
        )
        response = self.client.delete(
            self.account_detail_url(other_account.pk), format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # 권한이 없으므로 404 반환
