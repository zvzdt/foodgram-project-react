import re

from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.validators import validate_amount
from recipes.models import (FavoriteList, Ingredients, Recipe,
                            RecipeIngredients, ShoppingCart, Tags)
from users.models import Subscription, User


class UserSerializer(UserSerializer):
    """Сериализатор списка пользователей"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',)
        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password')

    def validate(self, attrs):
        required_fields = ['username', 'last_name', 'email', 'password']
        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError(
                    f'{field.capitalize()} обязательное поле')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок"""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False

    def get_recipe(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serialized_recipes = ShortCutRecipeSerializer(recipes, many=True).data
        return serialized_recipes

    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""

    class Meta:
        model = Tags
        fields = '__all__'
        read_only_fields = ('id',)


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов с количеством"""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания ингредиентов для рецепта"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=[validate_amount,
                    MinValueValidator(1)], write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор получения рецептов"""
    name = serializers.ReadOnlyField()
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='recipeingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('id', 'author', 'name', 'is_favorited',
                            'is_in_shopping_cart')
        
    def get_favorited(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return FavoriteList.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False

    def get_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True)
    ingredients = RecipeIngredientsCreateSerializer(
        many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time', 'author')
        read_only_fields = ('author',)

    def validate_name(self, value):
        if re.match(r'^[0-9\W]+$', value):
            raise serializers.ValidationError(
                'Название рецепта не может состоять только из цифр и знаков.'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Добавьте тег.')
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Добавьте ингредиент.')
        ingredients = [item['id'] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'Такой ингредиент уже есть.'
                )
            if not Ingredients.objects.filter(pk=ingredient).first():
                raise serializers.ValidationError('Ингредиент не найден.')
        return value

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Добавьте изображение.')
        return image

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            ingredient_id = ingredient_data['id']
            if ingredient_id:
                ingredient = get_object_or_404(Ingredients, pk=ingredient_id)
                RecipeIngredients.objects.create(
                    recipe=recipe,
                    ingredients=ingredient,
                    amount=amount)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' not in validated_data or 'tags' not in validated_data:
            raise serializers.ValidationError('Поле не может быть пустым.')
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.set(validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Список рецептов в избранном."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShortCutRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор коротокого отображения рецепта"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
