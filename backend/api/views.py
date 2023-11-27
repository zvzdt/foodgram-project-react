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
from users.models import User
from .serializers import (
    ChangePasswordSerializer, UserCreateSerializer, UserSerializer,
    IngredientsSerializer, RecipeSerializer, RecipeIngredientsSerializer,
    TagsSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def profile(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserPasswordViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['put'])
    def change_password(self, request):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.validated_data.get(
                'current_password')
            new_password = serializer.validated_data.get('new_password')
            if not user.check_password(current_password):
                return Response({'detail': 'wrong password'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'password updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = (AllowAny, )


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
