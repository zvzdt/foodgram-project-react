from django.contrib import admin
from .models import Ingredients, Recipe, Tags

admin.site.register(Ingredients)
admin.site.register(Recipe)
admin.site.register(Tags)
