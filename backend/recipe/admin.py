from django.contrib import admin

from .models import (Favorite,
                     Ingredient,
                     Recipe,
                     RecipeToIngredient,
                     ShopList,
                     Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name')


@admin.register(RecipeToIngredient)
class RecipeToIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
    pass


@admin.register(ShopList)
class ShopList(admin.ModelAdmin):
    pass
