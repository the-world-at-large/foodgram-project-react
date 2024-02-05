from django.db.models import Sum

from recipes.models import RecipeIngredient


def shopping_cart_report(user):
    """Обработчик корзины покупок."""

    ingredient_totals = RecipeIngredient.objects.filter(
        recipe__shopping_list__user=user,
    ).values(
        'ingredient__name', 'ingredient__measurement_unit',
    ).annotate(
        total_amount=Sum('amount')
    ).order_by('ingredient__name')

    buy_list_text = 'Foodgram\nКорзина покупок:\n'
    for ingredient_total in ingredient_totals:
        ingredient_name = ingredient_total['ingredient__name']
        measurement_unit = ingredient_total['ingredient__measurement_unit']
        total_amount = ingredient_total['total_amount']
        buy_list_text += (f'{ingredient_name}, '
                          f'{total_amount} {measurement_unit}\n')

    return buy_list_text
