from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef, Value

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import CreateListRetrieveViewSet
from api.paginators import PageNumberLimitPaginator
from api.serializers import (
    CreateAndDeleteSubscriptionSerializer, AddFavoriteRecipeSerializer,
    GetRecipeSerializer, IngredientSerializer,
    RecipeCreateAndUpdateSerializer, SetNewPasswordSerializer,
    ShoppingCartSerializer, SubscriptionShowSerializer, TagSerializer,
    AddUserSerializer, UserReadSerializer
)
from api.utils import add_link, remove_link, shopping_cart_report

from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag
)
from users.models import Follow

User = get_user_model()


class UserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        if self.action == 'set_password':
            return SetNewPasswordSerializer
        if self.action == 'subscribe':
            return CreateAndDeleteSubscriptionSerializer
        return AddUserSerializer

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('post',),
        detail=False,
        serializer_class=SetNewPasswordSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        if not user.check_password(old_password):
            return Response(
                {'error': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Пароль успешно изменен'},
                        status=status.HTTP_200_OK)

    @action(
        methods=('get',),
        detail=False,
        serializer_class=SubscriptionShowSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=PageNumberLimitPaginator
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.follower.select_related('author')
        users = [subscription.author for subscription in subscriptions]
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.serializer_class(paginated_queryset,
                                           context={'request': request},
                                           many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=CreateAndDeleteSubscriptionSerializer,
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, pk=None):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'id': pk},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(id=pk)
            return Response(
                {'message': 'Подписка успешно создана'},
                status=status.HTTP_201_CREATED,
            )

        subscription = get_object_or_404(
            Follow, user=request.user,
            author=get_object_or_404(User, pk=pk)
        )
        subscription.delete()
        return Response(
            {'message': 'Успешно отписан'},
            status=status.HTTP_204_NO_CONTENT,
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberLimitPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        if self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeCreateAndUpdateSerializer

    def get_queryset(self):
        return Recipe.objects.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=self.request.user, recipe=OuterRef('id'))),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('id')))
        ).select_related('author').prefetch_related(
            'tags',
            'ingredients',
            'shopping_list',
            'favorites',
        ) if self.request.user.is_authenticated else Recipe.objects.annotate(
            is_in_shopping_cart=Value(False),
            is_favorited=Value(False),
        ).select_related('author').prefetch_related(
            'tags',
            'ingredients',
            'shopping_list',
            'favorites',
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete',),
        detail=True,
        serializer_class=AddFavoriteRecipeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return add_link(
                self,
                request,
                Favorite,
                'Рецепт уже добавлен в избранное.',
                pk,
            )
        if request.method == 'DELETE':
            return remove_link(
                self,
                request,
                Favorite,
                pk,
            )

    @action(
        methods=('post', 'delete',),
        detail=True,
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return add_link(
                self,
                request,
                ShoppingCart,
                'Рецепт уже добавлен в список покупок.',
                pk,
            )
        if request.method == 'DELETE':
            return remove_link(
                self,
                request,
                ShoppingCart,
                pk,
            )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        buy_list_text = shopping_cart_report(request.user)
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
