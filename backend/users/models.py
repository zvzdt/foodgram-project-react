from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

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
        unique=True,
        blank=False,
        max_length=150,
        verbose_name='ваше имя'
    )
    last_name = models.CharField(
        unique=True,
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
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
