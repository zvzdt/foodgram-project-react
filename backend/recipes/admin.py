from django.contrib import admin

from .models import (FavoriteList, Ingredients, Recipe, RecipeIngredients,
                     ShoppingCart, Tags)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    fields = ['ingredients', 'amount']
    list_display = ['ingredients', 'amount']


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'display_tags', 'favorite')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    readonly_fields = ('favorite',)
    fields = ('image',
              ('name', 'author'),
              'text',
              ('tags', 'cooking_time'),
              'favorite')

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'

    def favorite(self, obj):
        return obj.favorite.count()
    favorite.short_description = 'Раз в избранном'


class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(FavoriteList, FavoriteListAdmin)
