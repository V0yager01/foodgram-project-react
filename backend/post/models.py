from django.core.validators import validate_slug
from django.db import models

from user.models import User


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(verbose_name="Name",
                            max_length=256,
                            unique=True,
                            blank=False)
    color = models.CharField(verbose_name="color",
                             max_length=16,
                             blank=False)
    slug = models.SlugField(unique=True,
                            blank=False,
                            max_length=256,
                            verbose_name='Slug name',
                            validators=[validate_slug])

    def __str__(self) -> str:
        return f"{self.name}"


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(max_length=256,
                            blank=False,
                            verbose_name='Name')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Measurement unit')

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Author',
                               related_name='recipes')
    name = models.CharField(verbose_name="Название рецепта",
                            max_length=256,
                            blank=False)
    image = models.ImageField(upload_to='recipes/',
                              blank=False,
                              verbose_name='Image')
    text = models.CharField(max_length=256,
                            blank=False,
                            verbose_name='Text')
    cooking_time = models.IntegerField(blank=False)
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


class RecipeToIngredient(models.Model):
    """Промежуточная таблица между рецептом и ингредиентом."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_recipes')
    amount = models.IntegerField(verbose_name='amount',
                                 blank=False)


class Favorite(models.Model):
    """Favorite."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='user_favorite')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name="recipe_favorite")


class ShopList(models.Model):
    """Shop list."""

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

    def __str__(self) -> str:
        return f"{self.user} shoplist"
