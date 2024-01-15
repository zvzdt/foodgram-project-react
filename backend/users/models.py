from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='имя пользователя',
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='ваше имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия'
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='email aдрес'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribes'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='user_cannot_follow_self'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
