from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.accounts.models import Account
from app.transactions.models import Transaction
from app.transactions.serializers import (
    TransactionHistorySerializer,
    TransactionsCreateSerializer,
    TransactionsUpdateSerializer,
)


class TransactionView(APIView):
    @extend_schema(
        summary="현재 로그인된 사용자의 모든 계좌 거래 내역 조회",
        description="인증된 사용자가 소유한 모든 계좌의 거래 내역을 최근 거래일 기준으로 내림차순으로 조회합니다.",
        responses={
            200: TransactionHistorySerializer(many=True),
            401: {"description": "인증 정보 없음 (Unauthorized)"},
            404: {"description": "사용자 계좌를 찾을 수 없음"},
        },
        tags=["transaction"],
    )
    # 현재 로그인 된 사용자 거래 내역 조회
    def get(self, request):
        # 사용자와 연결된 계좌 가져오기
        accounts = Account.objects.filter(user=request.user)
        if not accounts.exists():
            return Response(
                {"error": "사용자 계좌를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 해당 계좌의 모든 거래 내역 조회 - 최근 거래 시간 순으로 정렬
        # account__in 은 account 필드 값이 특정 집합에 포함되는지 확인
        transactions = Transaction.objects.filter(account__in=accounts).order_by(
            "-transaction_date"
        )  # 내림차순
        serializer = TransactionHistorySerializer(
            transactions, many=True
        )  # 거래 내역 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionCreateView(APIView):
    @extend_schema(
        summary="새로운 거래 내역 생성 및 계좌 잔액 업데이트",
        description="입금 또는 출금 거래 내역을 생성하고, 해당 계좌의 잔액을 업데이트합니다.",
        request=TransactionsCreateSerializer,
        responses={
            201: TransactionsCreateSerializer,
            400: {"description": "잘못된 요청 데이터 (Bad Request)"},
            401: {"description": "인증 정보 없음 (Unauthorized)"},
            403: {"description": "접근 권한 없음 (Forbidden)"},
        },
        tags=["transaction"],
    )
    # 거래 내역 생성
    def post(self, request):
        account_id = request.data.get("account")
        io_type = request.data.get("io_type")
        transaction_type = request.data.get("transaction_type")
        transaction_amount = request.data.get("amount")

        if not account_id:
            return Response(
                {"error": "계좌 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        if transaction_amount is None:
            return Response(
                {"error": "거래 금액이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        if io_type not in ["DEPOSIT", "WITHDRAW"]:
            return Response(
                {"error": "올바른 거래 유형(DEPOSIT 또는 WITHDRAW)을 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if transaction_type not in [
            "ATM",
            "TRANSFER",
            "AUTOMATIC_TRANSFER",
            "CARD",
            "INTEREST",
        ]:
            return Response({"error": "올바른 거래 종류를 입력해주세요"})

        # 사용자의 계좌가 맞는지 확인
        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            # 해당 ID의 계좌가 없거나 사용자의 소유가 아닐 경우
            return Response(
                {"error": "유효하지 않은 계좌 ID이거나, 접근 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Django의 Atomic Transaction을 사용하여 잔액 업데이트와 거래 내역 생성을 원자적으로 처리
        with transaction.atomic():
            current_balance = account.balance
            new_balance = current_balance

            try:
                transaction_amount = Decimal(str(transaction_amount))
            except (ValueError, TypeError):
                return Response(
                    {"error": "잘못된 거래 금액 형식입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if io_type == "DEPOSIT":
                new_balance = current_balance + transaction_amount
            elif io_type == "WITHDRAW":
                if transaction_amount > current_balance:
                    return Response(
                        {"error": "잔액이 부족합니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                new_balance = current_balance - transaction_amount

            # 시리얼라이저를 통한 거래 내역 생성
            # post_transaction_amount는 뷰에서 계산하여 전달
            serializer = TransactionsCreateSerializer(data=request.data)
            if serializer.is_valid():
                # 유효한 데이터라면 저장
                serializer.save(account=account, balance_after=new_balance)

                # 계좌 잔액 업데이트
                account.balance = new_balance
                account.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryDetailView(APIView):
    @extend_schema(
        summary="특정 거래 내역 수정",
        description="지정된 ID의 거래 내역을 수정합니다. 부분 업데이트가 가능하며, 해당 거래가 로그인된 사용자의 계좌와 연결되어 있어야 합니다.",
        request=TransactionsUpdateSerializer(partial=True),  # partial=True 명시
        responses={
            200: TransactionsUpdateSerializer,
            400: {"description": "잘못된 요청 데이터 (Bad Request)"},
            401: {"description": "인증 정보 없음 (Unauthorized)"},
            404: {"description": "거래 내역을 찾을 수 없음"},
        },
        tags=["transaction"],
    )
    # 특정 거래 내역 수정
    def put(self, request, pk):
        # 거래 내역 ID로 특정 거래 내역 조회 (로그인된 사용자의 계좌와 연결된 거래만 허용)
        transaction_obj = get_object_or_404(
            Transaction, pk=pk, account__user=request.user
        )
        # account__user 는 관계 모델의 특정 필드를 지정해서 필터링하거나 값을 가져올 때 사용
        # transaction -FK> account -FK> user

        # 데이터 업데이트
        serializer = TransactionsUpdateSerializer(
            transaction_obj, data=request.data, partial=True
        )
        # partial=True 는 부분 업데이트를 허용하여 요청 데이터에 포함된 필드만 업데이트 하고, 나머지는 기존값을 유지
        # partial 옵션을 설정하지 않으면 기본값인 False 가 되어 모든 필드가 포함 되어야 유효성 검증을 통과

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="특정 거래 내역 삭제",
        description="지정된 ID의 거래 내역을 삭제합니다. 해당 거래가 로그인된 사용자의 계좌와 연결되어 있어야 합니다.",
        responses={
            200: {"description": "성공적으로 삭제됨"},
            401: {"description": "인증 정보 없음 (Unauthorized)"},
            404: {"description": "거래 내역을 찾을 수 없음"},
        },
        tags=["transaction"],
    )
    # 특정 거래 내역 삭제
    def delete(self, request, pk):
        transaction_obj = get_object_or_404(
            Transaction, pk=pk, account__user=request.user
        )
        transaction_obj.delete()
        return Response(
            {"message": "거래 내역이 성공적으로 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
