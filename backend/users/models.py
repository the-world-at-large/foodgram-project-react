from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from users.constants import (
    MAX_LENGTH_USERNAME, MAX_LENGTH_FIRST_NAME, MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_EMAIL, MAX_LENGTH_PASSWORD,
)


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_FIRST_NAME,
        blank=False,
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_LAST_NAME,
        blank=False,
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        blank=False,
        unique=True,)
    password = models.CharField(
        max_length=MAX_LENGTH_PASSWORD,
        blank=False,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_following',
            ),
        ]
