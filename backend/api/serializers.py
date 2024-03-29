import re

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from api.constants import MIN_AMOUNT, MIN_COOKING_TIME
from recipes.models import (
    Favorite, Ingredient, RecipeIngredient,
    Recipe, ShoppingCart, Tag
)
from users.models import Follow, User


class UserReadSerializer(UserSerializer):
    """Серилизатор вывода пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        return (
            user
            and user.is_authenticated
            and obj.following.filter(user=user).exists()
        )


class AddUserSerializer(UserCreateSerializer):
    """Серилизатор создания пользователей."""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate_username(self, value):
        """Проверка username-символов."""

        if not re.match(r'^[\w.@+-]+$', value):
            raise ValidationError('Username содержит недопустимые символы')
        return value


class SetNewPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)


class IngredientSerializer(serializers.ModelSerializer):
    """Серилизатор работы с ингридиентами."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Серилизатор работы с тэгами."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShortRecipesShowSerializer(serializers.ModelSerializer):
    """Сериализатор краткого вывода рецептов."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class GetRecipeIngredienterializer(serializers.ModelSerializer):
    """Сериализатор получения ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Получение списка рецептов."""

    author = UserReadSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    ingredients = GetRecipeIngredienterializer(
        many=True, source='recipe_ingredients',
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class AddRecipeIngredienterializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """
        Проверяет, что количество ингредиента больше минимального значения.
        """
        if value <= MIN_AMOUNT:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше нуля.')
        return value


class RecipeCreateAndUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = AddRecipeIngredienterializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        """
        Проверка корректности времени
        приготовления рецепта (> MIN_COOKING_TIME).
        """

        if value <= MIN_COOKING_TIME:
            raise ValidationError(
                f'Время приготовления должно быть больше {MIN_COOKING_TIME}.'
            )
        return value

    def add_ingredients(self, recipe, ingredients_data):
        """Добавление ингредиентов в рецепт."""
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['id']
            amount = ingredient_data['amount']
            recipe_ingredient = RecipeIngredient(
                recipe=recipe, ingredient=ingredient, amount=amount,
            )
            ingredients.append(recipe_ingredient)

        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.add_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки пользователя."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def create(self, validated_data):
        user = validated_data['user']
        author = validated_data['author']

        Follow.objects.create(user=user, author=author)
        return {'success': True}

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        if user.following.filter(author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data


class SubscriptionShowSerializer(UserReadSerializer):
    """Сериализатор просмотра подписок пользователя."""

    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta(UserReadSerializer):
        model = User
        fields = UserReadSerializer.Meta.fields + (
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = self._get_recipes_limit(request)
        recipes = obj.recipes.all()[:recipes_limit]
        context = {'request': request}
        return ShortRecipesShowSerializer(
            recipes, many=True, context=context).data

    def _get_recipes_limit(self, request):
        recipes_limit = request.query_params.get('recipes_limit')
        try:
            return int(recipes_limit) if recipes_limit else None
        except ValueError:
            return None


class BaseItemOperationSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для операций с элементами списка."""

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в этот список.'
            )
        return data

    def create(self, validated_data):
        recipe = validated_data['recipe']
        user = validated_data['user']
        return self.Meta.model.objects.create(user=user, recipe=recipe)

    def delete(self, data):
        user = data['user']
        recipe = data['recipe']
        return get_object_or_404(self.Meta.model,
                                 user=user,
                                 recipe=recipe).delete()


class AddFavoriteRecipeSerializer(BaseItemOperationSerializer):
    """Сериализатор добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        item_model = Recipe
        item_serializer = ShortRecipesShowSerializer
        fields = ('user', 'recipe')


class ShoppingCartSerializer(BaseItemOperationSerializer):
    """Сериализатор добавления и удаления рецептов из корзины покупок."""

    class Meta:
        model = ShoppingCart
        item_model = Recipe
        item_serializer = ShortRecipesShowSerializer
        fields = ('user', 'recipe')
