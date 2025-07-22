from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},  # 비밀번호 입력 필드 표시
        min_length=10,  # 최소 10자
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=10,
    )

    class Meta:
        model = User
        fields = ("email", "nickname", "name", "phone_number", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
            "nickname": {"required": True},
            "name": {"required": True},
        }

    def validate(self, data):
        # 비밀번호와 비밀번호 확인이 일치하는지 검증
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "두 비밀번호가 일치하지 않습니다."}
            )
        phone_number = data["phone_number"]
        if not phone_number.isdigit():
            raise serializers.ValidationError("휴대폰 번호는 숫자만 입력해야 합니다.")

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("이미 등록된 휴대폰 번호입니다.")

        return data

    def create(self, validated_data):
        # 비밀번호2는 저장할 필요 없이 제거
        validated_data.pop("password2")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname"),
            name=validated_data.get("name"),
            phone_number=validated_data.get("phone_number"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "name",
            "nickname",
            "phone_number",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise serializers.ValidationError("이메일을 입력하세요.")
        if not password:
            raise serializers.ValidationError("비밀번호를 입력하세요.")

        user = authenticate(self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("잘못된 이메일 또는 비밀번호입니다.")

        data["user"] = user
        return data
