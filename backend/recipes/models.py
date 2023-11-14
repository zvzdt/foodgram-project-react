from django.contrib.auth import get_user_model
from django.db import models
from colorfield.fields import ColorField

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(
        'ингредиенты',
        blank=False,
        max_length=50
        )
    quantity = models.FloatField(
        'количество',
        blank=False
    )
    units = models.CharField(
        'единица измерения',
        blank=False,
        max_length=10
        )
    
    class Meta:
        verbose_name='Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    title = models.CharField(
        'имя тэга',
        max_length=50, 
        blank=False, 
        unique=True
        )
    color = ColorField(
        'цвет',
        format='hex'
        )
    slug = models.SlugField(
        max_length=50, 
        blank=False, 
        unique=True
        )
    
    class Meta:    
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(      
        User, 
        on_delete=models.CASCADE,
        verbose_name='автор'
        )
    pub_date = models.DateTimeField(
        'Дата публикации', 
        auto_now_add=True
        )
    title = models.CharField(
        'название',
        blank=False, 
        max_length=50
        )
    image = models.ImageField(
        'фото',
        upload_to='recipes/images/',
        blank=False
        )
    description = models.TextField(
        'описание',
        blank=False
    )
    ingredients = models.ForeignKey(
        Ingredient, 
        related_name='ingredient', 
        on_delete=models.CASCADE,
        verbose_name='ингредиенты'
    )
    tag = models.ForeignKey(
        Tag, 
        related_name='tags', 
        on_delete=models.CASCADE,
        verbose_name='тэг'
        )
    cooking_time = models.DurationField(
        'время приготовления',
        blank=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name



