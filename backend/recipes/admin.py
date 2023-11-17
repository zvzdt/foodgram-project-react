from django.contrib import admin
from .models import Ingredients, Recipe, RecipeIngredients, Tags

admin.site.register(Ingredients)
admin.site.register(Recipe)
admin.site.register(RecipeIngredients)
admin.site.register(Tags)
