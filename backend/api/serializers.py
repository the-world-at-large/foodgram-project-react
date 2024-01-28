import re

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredients, RecipeIngredients,
    Recipes, ShoppingCart, Tags
)
from users.models import Follow, User


class UserReadSerializer(UserSerializer):
    """Серилизатор вывода пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        return (
            user
            and user.is_authenticated
            and obj.following.filter(user=user).exists()
        )


class UserCreateSerializer(UserCreateSerializer):
    """Серилизатор создания пользователей."""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate_username(self, value):
        """Проверка username-символов."""

        if not re.match(r'^[\w.@+-]+$', value):
            raise ValidationError(
                'Username содержит недопустимые символы'
            )
        return value


class SetNewPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)


class IngredientsSerializer(serializers.ModelSerializer):
    """Серилизатор работы с ингридиентами."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    """Серилизатор работы с тэгами."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class ShortRecipesShowSerializer(serializers.ModelSerializer):
    """Сериализатор краткого вывода рецептов."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class GetRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор получения ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit',
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipesSerializer(serializers.ModelSerializer):
    """Получение списка рецептов."""

    author = UserReadSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    tags = TagsSerializer(
        many=True,
        read_only=True,
    )
    ingredients = GetRecipeIngredientsSerializer(
        many=True, source='recipe_ingredients',
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipes
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

        def to_representation(self, instance):
            request = self.context.get('request')
            user = (request.user if request
                    and request.user.is_authenticated else None)

            data = super().to_representation(instance)
            data['is_favorited'] = instance.is_favorited(user)
            data['is_in_shopping_cart'] = instance.is_in_shopping_cart(user)
            return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if not request or not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if not request or not user.is_authenticated:
            return False
        shopping_list = ShoppingCart.objects.filter(
            user=user, recipe=obj,
        )
        return shopping_list.exists()


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredients
        fields = ('id', 'amount')


class RecipeCreateAndUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tags.objects.all())
    ingredients = AddRecipeIngredientsSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipes
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        """Проверка корректности времени приготовления рецепта (> 0)."""

        if value <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0.'
            )
        return value

    def add_ingredients(self, recipe, ingredients_data):
        RecipeIngredients.objects.filter(recipe=recipe).delete()

        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient'].id
            amount = ingredient_data['amount']
            ingredient = Ingredients.objects.get(id=ingredient_id)
            recipe_ingredient = RecipeIngredients(
                recipe=recipe, ingredient=ingredient, amount=amount,
            )
            ingredients.append(recipe_ingredient)

        RecipeIngredients.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags')
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.add_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class SubscriptionsShowSerializer(UserSerializer):
    """Сериализатор просмотра списка подписок пользователя."""

    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = self.context['request'].user
        if not request or not user.is_authenticated:
            return False
        return obj.following.filter(user=user).exists()

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


class CreateAndDeleteSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор добавления и удаления подписок пользователя."""

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, data, obj):
        user = self.context['request'].user
        author_id = self.context['id']
        author = get_object_or_404(User, pk=author_id)

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        if obj.following.filter(user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )

        data['author'] = author
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        author = validated_data['author']

        subscription = Follow.objects.create(user=user, author=author)
        return subscription


class BaseItemOperationSerializer(serializers.Serializer):
    """Базовый сериализатор для операций с элементами списка."""

    def validate(self, data):
        item_id = self.context['item_id']
        user = self.context['request'].user
        if self.Meta.model.objects.filter(user=user, item_id=item_id).exists():
            raise serializers.ValidationError(
                'Этот объект уже есть в списке.'
            )
        return data

    def create(self, validated_data):
        item = get_object_or_404(self.Meta.item_model, pk=validated_data['id'])
        self.Meta.model.objects.create(
            user=self.context['request'].user,
            item=item
        )
        serializer = self.Meta.item_serializer(item)
        return serializer.data


class AddFavoriteRecipeSerializer(BaseItemOperationSerializer):
    """Сериализатор добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        item_model = Recipes
        item_serializer = ShortRecipesShowSerializer


class ShoppingCartSerializer(BaseItemOperationSerializer):
    """Сериализатор добавления и удаления рецептов из корзины покупок."""

    class Meta:
        model = ShoppingCart
        item_model = Recipes
        item_serializer = ShortRecipesShowSerializer
