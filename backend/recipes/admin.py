from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка для компонентов в рецептах."""

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного."""

    list_display = (
        'user',
        'recipe',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""
    inlines = (RecipeIngredientInline,)
    search_fields = (
        'author__username',
        'name',
    )
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    list_display = (
        'name',
        'author',
        'favorites_count'
    )
    readonly_fields = ('author',)

    def get_queryset(self, request):
        return super(RecipeAdmin, self).get_queryset(request).annotate(
            favorites_count=Count('favorites', distinct=True)
        )

    @admin.display(
        ordering='favorites_count',
        description='Общее число добавлений в избранное'
    )
    def favorites_count(self, obj):
        return obj.favorites_count

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для списка покупок."""

    list_display = (
        'user',
        'recipe',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тэгов."""

    list_display = (
        'name',
        'slug',
    )
