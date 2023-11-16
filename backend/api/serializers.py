import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
#from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer

from recipes.models import Ingredients, Recipe, Tags, User


class CustomUserSerializer(UserSerializer):
    
    class Meta:
        model = User
        fields  = ('email', 'id', 'username', 
                   'first_name', 'last_name')

class IngredientsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    

class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsSerializer(read_only=True, many=True)
    tags = TagsSerializer(read_only=True, many=True)
    image = Base64ImageField(allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id',)
