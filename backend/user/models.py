from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from constants.constants import (MAX_EMAIL_LENGTH,
                                 MAX_FIRST_NAME_LENGTH,
                                 MAX_LAST_NAME_LENGTH,
                                 MAX_USERNAME_LENGTH)

from .validators import validate_me


class User(AbstractUser):
    """Модель юзера."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name',
                       'last_name',
                       'username')

    email = models.EmailField(max_length=MAX_EMAIL_LENGTH,
                              verbose_name='email',
                              unique=True)
    username = models.CharField(max_length=MAX_USERNAME_LENGTH,
                                unique=True,
                                validators=[UnicodeUsernameValidator(),
                                            validate_me])
    first_name = models.CharField(max_length=MAX_FIRST_NAME_LENGTH)

    last_name = models.CharField(max_length=MAX_LAST_NAME_LENGTH)

    class Meta:
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.username}'


class Subscribe(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author')

    def __str__(self) -> str:
        return f'{self.user.username}'

    class Meta:
        verbose_name = 'Подписка',
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='author_user'
            )
        ]
