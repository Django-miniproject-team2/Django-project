from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account
from .serializers import AccountSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

class AccountListCreateView(APIView):
    """
    계좌 목록 조회 및 신규 계좌 생성
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="계좌 목록 조회",
        description="현재 로그인한 사용자의 계좌 목록을 조회합니다.",
        responses=AccountSerializer(many=True),
    )
    def get(self, request):
        """사용자의 계좌 목록을 조회합니다."""
        accounts = Account.objects.filter(user=request.user)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="신규 계좌 생성",
        description="새로운 계좌를 생성합니다.",
        request=AccountSerializer,
        responses={
            201: AccountSerializer,
            400: OpenApiResponse(description="유효성 검사 실패"),
        },
    )
    def post(self, request):
        """신규 계좌를 생성합니다."""
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)  # 현재 로그인된 사용자를 user로 설정
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccountDetailView(APIView):
    """
    특정 계좌의 상세 조회, 수정, 삭제
    """

    permission_classes = [IsAuthenticated]


    def get_object(self, pk, user):
        try:
            return Account.objects.get(pk=pk, user=user)
        except Account.DoesNotExist:
            return None

    @extend_schema(
        summary="계좌 상세 조회",
        description="특정 계좌의 정보를 조회합니다.",
        responses={
            200: AccountSerializer,
            404: OpenApiResponse(description="계좌를 찾을 수 없거나 권한이 없습니다."),
        },
    )
    def get(self, request, pk):
        """특정 계좌 정보를 조회합니다."""
        account = self.get_object(pk, request.user)
        if account is None:
            return Response(
                {"error": "계좌를 찾을 수 없거나 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    @extend_schema(
        summary="계좌 삭제",
        description="특정 계좌를 삭제합니다.",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            404: OpenApiResponse(description="계좌를 찾을 수 없거나 권한이 없습니다."),
        },
    )
    def delete(self, request, pk):
        """특정 계좌를 삭제합니다."""
        account = self.get_object(pk, request.user)
        if account is None:
            return Response(
                {"error": "계좌를 찾을 수 없거나 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
