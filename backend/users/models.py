from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
