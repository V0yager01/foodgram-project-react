from django_filters import rest_framework

from post.models import Ingredient, Recipe
from user.models import User


class IngedientNameFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='istartswith',
                                     field_name='name')

    class Meta:
        model = Ingredient
        fields = ('name', )

class RecipesFilters(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all(),
    )

    is_favorited = rest_framework.BooleanFilter(
        method='get_favorite',
    )

    tags = rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_favorite__user=self.request.user)
        return queryset.exclude(recipe_favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shoplist__user=self.request.user
            )
