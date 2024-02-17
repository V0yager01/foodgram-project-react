from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from .validators import validate_me


class User(AbstractUser):
    """Модель юзера."""

    email = models.EmailField(max_length=256,
                              verbose_name='email')
    username = models.CharField(max_length=256,
                                unique=True,
                                validators=[UnicodeUsernameValidator(),
                                            validate_me])
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

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
