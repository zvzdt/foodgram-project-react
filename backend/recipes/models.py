from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField

User = get_user_model()

class Tags(models.Model):
    name = models.CharField(
        verbose_name='имя тэга',
        max_length=200,
        blank=False, 
        unique=True
        )
    color = ColorField(
        verbose_name='цвет',
        format='hex'
        )
    slug = models.SlugField(
        max_length=200, 
        unique=True, 
        null=True
        )
    class Meta:    
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=200,
        blank=False
        )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=200,
        blank=False
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        verbose_name='ингредиенты',
        blank=False
        )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes', 
        verbose_name='теги'
        )
    image = models.ImageField(
        verbose_name='картинка'
        )
    name = models.CharField(
        verbose_name='название',
        max_length=200,
        blank=False
        )
    text = models.TextField(
        verbose_name='описание',
        blank=False
        )
    cooking_time = models.PositiveIntegerField(
        verbose_name='время приготовления (в минутах)',
        blank=False
        )

    class Meta:    
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
