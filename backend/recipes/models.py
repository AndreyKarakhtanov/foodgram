from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (INGREDIENT_AMOUNT_MAX_VALUE,
                        INGREDIENT_AMOUNT_MIN_VALUE,
                        INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
                        INGREDIENT_NAME_MAX_LENGTH,
                        RECIPE_COOKING_TIME_MAX_VALUE,
                        RECIPE_COOKING_TIME_MIN_VALUE, RECIPE_NAME_MAX_LENGTH,
                        TAG_NAME_MAX_LENGTH, TAG_SLUG_MAX_LENGTH)

User = get_user_model()


class Tag(models.Model):
    """Класс модели тег."""
    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_NAME_MAX_LENGTH,
        help_text='Уникальное название, не более 256 символов',
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'объект "Тег"'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс модели ингредиент."""
    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        help_text='Уникальное название, не более '
        f'{INGREDIENT_NAME_MAX_LENGTH} символов.',
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
        help_text='Название не более '
        f'{INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH} символов.'
    )

    class Meta:
        verbose_name = 'объект "Ингредиент"'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'),
        )
        ordering = ['name']  # unique?

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Класс модели рецепт."""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(Tag, verbose_name='теги')
    name = models.CharField(
        verbose_name='Название',
        max_length=RECIPE_NAME_MAX_LENGTH
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(RECIPE_COOKING_TIME_MIN_VALUE),
            MaxValueValidator(RECIPE_COOKING_TIME_MAX_VALUE)
        ]
    )
    text = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'объект "Рецепт"'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at', 'name', 'author', 'cooking_time', 'text')

    def __str__(self):
        return self.name

    def favorites_count(self):
        return 0


class RecipeIngredient(models.Model):
    """Класс модели связи рецепт-ингредиент."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(INGREDIENT_AMOUNT_MIN_VALUE),
            MaxValueValidator(INGREDIENT_AMOUNT_MAX_VALUE)
        ]
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'объект "Компонент рецепта"'
        verbose_name_plural = 'Рецепт-Ингредиент'
        default_related_name = 'recipe_ingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_composition'),
        )
        ordering = ('recipe', 'ingredient')


class RecipeUser(models.Model):
    """Класс абстрактной модели рецепт-пользователь."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        ordering = ('recipe', 'user')


class Favorite(RecipeUser):
    """Класс модели избранное."""
    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'

    class Meta:
        verbose_name = 'объект "Избранный рецепт пользователя"'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'), name='unique_favorite'),
        )


class ShoppingCart(RecipeUser):
    """Класс модели список покупок."""
    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'

    class Meta:
        verbose_name = 'объект "Рецепт в списоке покупок пользователя"'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'), name='unique_shopping_cart'),
        )
