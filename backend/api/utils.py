from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from recipes.models import Ingredients, RecipeIngredients, Recipes


def shopping_cart_report(shopping_cart):
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
