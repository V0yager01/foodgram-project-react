from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from post.models import (Ingredient,
                         Tag,
                         Recipe,
                         RecipeToIngredient,
                         ShopList)
from user.models import User

from .filters import IngedientNameFilter, RecipesFilters
from .paginators import LimitPaginator
from .serializers import (ChangePasswordSerializer,
                          SignUpSerializer,
                          FavoriteSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          RecipeGetListSerializer,
                          RecipesCreateSerializer,
                          ShopListSerializer,
                          SubscribeSerializer,
                          SubscriceListSerializer,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)

    @action(
        detail=False,
        methods=(['GET']),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = SignUpSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=(['POST']),
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        current_password = serializer.validated_data.get('current_password')
        if not user.check_password(current_password):
            return Response (
                'Неверный пароль',
                status=400
            )
        user.set_password(new_password)
        user.save()
        return Response('Пароль успешно изменен', status=200)

    @action(
        detail=True,
        methods=(['POST', 'DELETE']),
        serializer_class=SubscribeSerializer,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        serializer = SubscribeSerializer(data=request.data,
                                         context={
                                             'request': request,
                                             'id': pk
                                         })
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data["message"], status=data["status"])

    @action(
        detail=False,
        methods=(['GET']),
        serializer_class=SubscriceListSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPaginator
    )
    def subscriptions(self, request):
        user = request.user
        subs = user.user.all()
        subs_id_list = subs.values_list('author_id', flat=True)
        subs_list = User.objects.filter(id__in=subs_id_list)
        paginator = self.paginate_queryset(subs_list)
        serializer = SubscriceListSerializer(paginator,
                                             context={'request': request},
                                             many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngedientNameFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete',]
    filterset_class = RecipesFilters

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipesCreateSerializer
        elif self.action == 'list':
            return RecipeGetListSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        return RecipeGetListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=(['POST', 'DELETE']),
        serializer_class=FavoriteSerializer,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(data=request.data,
                                        context={
                                            "request": request,
                                            "pk": pk
                                        })
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data["message"], status=data["status"])

    @action(
        methods=(['DELETE', 'POST']),
        permission_classes=(IsAuthenticated,),
        serializer_class=ShopListSerializer,
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        serializer = ShopListSerializer(data=request.data,
                                        context={
                                            "request": request,
                                            "id": pk
                                        })
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data["message"], data["status"])

    @action(
        methods=(['GET']),
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def download_shopping_cart(self, request):
        shop_list = (ShopList.objects.filter(user=request.user)
                     .values_list('recipe_id', flat=True))
        download_list = (RecipeToIngredient
                         .objects
                         .filter(recipe__in=shop_list)
                         .values('ingredient')
                         .annotate(amount=Sum('amount')))
        out_txt = "Список покупок\n"
        for obj in download_list:
            ingredient = Ingredient.objects.get(pk=obj['ingredient'])
            amount = obj['amount']
            out_txt = (out_txt + f"{ingredient.name} "
                       + f"{amount} - "
                       + f"({ingredient.measurement_unit})\n")
        response = HttpResponse(out_txt, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           + 'filename="IngredientList.txt"')
        return response
