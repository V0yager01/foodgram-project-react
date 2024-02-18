from django.core.validators import (validate_slug,
                                    MaxValueValidator,
                                    MinValueValidator)
from django.db import models

from user.models import User
from .validators import validate_color


MAX_LENGTH = 256

MAX_COLOR_LENGTH = 7

MIN_VALUE = 0

MAX_AMOUNT_VALUE = 10000

MAX_VALUE_COOKING_TIME = 500


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(verbose_name="Name",
                            max_length=MAX_LENGTH,
                            unique=True,
                            blank=False)
    color = models.CharField(verbose_name="color",
                             max_length=MAX_COLOR_LENGTH,
                             blank=False,
                             validators=[validate_color],
                             default='#000000')
    slug = models.SlugField(unique=True,
                            blank=False,
                            max_length=MAX_LENGTH,
                            verbose_name='Slug name',
                            validators=[validate_slug])

    class Meta:
        verbose_name = 'Тэг',
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f"{self.name}"


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=MAX_LENGTH,
                            blank=False,
                            verbose_name='Name')
    measurement_unit = models.CharField(max_length=MAX_LENGTH,
                                        verbose_name='Measurement unit')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit'
            )
        ]
        verbose_name = 'Ингредиент',
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Author',
                               related_name='recipes')
    name = models.CharField(verbose_name="Название рецепта",
                            max_length=MAX_LENGTH,
                            blank=False)
    image = models.ImageField(upload_to='recipes/',
                              blank=False,
                              verbose_name='Image')
    text = models.CharField(max_length=MAX_LENGTH,
                            blank=False,
                            verbose_name='Text')
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        validators=[MinValueValidator(MIN_VALUE),
                    MaxValueValidator(MAX_VALUE_COOKING_TIME)])
    pub_date = models.DateTimeField('pub_date',
                                    auto_now_add=True)
    tags = models.ManyToManyField(Tag,
                                  blank=False,
                                  verbose_name='tag')
    ingredients = models.ManyToManyField(Ingredient,
                                         blank=False,
                                         related_name='recipes')

    def __str__(self) -> str:
        return f"{self.name} - {self.author}"

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'


class RecipeToIngredient(models.Model):
    """Промежуточная таблица между рецептом и ингредиентом."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_recipes')
    amount = models.PositiveSmallIntegerField(verbose_name='amount',
                                              blank=False,
                                              validators=[
                                                  MinValueValidator(
                                                      MIN_VALUE
                                                  ),
                                                  MaxValueValidator(
                                                      MAX_AMOUNT_VALUE)]
                                              )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique'
            )
        ]
        verbose_name = 'Ингредиент в рецепте',
        verbose_name_plural = 'Ингредиенты в рецептах'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='user_favorite')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name="recipe_favorite")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_recipe_fav'
            )
        ]
        verbose_name = 'Избранное',
        verbose_name_plural = 'Избранные'


class ShopList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='user_shoplist')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               verbose_name='recipe_shoplist')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="user_recipe"
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        return f"{self.user} shoplist"
