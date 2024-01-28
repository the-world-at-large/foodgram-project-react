from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from recipes.models import Ingredients, Recipes, Tags

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """Фильтрация ингредиентов по их названию."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтрация по избранному, автору, списку покупок и тегам."""

    author = filters.ModelChoiceFilter(
        field_name='author',
        label='Автор',
        queryset=User.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite',
        label='Избранные группы',
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        label='Тэги',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='Рецепты в корзине',
    )

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
