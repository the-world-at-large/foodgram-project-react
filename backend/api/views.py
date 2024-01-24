from api.filters import IngredientFilter, RecipeFilter
from api.mixins import CreateListRetrieveViewSet
from api.paginators import PageNumberLimitPaginator
from api.serializers import (CreateAndDeleteSubscriptionsSerializer,
                             FavouriteRecipesListSerializer,
                             GetRecipesSerializer, IngredientsSerializer,
                             RecipeCreateAndUpdateSerializer,
                             SetNewPasswordSerializer, ShoppingCartSerializer,
                             SubscriptionsShowSerializer, TagsSerializer,
                             UserCreateSerializer, UserReadSerializer)
from api.utils import add_link, remove_link, shopping_cart_report
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavouritesList, Ingredients, Recipes, ShoppingList,
                            Tags)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follow

User = get_user_model()


class UsersViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        elif self.action == 'set_password':
            return SetNewPasswordSerializer
        elif self.action == 'subscribe':
            return CreateAndDeleteSubscriptionsSerializer
        return UserCreateSerializer

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
        serializer_class=SubscriptionsShowSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=PageNumberLimitPaginator
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.follower.all()
        users_id = subscriptions.values_list('author_id', flat=True)
        users = User.objects.filter(id__in=users_id)
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.serializer_class(paginated_queryset,
                                           context={'request': request},
                                           many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=CreateAndDeleteSubscriptionsSerializer,
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, pk=None):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'id': pk}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=pk)
            return Response(
                {'message': 'Подписка успешно создана',
                 'data': response_data},
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=request.user,
                author=get_object_or_404(User, pk=pk)
            )
            subscription.delete()
            return Response(
                {'message': 'Успешно отписан'},
                status=status.HTTP_204_NO_CONTENT
            )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
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
            return GetRecipesSerializer
        elif self.action == 'favourite':
            return FavouriteRecipesListSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeCreateAndUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete',),
        detail=True,
        serializer_class=FavouriteRecipesListSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def favourite(self, request):
        if request.method == 'POST':
            return add_link(
                self,
                request,
                FavouritesList,
                'Рецепт уже добавлен в избранное.'
            )
        elif request.method == 'DELETE':
            return remove_link(
                self,
                request,
                FavouritesList,
            )

    @action(
        methods=('post', 'delete',),
        detail=True,
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request):
        if request.method == 'POST':
            return add_link(
                self,
                request,
                ShoppingList,
                'Рецепт уже добавлен в список покупок.'
            )
        elif request.method == 'DELETE':
            return remove_link(
                self,
                request,
                ShoppingList,
            )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingList.objects.filter(user=request.user)
        buy_list_text = shopping_cart_report(shopping_cart)
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
