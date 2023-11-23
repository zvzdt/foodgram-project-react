from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from .views import (ChangePasswordViewSet, UserCreateViewSet,
                    UsersListViewSet, UserProfileViewSet, IngredientsViewSet,
                    RecipeViewSet, TagsViewSet)


app_name = 'api'


router = routers.DefaultRouter()
router.register(r'users', UsersListViewSet, basename='users-list')
router.register(r'users-create', UserCreateViewSet, basename='user-create')
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')
router.register(r'change-password', ChangePasswordViewSet, basename='change-password')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
