from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from rest_framework import viewsets, filters, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import Ingredients, Recipe, RecipeIngredients, Tags
from recipes.filters import IngredientSearchFilter
from users.models import User
from .serializers import (ChangePasswordSerializer, UserSerializer, IngredientsSerializer,
                          RecipeSerializer, RecipeIngredientsSerializer, TagsSerializer)
#from .permissions import IsOwnerOrReadOnly


# class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     serializer_class = UserSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def perform_create(self, serializer):
#         serializer.save()


# class UsersListViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = LimitOffsetPagination
#     permission_classes = (IsAuthenticatedOrReadOnly, )


# class CreateUserViewset(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny, )

#     def get_queryset(self):
#         return User.objects.all()
    
#     def perform_create(self, serializer):
#         serializer.save()

#     def perform_update(self, serializer):
#         serializer.save()


# class UserProfileViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = LimitOffsetPagination
#     permission_classes = (AllowAny, )


# class CurrentUserViewSet(viewsets.ModelViewSet):
#     serializer_class = UserSerializer

#     def get_queryset(self):
#         return User.objects.all()

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def perform_update(self, serializer):
#         if self.request.method == 'PATCH':
#             serializer.save(user=self.request.user)

#     def create(self, request,  *args, ** kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=201, headers=headers)

#     def update(self, request,  *args, ** kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=200, headers=headers)


class ChangePasswordViewSet(viewsets.ViewSet):
    serializer_class = ChangePasswordSerializer

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            current_password = serializer.data.get('current_password')
            new_password = serializer.data.get('new_password')
            user = request.user
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'current_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
        else:
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