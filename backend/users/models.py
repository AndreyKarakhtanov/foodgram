from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Класс модели кастомного пользователя."""
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    avatar = models.ImageField(
        verbose_name='Avatar',
        upload_to='users/avatars',
        null=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

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
            models.CheckConstraint(
                check=~Q(blogger=F('user')),
                name='refuse_self_subscription'
            ),
            models.UniqueConstraint(
                fields=('blogger', 'user'), name='unique_subscription'),
        )
        ordering = ('user', 'blogger')

    def clean(self):
        if self.user == self.blogger:
            raise ValidationError('Попытка подписки на себя отклонена.')
