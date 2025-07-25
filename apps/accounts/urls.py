from django.urls import path

from .views import AccountDetailView, AccountListCreateView

urlpatterns = [
    path("", AccountListCreateView.as_view(), name="account-list-create"),
    path("<int:pk>/", AccountDetailView.as_view(), name="account-detail"),
]
