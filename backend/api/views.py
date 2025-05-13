from django.contrib.auth import get_user_model
from django.http import FileResponse
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeDataSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer, UserAvatarSerializer,
                          UserRecipeSerializer)
from .utils import encode_to_string, to_pdf

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Класс-вьюсет кастомного пользователя."""
    def perform_create(self, serializer):
        serializer.save(
            password=self.request.data['password']
        )

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Страница изменения аватара текущего пользователя."""
        user = self.request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(data=request.data, instance=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': request.scheme + '://' + request.META['HTTP_HOST']
                    + serializer.data.get('avatar')}
            )
        elif request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Страница подписок текущего пользователя."""
        user = request.user
        queryset = Subscription.objects.filter(
            user=user
        )
        pages = self.paginate_queryset(queryset=queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Страница добаления/удаления подписки на пользователя."""
        user = request.user
        blogger = self.get_object()
        if request.method == 'POST':
            try:
                Subscription.objects.create(
                    user=user,
                    blogger=blogger
                )
                return Response(
                    UserRecipeSerializer(
                        self.get_object(),
                        context={'request': request}
                    ).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                Subscription.objects.get(
                    user=user,
                    blogger=blogger
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get')


class IngredientViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет ингредиетнов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ('get')

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__startswith=name.lower())
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        is_favorited = int(
            self.request.query_params.get('is_favorited') or 0
        )
        is_in_shopping_cart = int(
            self.request.query_params.get('is_in_shopping_cart') or 0
        )
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if is_favorited and not user.is_anonymous:
            queryset = queryset.filter(favorites__user=user)
        if is_in_shopping_cart and not user.is_anonymous:
            queryset = queryset.filter(shopping_cart__user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Страница получения короткой ссылки на рецепт."""
        short_link = encode_to_string(int(pk))
        return Response(
            {
                'short-link': request.scheme + '://'
                + request.META['HTTP_HOST'] + '/s/' + short_link
            }
        )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Страница скачивания списка покупок."""
        if True:
            shopping_cart_list = ShoppingCart.objects.filter(
                user=request.user
            ).prefetch_related('recipe__ingredients')
            ingredient_dict = dict()
            for shopping_cart in shopping_cart_list:
                full_recipe = shopping_cart.recipe.recipe_ingredients.all()
                for element in full_recipe:
                    ingredient_id = element.ingredient_id
                    if ingredient_id in ingredient_dict:
                        ingredient_dict[ingredient_id][2] += element.amount
                    else:
                        ingredient_dict[ingredient_id] = [
                            element.ingredient.name,
                            element.ingredient.measurement_unit,
                            element.amount
                        ]
        buffer = to_pdf(ingredient_dict)

        return FileResponse(buffer, as_attachment=True,
                            filename="Список покупок.pdf")

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Страница добавления/удаления рецепта в списке покупок."""
        current_recipe = self.get_object()
        if request.method == 'POST':
            try:
                ShoppingCart.objects.create(
                    user=request.user,
                    recipe=current_recipe
                )
                return Response(
                    RecipeDataSerializer(self.get_object()).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                ShoppingCart.objects.get(
                    user=request.user,
                    recipe=current_recipe
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Страница добавления/удаления рецепта в списке избранного."""
        current_recipe = self.get_object()
        if request.method == 'POST':
            try:
                Favorite.objects.create(
                    user=request.user,
                    recipe=current_recipe
                )
                return Response(
                    RecipeDataSerializer(self.get_object()).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                Favorite.objects.get(
                    user=request.user,
                    recipe=current_recipe
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
