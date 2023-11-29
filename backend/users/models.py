from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError

class User(AbstractUser):
    username = models.CharField(
        unique=True,
        blank=False,
        max_length=150,
        verbose_name='имя пользователя',
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='ваше имя'
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='фамилия'
    )
    email = models.EmailField( 
        unique=True,
        blank=False,
        max_length=254,
        verbose_name='email aдрес'
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
    )
    is_subscribed = models.ManyToManyField(
        to='self',
        through='Subscription',
        through_fields=('user', 'author'),
        related_name='is_following',
        symmetrical=False,
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
    

    def __str__(self):
        return f'{self.user} {self.author}'
