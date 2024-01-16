from api.filters import RecipeFilter
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredients, ShoppingCart, Tag)
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientsSerializer, RecipeCreateSerializer,
                          RecipeFavoriteSerializer, RecipeSerializer,
                          ShortCutRecipeSerializer, SubscriptionSerializer,
                          TagsSerializer, UserSerializer)


class UserViewSet(UserViewSet):
    """Класс работы с пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny, )

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({"errors": 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({"errors": 'Нелья подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                author, context={'request': request})
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = SubscriptionSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка ингредиентов."""
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    ordering_fields = ('name', )
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Получпение списка тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly, )
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe_to_list(self, request, list_model,
                           list_serializer):
        user = request.user
        recipe_id = self.kwargs.get('pk')
        recipe = Recipe.objects.filter(id=recipe_id).first()
        if not recipe:
            return Response({"errors": 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        if list_model.objects.filter(user=user,
                                     recipe=recipe).exists():
            raise exceptions.ValidationError(
                {"errors": 'Рецепт уже добавлен в список'})
        list_model.objects.create(user=user, recipe=recipe)
        serializer = list_serializer(recipe,
                                     context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def remove_recipe_from_list(self, request, list_model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        list_item = list_model.objects.filter(user=user, recipe=recipe)
        if list_item.exists():
            list_item.delete()
            return Response('Рецепт удален.',
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"errors": 'Рецепт не найден в списке'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe_to_list(
                request,
                Favorite,
                RecipeFavoriteSerializer
            )
        elif request.method == 'DELETE':
            return self.remove_recipe_from_list(
                request,
                Favorite
            )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe_to_list(
                request,
                ShoppingCart,
                ShortCutRecipeSerializer
            )
        elif request.method == 'DELETE':
            return self.remove_recipe_from_list(
                request,
                ShoppingCart
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        recipeingredients_list = RecipeIngredients.objects.filter(
            recipe__in=recipes).values('ingredient').annotate(
            amount=Sum('amount'))
        text = 'Список покупок:\n'
        for item in recipeingredients_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            text += (f'{ingredient.name}, {amount} '
                     f'{ingredient.measurement_unit}\n'
                     )
        response = HttpResponse(text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt')
        return response
