from django.contrib import admin
from .models import Ingredients, Recipe, RecipeIngredients, Tags


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    fields = ['ingredients', 'amount']
    list_display = ['ingredients', 'amount']

class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'cooking_time']
    inlines = [RecipeIngredientsInline]


admin.site.register(Ingredients)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tags)
admin.site.register(RecipeIngredients)
