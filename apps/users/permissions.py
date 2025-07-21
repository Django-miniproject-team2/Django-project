from rest_framework import permissions

# 객체 소유자에게만 권한 부여
class IsOwner(permissions.BasePermission):

    message = "자신의 프로필에만 접근/수정/삭제할 수 있습니다."

    # has_permission: 뷰 레벨 권한
    # has_object_permission: 객체 레벨 권한
    # APIView에서는 get_object()가 없으므로, has_object_permission을 직접 호출해야 함.

    def has_permission(self, request, view):
        # GET, PUT, PATCH, DELETE 요청 시에는 인증된 사용자만 view에 접근 허용
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 관리자는 모든 객체에 접근 가능해야 함.
        if request.user.is_superuser:
            return True
        # 요청하는 사용자가 해당 객체의 소유자인지 확인
        # obj는 User 모델 인스턴스이므로, obj.pk와 request.user.pk를 비교
        return obj == request.user