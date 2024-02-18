from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from .validators import validate_me

MAX_LENGTH = 256


class User(AbstractUser):
    """Модель юзера."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name',
                       'last_name',
                       'username')

    email = models.EmailField(max_length=MAX_LENGTH,
                              verbose_name='email',
                              unique=True)
    username = models.CharField(max_length=MAX_LENGTH,
                                unique=True,
                                validators=[UnicodeUsernameValidator(),
                                            validate_me])
    first_name = models.CharField(max_length=MAX_LENGTH)

    last_name = models.CharField(max_length=MAX_LENGTH)

    def __str__(self) -> str:
        return f"{self.username}"


class Subscribe(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author')

    def __str__(self) -> str:
        return f"{self.user.username}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='author_user'
            )
        ]
