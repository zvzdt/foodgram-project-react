from colorfield.fields import ColorField
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Tags(models.Model):
    name = models.CharField(
        verbose_name='имя тэга',
        max_length=200,
        blank=False,
    )
    color = ColorField(
        verbose_name='цвет',
        format='hex',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(r'^[-a-zA-Z0-9_]+$'),
        ],
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
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit'
            )
        ]

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
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='ингредиенты',
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


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(Ingredients,
                                    on_delete=models.CASCADE,
                                    related_name='recipeingredients',
                                    verbose_name='Ингредиенты')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MaxValueValidator(2000), MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        # ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} {self.ingredients}'


class FavoriteList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_shoppingcart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
