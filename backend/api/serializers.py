from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscription
        fields = '__all__'

    def to_representation(self, instance):
        user = UserRecipeSerializer(
            instance.blogger,
            context=self.context
        ).data
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and self.context.get('request').user.subscriptions.filter(
                blogger=obj
            ).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url


class RecipeDataSerializer(serializers.ModelSerializer):
    """Сериализатор основы рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipeSerializer(UserSerializer):
    """Сериализатор информации о рецептах пользователя."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeDataSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингрединетов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    tags = TagSerializer(many=True, partial=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'image', 'name', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        write_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'image', 'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        return RecipeListSerializer(instance).data

    def get_recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        return recipe_ingredients

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        RecipeIngredient.objects.bulk_create(
            self.get_recipe_ingredients(recipe, ingredients)
        )
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        # raise Exception(ingredients_data)
        tags_data = validated_data.pop('tags', [])
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        RecipeIngredient.objects.bulk_create(
            self.get_recipe_ingredients(instance, ingredients_data)
        )
        return super().update(instance, validated_data)

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {
                    'tags': 'Обязательное поле. '
                    'Добавьте мининум один тег.'
                }
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                {
                    'tags': 'Тег не должен повторяться.'
                }
            )
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Обязательное поле. '
                    'Добавьте мининум один ингредиент.'
                }
            )
        ingredient_list = []
        for ingredient in ingredients:
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Ингредиент не должен повторяться.'
                    }
                )
            else:
                ingredient_list.append(ingredient)
        return data
