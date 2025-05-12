from django.contrib import admin

from .forms import RecipeModelForm
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeIngredientAdmin(admin.ModelAdmin):
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
    search_fields = (
        'name',
    )


class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""
    form = RecipeModelForm
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
    )
    readonly_fields = ('author',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для списка покупок."""

    list_display = (
        'user',
        'recipe',
    )


class TagAdmin(admin.ModelAdmin):
    """Админка для тэгов."""

    list_display = (
        'name',
        'slug',
    )


admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
