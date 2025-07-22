from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsOwner
from .serializers import LoginSerializer, UserRegisterSerializer, UserSerializer


# 회원가입 API
class UserRegisterView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    # drf-spectacular 데코레이터: OpenAPI 자동 생성
    @extend_schema(
        summary="새로운 계정 생성",
        description="이메일, 닉네임, 이름, 비밀번호, 전화번호를 입력하여 새로운 계정을 생성합니다. ",
        request=UserRegisterSerializer,
        responses={
            201: {
                "description": "회원가입 성공",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "example": "회원가입이 성공적으로 완료되었습니다.",
                                }
                            },
                        },
                    },
                },
            },
            400: UserRegisterSerializer,  # 유효성 검사 실패 시 에러 반환
        },
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():  # 유효성 검사
            serializer.save()
            return Response(
                {"message": "회원가입이 성공적으로 완료되었습니다"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인 API
class JWTLoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {"message": "로그인이 성공적으로 완료되었습니다."},
            400: LoginSerializer,
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(
            raise_exception=True
        )  # 유효성 검사 실패 시 자동으로 400 응답

        # validate 메서드에서 설정한 user 가져오기
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        user_serializer = UserSerializer(user)

        response = Response(
            {"access": access_token, "user": user_serializer.data},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "refresh_token",
            value=str(refresh),
            httponly=True,
            secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
            samesite="Lax",
            max_age=5 * 60 * 60,
        )
        return response


# 로그아웃 API
class JWTLogoutView(APIView):

    @extend_schema(
        responses={
            205: {"message": "성공적으로 로그아웃되었습니다."},
            500: {"message": "서버에 문제가 있습니다."},
        }
    )
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token이 제공되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(
                {"message": "성공적으로 로그아웃되었습니다."},
                status=status.HTTP_205_RESET_CONTENT,
            )

            # 로그인시 설정했던 쿠키와 동일하게 해야 함
            response.set_cookie(
                "refresh_token",
                value="",  # 값을 비워줌
                httponly=True,
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                samesite="Lax",
                max_age=0,  # 0초 -> 즉시 만료
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
            )
            return response

        except TokenError:
            return Response(
                {"error": "유효하지 않거나 만료된 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"로그아웃 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # 유저 프로필 조회, 수정, 삭제 API


class UserProfileAPIView(APIView):
    # View 권한 검사
    permission_classes = (IsOwner,)

    @extend_schema(
        responses={
            200: {"message": "프로필이 조회되었습니다."},
            500: {"message": "서버에 문제가 있습니다."},
        }
    )
    # 특정 유저 조회
    def get(self, request, pk):

        user_to_retrieve = get_object_or_404(User, pk=pk)

        self.check_object_permissions(request, user_to_retrieve)

        serializer = UserSerializer(user_to_retrieve)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserSerializer,
        responses={
            200: {"message": "프로필이 성공적으로 수정되었습니다."},
            400: UserSerializer,
        },
    )
    # 특정 유저 업데이트
    def patch(self, request, pk):

        user_to_update = get_object_or_404(User, pk=pk)

        self.check_object_permissions(request, user_to_update)

        # partial=True는 PATCH 요청에 필수, 일부 필드만 검증
        serializer = UserSerializer(user_to_update, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None, 500: {"message": "서버에 문제가 있습니다."}})
    # 특정 유저 삭제
    def delete(self, request, pk):
        user_to_delete = get_object_or_404(User, pk=pk)

        self.check_object_permissions(request, user_to_delete)

        user_to_delete.delete()
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
