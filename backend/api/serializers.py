from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredients, Recipe, RecipeIngredients, Tags
from users.models import User, Subscription


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
    

class UserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )
    
    def validate(self, attrs):
        required_fields = ['username', 'last_name', 'email', 'password']
        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError(f'{field.capitalize()} обязательное поле')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

 

class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipe_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
    )
    is_subscribed = serializers.SerializerMethodField()

    def validate(self, obj):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!'
            )
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        return obj

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()

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

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipe_count')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = ('id',)


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'
        read_only_fields = ('id',)



class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_units = serializers.ReadOnlyField(
        source='ingredients.measurement_units')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_units', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    image = Base64ImageField(allow_null=False)

    ingredients = RecipeIngredientsSerializer(
        source='ingredient',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()


class ShortCutRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
