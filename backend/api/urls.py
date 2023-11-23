from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from .views import (ChangePasswordViewSet, UserCreateViewSet,
                    UsersListViewSet, UserProfileViewSet, IngredientsViewSet,
                    RecipeViewSet, TagsViewSet)


app_name = 'api'


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UsersListViewSet, basename='users')
router_v1.register(r'users', UserCreateViewSet, basename='user-create')
router_v1.register(r'users', UserProfileViewSet, basename='user-profile')
router_v1.register(r'users', ChangePasswordViewSet, basename='change-password')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
