from django.contrib.auth.models import (
    PermissionsMixin, # is_superuser 와 같은 필드 및 권한 관련 기능
    AbstractBaseUser, # 비밀번호 해싱 및 인증 로직 기능
    BaseUserManager, # 사용자 정의 공통 모델, 타임 스탬프 필드를 포함하도록 커스텀
)
from django.db import models
from django.utils import timezone

# 유저 관리자 생성 클래스
class CustomUserManager(BaseUserManager):
    # 일반 유저 생성 시
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 주소를 입력해주세요.")
        email = self.normalize_email(email) # 이메일 표준화
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # 비밀번호 해싱
        user.save(using=self._db) # 현재 사용중인 DB에 저장
        return user

    # 관리자 생성 시
    def create_superuser(self, email, password=None, **extra_fields):
        # 관리자 기본 값 지정
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("superuser는 is_staff=True 이어야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("superuser는 is_superuser=True 이어야 합니다.")

        # 검증 끝낸 후 유저 인스턴스 생성
        return self.create_user(email, password, **extra_fields)

# 유저 생성 클래스
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="이메일 주소",  # 한국어 UI 제공
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(
        max_length=50,
        verbose_name="별명",
        unique=True,
    )
    name = models.CharField(max_length=50,verbose_name="성함")
    phone_number = models.CharField(max_length=15,verbose_name="전화번호")
    last_login = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # 생성일 - auto_now_add : 처음 생성될 때 현재 시간
    created_at = models.DateTimeField(auto_now_add=True)
    # 변경일 - auto_now : 저장될 때마다 현재 시간
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    # 사용자 식별자로 사용할 필드 지정
    USERNAME_FIELD = "email"
    # superuser 생성 시 필수 요구 사항
    REQUIRED_FIELDS = ["nickname", "name", "phone_number"]

    # 사용자 인스턴스를 문자열로 표현할 때 이메일로 반환
    def __str__(self):
        return self.email

    # 한국어 UI -> 가독성 향상
    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"

