from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение позволяет автору редактировать/удалять объекты,
    а всем остальным пользователям — только чтение.
    """
    def has_object_permission(self, request, view, obj):

        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)
