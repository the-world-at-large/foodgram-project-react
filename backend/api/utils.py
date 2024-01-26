from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from recipes.models import Ingredients, RecipeIngredients, Recipes
from rest_framework import status
from rest_framework.response import Response


def shopping_cart_report(shopping_cart):
    """Обработчик списка покупок."""
    try:
        recipes = Recipes.objects.filter(pk__in=shopping_cart)
    except Recipes.DoesNotExist:
        # Обработка случая, когда один или несколько рецептов не найдены.
        return 'Некоторые рецепты из корзины покупок недоступны.'

    buy_list = RecipeIngredients.objects.filter(
        recipe__in=recipes
    ).values(
        'ingredient'
    ).annotate(
        amount=Sum('amount')
    )

    buy_list_text = 'Foodgram\nКорзина покупок:\n'

    for item in buy_list:
        try:
            ingredient = Ingredients.objects.get(pk=item['ingredient'])
            amount = item['amount']
            buy_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )
        except ObjectDoesNotExist:
            # Обработка случая, когда ингредиент не найден.
            return 'Некоторые ингредиенты из корзины покупок недоступны.'

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
