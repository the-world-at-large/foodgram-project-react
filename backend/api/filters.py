from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from recipes.models import Ingredients, Recipes

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
    """Фильтрация по избранному, автору списку покупок и тегам."""

    author = filters.ModelChoiceFilter(
        field_name='author',
        label='Автор',
        queryset=User.objects.all(),
    )
    is_favorite = filters.BooleanFilter(
        method='get_favorite',
        label='Избранные группы',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags',
        label='Тэги',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='Рецепты в корзине'
    )

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'author',
            'is_favorite',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(
            favorites__user=self.request.user,
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipes.objects.filter(
                shopping_list__user=self.request.user,
            )
