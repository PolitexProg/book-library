from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from users.models import FriendshipRequest

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin for CustomUser that exposes profile picture upload and preview."""

    fieldsets = tuple(
        list(UserAdmin.fieldsets)
        + [
            ("Profile", {"fields": ("profile_picture",)}),
        ]
    )

    add_fieldsets = tuple(
        list(UserAdmin.add_fieldsets)
        + [
            ("Profile", {"fields": ("profile_picture",)}),
        ]
    )

    list_display = tuple(list(UserAdmin.list_display) + ["profile_picture_tag"])

    def profile_picture_tag(self, obj):
        if getattr(obj, "profile_picture", None):
            try:
                url = obj.profile_picture.url
            except Exception:
                return ""
            return format_html(
                '<img src="{}" style="height:40px;border-radius:50%;" />', url
            )
        return ""

    profile_picture_tag.short_description = "Avatar"


@admin.register(FriendshipRequest)
class FriendshipRequestAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("from_user__username", "to_user__username")
