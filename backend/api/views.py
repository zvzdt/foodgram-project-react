from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import Ingredients, Recipe, RecipeIngredients, Tags
from recipes.filters import IngredientSearchFilter
from users.models import User
from .serializers import (UserSerializer, IngredientsSerializer,
                          RecipeSerializer, RecipeIngredientsSerializer, TagsSerializer)
#from .permissions import IsOwnerOrReadOnly


class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny, )
    filter_backends = [IngredientSearchFilter]

    # @action(detail=False, permission_classes=[IsAuthenticated])
    # def action(self, request):
    #     raise NotImplementedError(777)



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