from django.db.models import Q, Sum
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.filters import RecipeFilter
from recipes.models import (FavoriteList, Ingredients, Recipe,
                            RecipeIngredients, ShoppingCart, Tags)
from users.models import Subscription, User

from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientsSerializer, RecipeCreateSerializer,
                          RecipeFavoriteSerializer, RecipeSerializer,
                          ShortCutRecipeSerializer, SubscriptionSerializer,
                          TagsSerializer, UserSerializer)


class UserViewSet(UserViewSet):
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
                return Response('Вы уже подписаны',
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response('Нелья подписаться на себя',
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                author, context={'request': request})
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response('Вы отписались',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Вы не подписаны на этого пользователя',
                            status=status.HTTP_400_BAD_REQUEST)

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
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    ordering_fields = ('name', )
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        ingredient_name = self.request.GET.get('name')
        if ingredient_name:
            filters = Q(name__istartswith=ingredient_name)
            queryset = queryset.filter(filters).annotate(
                lower_name=Lower('name')).order_by('lower_name')
        return queryset


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
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
            return Response({'error': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        if list_model.objects.filter(user=user,
                                     recipe=recipe).exists():
            raise exceptions.ValidationError(
                'Рецепт уже добавлен в список.')
        list_model.objects.create(user=user, recipe=recipe)
        serializer = list_serializer(recipe,
                                     context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def remove_recipe_from_list(self, request, list_model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        try:
            list_item = list_model.objects.get(user=user,
                                               recipe=recipe)
            list_item.delete()
            return Response({'detail': 'Рецепт удален.'},
                            status=status.HTTP_204_NO_CONTENT)
        except list_model.DoesNotExist:
            raise exceptions.ValidationError(
                'Рецепт не найден в списке.')

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe_to_list(
                request,
                FavoriteList,
                RecipeFavoriteSerializer
            )
        elif request.method == 'DELETE':
            return self.remove_recipe_from_list(
                request,
                FavoriteList
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
            recipe__in=recipes).values('ingredients').annotate(
            amount=Sum('amount'))
        text = 'Список покупок:\n'
        for item in recipeingredients_list:
            ingredient = Ingredients.objects.get(pk=item['ingredients'])
            amount = item['amount']
            text += (f'{ingredient.name}, {amount} '
                     f'{ingredient.measurement_unit}\n'
                     )
        response = HttpResponse(text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt')
        return response
