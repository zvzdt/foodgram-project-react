from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet, filters

from .models import Ingredients


class IngredientsFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredients
        fields = ['name']

    def filter_name(self, queryset, name, value):
        """Метод возвращает кверисет с заданным именем ингредиента."""
        return queryset.filter(
        Q(name__istartswith=value) | Q(name__icontains=' ' + value)
    ).order_by('name')
