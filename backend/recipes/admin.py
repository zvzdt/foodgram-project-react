from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    fields = ['ingredient', 'amount']
    list_display = ['ingredient', 'amount']


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline,]
    list_display = ('name', 'author', 'display_tags', 'favorite')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    readonly_fields = ('favorite',)
    fields = ('image', 'name', 'author', 'text',
              'tags', 'cooking_time', 'favorite')

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'

    def favorite(self, obj):
        return obj.favorite
    favorite.short_description = 'В избранном'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
