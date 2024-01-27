from django.db.models import Sum
from django.shortcuts import get_object_or_404
from recipes.models import RecipeIngredients, Recipes, ShoppingList
from rest_framework import status
from rest_framework.response import Response


def shopping_cart_report(user):
    '''Обработчик списка покупок.'''
    # Получаем все рецепты, добавленные в корзину покупок данного пользователя.
    shopping_cart_recipes = ShoppingList.objects.filter(
        user=user).values_list('recipes', flat=True)

    # Получаем суммарное количество каждого ингредиента
    # из всех рецептов в корзине покупок.
    ingredient_totals = RecipeIngredients.objects.filter(
        recipe__in=shopping_cart_recipes)\
        .values('ingredient__name', 'ingredient__measurement_unit')\
        .annotate(total_amount=Sum('amount'))\
        .order_by('ingredient__name')

    # Формируем текст списка покупок.
    buy_list_text = 'Foodgram\nКорзина покупок:\n'
    for ingredient_total in ingredient_totals:
        ingredient_name = ingredient_total['ingredient__name']
        measurement_unit = ingredient_total['ingredient__measurement_unit']
        total_amount = ingredient_total['total_amount']
        buy_list_text += (f'{ingredient_name}, '
                          f'{total_amount} {measurement_unit}\n')

    return buy_list_text


def add_link(self, request, model, error_message, pk):
    '''Добавление связи.'''

    recipe = get_object_or_404(Recipes, pk=pk)
    _, with_relation = model.objects.get_or_create(
        user=request.user,
        recipe=recipe,
    )

    if not with_relation:
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    context = {'request': request}

    return Response(
        self.serializer_class(recipe, context=context).data,
        status=status.HTTP_201_CREATED
    )


def remove_link(self, request, model, pk):
    '''Удаление связи.'''

    recipe = get_object_or_404(Recipes, pk=pk)
    relation = get_object_or_404(
        model,
        recipe=recipe,
        user=request.user,
    )
    relation.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT,
    )
