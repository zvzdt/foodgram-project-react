from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from .views import (UsersListViewSet, UserProfileViewSet, CurrentUserViewSet, IngredientsViewSet, 
                    RecipeViewSet, TagsViewSet) 


app_name = 'api'


router_v1 = routers.DefaultRouter()
router_v1.register('users', UsersListViewSet, basename='users')
router_v1.register(r'users/{id}/', UserProfileViewSet, basename='user_profile')
router_v1.register('users/me/', CurrentUserViewSet, basename='me')
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