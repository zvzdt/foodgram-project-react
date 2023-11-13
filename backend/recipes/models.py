from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=50)
    quantity = models.FloatField()
    units = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Tag(models.Model):
    title = models.CharField(max_length=20)
    color = models.CharField(max_length=10)
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None)
    description = models.TextField()
    ingredients = models.ForeignKey(
        Ingredient, related_name='ingredient', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(Tag, related_name='tags', on_delete=models.CASCADE)
    cooking_time = models.DurationField()

    def __str__(self):
        return self.name



