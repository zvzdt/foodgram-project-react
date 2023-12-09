from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet, filters

from .models import Ingredients, Recipe, Tags


class IngredientsFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    def filter_name(self, queryset, name, value):
        """Метод возвращает кверисет с заданным именем ингредиента."""
        return queryset.filter(
        Q(name__istartswith=value) | Q(name__icontains=' ' + value)
    ).order_by('name')
    
    
    class Meta:
        model = Ingredients
        fields = ['name']
        filterset_fields = {
            'name': ['istartswith', 'icontains', 'exact'],
        }



class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tags.objects.all())
    is_favorited = filters.BooleanFilter(method='get_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_filter')

    def get_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')