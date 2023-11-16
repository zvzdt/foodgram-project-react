from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(
        unique=True,
        blank=False,
        max_length=200,
        verbose_name='имя пользователя'
    )
    first_name = models.CharField(
        unique=True,
        blank=False,
        max_length=200,
        verbose_name='ваше имя'
    )
    last_name = models.CharField(
        unique=True,
        blank=False,
        max_length=200,
        verbose_name='фамилия'
    )
    email = models.EmailField( 
        unique=True,
        blank=False,
        max_length=200,
        verbose_name='email aдрес'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
