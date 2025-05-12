from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Класс модели тег."""
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        help_text='Уникальное название, не более 256 символов'
    )
    slug = models.SlugField(verbose_name='Слаг', max_length=64, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'объект "Тег"'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс модели ингредиент."""
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        help_text='Уникальное название, не более 256 символов')
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=128,
        help_text='Уникальное название, не более 128 символов')

    class Meta:
        verbose_name = 'объект "Ингредиент"'
        verbose_name_plural = 'Ингредиенты'

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
        # through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(Tag, verbose_name='теги')
    name = models.CharField(verbose_name='Название', max_length=256)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
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


class RecipeIngredient(models.Model):
    """Класс модели связи рецепт-ингредиент."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'объект "Компонент рецепта"'
        verbose_name_plural = 'Рецепт-Ингредиент'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_composition'),
        )
        ordering = ('recipe', 'ingredient')


class Favorite(models.Model):
    """Класс модели избранное."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites'
    )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'

    class Meta:
        verbose_name = 'объект "Избранный рецепт пользователя"'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'), name='unique_favorite'),
        )
        ordering = ('recipe', 'user')


class ShoppingCart(models.Model):
    """Класс модели список покупок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart'
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        verbose_name = 'объект "Рецепт в списоке покупок пользователя"'
        verbose_name_plural = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'), name='unique_shopping_cart'),
        )
        ordering = ('user', 'recipe')
