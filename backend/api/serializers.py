import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
        if not self.context['request'].user.is_anonymous:
            return obj.subscriptions.filter(
                user=self.context['request'].user,
                blogger=obj
            ).exists()
        else:
            return False

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserRegSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop("password", None)
        return rep

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_fields(self):
        fields = super(UserRegSerializer, self).get_fields()
        for field in fields.values():
            field.required = True
        return fields


class RecipeDataSerializer(serializers.ModelSerializer):
    """Сериализатор основы рецепта."""

    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор информации рецептах пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeDataSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_anonymous:
            return obj.subscriptions.filter(
                user=self.context['request'].user,
                blogger=obj
            ).exists()
        else:
            return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

    def to_internal_value(self, data):
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингрединетов."""

    name = serializers.CharField(max_length=256)
    measurement_unit = serializers.CharField(max_length=128)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        return data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    name = serializers.CharField(max_length=256)
    cooking_time = serializers.IntegerField()
    text = serializers.CharField()
    tags = TagSerializer(many=True, partial=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags', [])
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.tags.set(tags_data)
        instance.recipe_ingredients.all().delete()
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        instance.save()
        return instance

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        if not self.context['request'].user.is_anonymous:
            return obj.favorites.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        if not self.context['request'].user.is_anonymous:
            return obj.shopping_cart.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        else:
            return False

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть целым положительным числом.')
        return value

    def validate(self, data):
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
            try:
                Ingredient.objects.get(pk=ingredient.get('id'))
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Ингредиент отсутствует в базе.'
                    }
                )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Ингредиент не должен повторяться.'
                    }
                )
            else:
                ingredient_list.append(ingredient)
            amount = int(ingredient.get('amount'))
            if not amount:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Обязательное поле. '
                        '(Количество ингредиента)'
                    }
                )
            elif not isinstance(amount, int) or not amount > 0:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Количество ингредиента должно быть '
                        'целым положительным числом.'
                    }
                )
        data['ingredients'] = ingredients
        return data
