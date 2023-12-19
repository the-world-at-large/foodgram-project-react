import re

from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import (FavoritesList, Ingredients, RecipeIngredients,
                            Recipes, ShoppingList, Tags)
from rest_framework import serializers
from users.models import Follow, User


class UserReadSerializer(UserSerializer):
    """Серилизатор вывода пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


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

    def validate_amount(self, value):
        """Проверка корректности количества ингридиентов (> 0)."""

        if value <= 0:
            raise ValidationError(
                'Количество ингредиентов должно быть больше 0'
            )
        return value


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
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorite(self, obj):
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
        shopping_list = ShoppingList.objects.filter(
            user=user, recipe=obj,
        )
        return shopping_list.exists()


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """Проверка корректности количества ингредиентов (> 0)."""

        if value <= 0:
            raise ValidationError(
                'Количество ингредиента должно быть больше 0.'
            )
        return value

    def validate(self, attrs):
        """Проверка корректности добавления ингридиентов в рецепт."""

        request = self.context.get('request')
        recipe_id = request.GET.get('recipe')
        ingredient_id = attrs['ingredient']['id']
        existing_ingredients = RecipeIngredients.objects.filter(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id
        )
        if existing_ingredients.exists():
            raise ValidationError('Ингредиент уже добавлен в рецепт.')
        return attrs


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
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient']['id']
            amount = ingredient_data['amount']
            ingredient = Ingredients.objects.get(id=ingredient_id)
            if RecipeIngredients.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists():
                amount += F('amount')
            recipe_ingredient = RecipeIngredients(
                recipe=recipe, ingredient=ingredient, amount=amount
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


class FavoriteRecipesListSerializer(serializers.Serializer):
    """Сериализатор добавления рецепта в избранное."""

    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if FavoritesList.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipes, pk=validated_data['id'])
        user = self.context['request'].user
        FavoritesList.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipesShowSerializer(recipe)
        return serializer.data


class SubscriptionsShowSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра списка подписок пользователя."""

    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = self.context['request'].user
        if not request or not user.is_authenticated:
            return False
        return obj.following.filter(user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return ShortRecipesShowSerializer(recipes, many=True,
                                          context=context).data


class CreateAndDeleteSubscriptionsSerializer(serializers.Serializer):
    """Сериализатор добавления и удаления подписок пользователя."""

    def validate(self, data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=self.context['id'])
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=validated_data['id'])
        Follow.objects.create(user=user, author=author)
        serializer = CreateAndDeleteSubscriptionsSerializer(
            author, context={'request': self.context.get('request')},
        )
        return serializer.data


class ShoppingCartSerializer(serializers.Serializer):
    """Сериализатор добавления и удаления рецептов из корзины покупок."""

    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if ShoppingList.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок.'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipes, pk=validated_data['id'])
        ShoppingList.objects.create(
            user=self.context['request'].user,
            recipe=recipe
        )
        serializer = ShortRecipesShowSerializer(recipe)
        return serializer.data
