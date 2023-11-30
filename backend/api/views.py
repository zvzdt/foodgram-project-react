from django.shortcuts import get_object_or_404
from rest_framework import (
    viewsets, filters, mixins, status, exceptions
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny 
)
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import (
    Ingredients, Recipe, RecipeIngredients, Tags
)
from recipes.filters import IngredientSearchFilter
from users.models import User, Subscription
from .serializers import (
    ChangePasswordSerializer, UserCreateSerializer, UserSerializer,
    IngredientsSerializer, RecipeSerializer, RecipeIngredientsSerializer,
    SubscriptionSerializer, TagsSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny, )

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль изменен'},
                        status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.is_following.all()
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = self.get_object()
        subscription = get_object_or_404(Subscription, user=request.user, author=author)

        if request.method == 'POST':
            if subscription is None:
                subscription = Subscription(user=request.user, author=author)
                subscription.full_clean()
                subscription.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if subscription is not None:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny, )
    filter_backends = [IngredientSearchFilter]

    @action(detail=False, permission_classes=[IsAuthenticated])
    def action(self, request):
        raise NotImplementedError(777)


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredients.objects.all()
    serializer_class = RecipeIngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


# class RecipeFilter(filters.FilterSet):
#     tags = filters.CharFilter(field_name='tags__name')

#     class Meta:
#         model = Recipe
#         fields = ['tags']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = LimitOffsetPagination
    # filter_backends = (filters.DjangoDilterBackend,)
    # filterset_class = RecipeFilter
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['post'])
    def create_recipe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    @action(detail=True, methods=['patch'])
    def update_recipe(self, request, pk=None):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    
    @action(detail=True, methods=['delete'])
    def delete_recipe(self, request, pk=None):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



