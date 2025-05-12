from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс модели кастомного пользователя."""
    avatar = models.ImageField(
        verbose_name='Avatar',
        upload_to='users/avatars',
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'объект "Пользователь"'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Subscription(models.Model):
    """Класс модели подписки."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    blogger = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )

    def __str__(self):
        return f'{self.user} подписан на {self.blogger}'

    class Meta:
        verbose_name = 'объект "Подписка"'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('blogger', 'user'), name='unique_subscription'),
        )
        ordering = ('user', 'blogger')
