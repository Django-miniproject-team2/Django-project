from django.urls import path

from .views import JWTLoginView, JWTLogoutView, UserProfileAPIView, UserRegisterView

app_name = "users"

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("auth/login/", JWTLoginView.as_view(), name="jwt_login"),
    path("auth/logout/", JWTLogoutView.as_view(), name="jwt_logout"),
    path("<int:pk>/", UserProfileAPIView.as_view(), name="user_profile"),
]
