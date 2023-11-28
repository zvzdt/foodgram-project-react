from rest_framework.filters import SearchFilter
from django_filters.rest_framework import filters

from recipes.models import Ingredients


class IngredientSearchFilter(SearchFilter):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name']