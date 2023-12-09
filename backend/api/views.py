from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.functions import Lower
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (
    viewsets, filters, mixins, status, exceptions
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny 
)

from recipes.models import (
    FavoriteList, Ingredients, Recipe, RecipeIngredients, ShoppingCart, Tags
)
from recipes.filters import IngredientsFilter, RecipeFilter
from users.models import User, Subscription
from .serializers import (
    UserSerializer, IngredientsSerializer, RecipeSerializer, RecipeCreateSerializer,
    RecipeFavoriteSerializer, SubscriptionSerializer, ShortCutRecipeSerializer, TagsSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


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
                return Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Невозможно подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(author, context={'request': request})
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого пользователя'},
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    search_fields = ['name__startswith']
    permission_classes = [AllowAny]
    pagination_class = None
    



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

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipeingredients__ingredients', 'tags')
        return recipes

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            if FavoriteList.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже добавен в избранное.')
            FavoriteList.objects.create(user=user, recipe=recipe)
            serializer = RecipeFavoriteSerializer(
                recipe,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favoriteslist = get_object_or_404(
                FavoriteList,
                user=user,
                recipe=recipe)
            favoriteslist.delete()
            return Response({'detail': 'Рецепт удален.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = self.request.user
        if request.method == 'POST':
            shoppinglist_recipe, created = ShoppingCart.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not created:
                raise exceptions.ValidationError(
                    'Рецепт уже в списке покупок.')
            serializer = RecipeSerializer(
                recipe,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
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