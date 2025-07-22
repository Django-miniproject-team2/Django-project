from django.contrib import admin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "nickname",
        "name",
        "phone_number",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ["email", "nickname", "phone_number"]
    list_filter = ("is_active", "is_staff")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            form.base_fields["is_superuser"].disabled = True
        return form