from django.contrib import admin

from .models import (
    Composition, Favorite, Ingredient, Recipe, ShoppingCart, Subscription, Tag
)


class CompositionAdmin(admin.ModelAdmin):
    """Админка для компонентов в рецептах."""

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )


class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного."""

    list_display = (
        'user',
        'recipe',
    )


class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""

    list_display = (
        'name',
        'measurement_unit',
    )


class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""

    list_display = (
        'name',
        'author',
        'image',
        'cooking_time',
        'text',
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для списка покупок."""

    list_display = (
        'user',
        'recipe',
    )


class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок."""

    list_display = (
        'user',
        'blogger',
    )


class TagAdmin(admin.ModelAdmin):
    """Админка для тэгов."""

    list_display = (
        'name',
        'slug',
    )


admin.site.register(Composition, CompositionAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Tag, TagAdmin)
