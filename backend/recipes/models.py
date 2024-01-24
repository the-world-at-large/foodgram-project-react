from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, validate_slug
from django.db import models

User = get_user_model()


class Tags(models.Model):
    '''Модель тэгов.'''

    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    BLACK = "#000000"
    TORQUOISE = "#00FFFF"

    COLOR_CHOICES = [
        (RED, "Красный"),
        (GREEN, "Зелёный"),
        (BLUE, "Синий"),
        (BLACK, "Чёрный"),
        (TORQUOISE, "Бирюзовый"),
    ]

    name = models.CharField(
        'Название тэга',
        max_length=200,
        blank=False,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        blank=False,
        unique=True,
        verbose_name='Цвет',
        default=RED,
    )
    slug = models.SlugField(
        'Слаг тэга',
        unique=True,
        blank=False,
        validators=[
            validate_slug
        ],
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    '''Модель ингредиентов.'''

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        blank=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    '''Модель рецептов.'''

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        blank=False,
        help_text='Введите название рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
        blank=False,
        help_text='Введите описание рецепта',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        blank=False,
        help_text='Прикрепите изображение',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        blank=False,
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
        Tags,
        blank=False,
        related_name='recipes',
        verbose_name='Тэги',
        help_text='Выберите тэги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        blank=False,
        validators=[
            MinValueValidator(
                1,
                'Время приготовления должно быть больше 1'
            )
        ],
        help_text='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    '''Модель ингредиентов рецепта.'''

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте',
        verbose_name_plural = 'Ингредиенты в рецепте'


class ShoppingList(models.Model):
    '''Модель добавления рецептов в корзину.'''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Владелец списка покупок',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        null=True,
        related_name='shopping_list',
        verbose_name='Рецепт из списка покупок',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe'
            ),
        ]

    def __str__(self):
        return (f'Рецепт "{self.recipe.name}" '
                f'из корзины покупок пользователя {self.user}')


class FavouritesList(models.Model):
    '''Модель подписок.'''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favourites',
        verbose_name='Владелец списка избранных рецептов',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        null=True,
        related_name='favourites',
        verbose_name='Избранные рецепты',
    )

    class Meta:
        verbose_name = 'Список избранных рецептов'
        verbose_name_plural = 'Списки избранных рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourites'
            ),
        ]

    def __str__(self):
        return (f'Избранный рецепт "{self.recipe.name}" '
                f'пользователя {self.user}')
