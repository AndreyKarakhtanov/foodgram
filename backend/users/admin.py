from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar',)}),
)


class CustomUserAdmin(UserAdmin):
    """Админка для кастомного пользователя."""
    readonly_fields = ('username', 'email', 'first_name', 'last_name',
                       'is_staff', 'is_superuser',
                       'user_permissions', 'groups',
                       'last_login', 'date_joined', 'avatar')
    search_fields = (
        'email',
        'username',
    )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        elif obj.username == request.user.username:
            return ('is_staff', 'is_superuser', 'groups', 'user_permissions',
                    'last_login', 'date_joined')
        if obj.is_superuser and request.user.is_staff:
            return list(self.readonly_fields).append('is_active')
        return self.readonly_fields


class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок."""
    list_display = (
        'user',
        'blogger',
    )


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, CustomUserAdmin)
