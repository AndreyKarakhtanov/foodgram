from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=256,
        help_text='Уникальное название, не более 256 символов')
    slug = models.SlugField('Слаг', max_length=64, unique=True)

    class Meta:
        verbose_name = 'объект "Тег"'  # 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=256,
        help_text='Уникальное название, не более 256 символов')
    measurement_unit = models.CharField(
        'Единица измерения', max_length=128,
        help_text='Уникальное название, не более 128 символов')

    class Meta:
        verbose_name = 'объект "Ингредиент"'  # 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    ingredients = models.ManyToManyField(Ingredient, through='Composition')
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=256)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    cooking_time = models.PositiveSmallIntegerField('Время приготовления')
    text = models.TextField('Описание')
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'объект "Рецепт"'  # 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name', 'author', 'cooking_time', 'text')

    def __str__(self):
        return self.name


class Composition(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='composition'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='composition'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'объект "Компонент рецепта"'  # 'Рецепт'
        verbose_name_plural = 'Составы'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='unique_composition'),
        )
        ordering = ('recipe', 'ingredient')


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites'
    )

    def __str__(self):
        return f'{self.recipe} favorite for {self.user}'

    class Meta:
        verbose_name = 'объект "Избранный рецепт пользователя"'  # 'Рецепт'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'), name='unique_favorite'),
        )
        ordering = ('recipe', 'user')


class ShoppingCart(models.Model):
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
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'), name='unique_shopping_cart'),
        )
        ordering = ('user', 'recipe')


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    blogger = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )

    def __str__(self):
        return f'{self.user} subscribed for {self.blogger}'

    class Meta:
        verbose_name = 'объект "Подписка"'  # 'Рецепт'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('blogger', 'user'), name='unique_subscription'),
        )
        ordering = ('user', 'blogger')
