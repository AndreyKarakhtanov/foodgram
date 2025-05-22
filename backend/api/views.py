from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef, Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UserViewSetBase
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeDataSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserAvatarSerializer, UserRecipeSerializer,
                          UserSerializer)
from .utils import encode_to_string, to_pdf

User = get_user_model()


class UserViewSet(UserViewSetBase):
    """Класс-вьюсет кастомного пользователя."""
    pagination_class = LimitPagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Страница текущего пользователя."""
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Страница изменения аватара текущего пользователя."""
        user = self.request.user
        serializer = UserAvatarSerializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': serializer.data.get('avatar')})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = self.request.user
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

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Страница добаления/удаления подписки на пользователя."""
        user = request.user
        blogger = self.get_object()
        if request.method == 'POST':
            try:
                if user == blogger:
                    raise Exception
                subscription, created = Subscription.objects.get_or_create(
                    user=user,
                    blogger=blogger
                )
                if not created:
                    raise Exception
                return Response(
                    UserRecipeSerializer(
                        self.get_object(),
                        context={'request': request}
                    ).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscription(self, request, id=None):
        user = request.user
        blogger = self.get_object()
        deleted_subscription = Subscription.objects.get(
            user=user,
            blogger=blogger
        ).delete()
        if not deleted_subscription[0]:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    action_serializers = {
        'retrieve': RecipeListSerializer,
        'list': RecipeListSerializer,
        'create': RecipeSerializer,
        'patch': RecipeSerializer,
    }
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            return self.action_serializers.get(
                self.action, self.
                serializer_class
            )
        return super(RecipeViewSet, self).get_serializer_class()

    def get_queryset(self):
        is_favorited = Favorite.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user,
        )
        in_shopping_cart = ShoppingCart.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user,
        )
        queryset = Recipe.objects.all().annotate(
            is_favorited=Exists(is_favorited),
            is_in_shopping_cart=Exists(in_shopping_cart)
        )
        return queryset

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Страница получения короткой ссылки на рецепт."""
        short_link = encode_to_string(int(pk))
        return Response(
            {
                'short-link': request.build_absolute_uri('/s/') + short_link
            }
        )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Страница скачивания списка покупок."""
        shopping_cart_list = list(
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
            ).annotate(
                total_amount=Sum('amount')
            ).order_by('ingredient__name')
        )
        buffer = to_pdf(shopping_cart_list)
        return FileResponse(buffer, as_attachment=True,
                            filename="Список покупок.pdf")

    def create_user_recipe(self, model):
        user = self.request.user
        recipe = self.get_object()
        instance, created = model.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(
            RecipeDataSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def delete_user_recipe(self, model):
        user = self.request.user
        recipe = self.get_object()
        deleted_user_recipe = model.objects.get(
            user=user,
            recipe=recipe
        ).delete()
        try:
            if not deleted_user_recipe[0]:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Страница добавления рецепта в списке покупок."""
        return self.create_user_recipe(ShoppingCart)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Страница удаления рецепта из списка покупок."""
        return self.delete_user_recipe(ShoppingCart)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Страница добавления/удаления рецепта в списке избранного."""
        return self.create_user_recipe(Favorite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Страница удаления рецепта из списка избранного."""
        return self.delete_user_recipe(Favorite)
