from django.contrib import admin

from .models import Ingredient, Tag, Recipe, User

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
