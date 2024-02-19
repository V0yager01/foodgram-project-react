from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from constants.constants import (MAX_AMOUNT_VALUE,
                                 MAX_COOK_TIME_VALUE,
                                 MIN_AMOUNT_VALUE,
                                 MIN_COOK_TIME_VALUE)
from user.models import User, Subscribe
from recipe.models import (Favorite,
                           Ingredient,
                           Recipe,
                           RecipeToIngredient,
                           ShopList,
                           Tag)


class SignUpSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id',
                  'email',
                  'first_name',
                  'last_name',
                  'password',
                  'username',
                  'is_subscribed')
        read_only_field = 'id'
        extra_kwargs = {'password': {'write_only': True}}
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_authenticated:
            return obj.author.filter(user=user).exists()
        return False


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=256)
    current_password = serializers.CharField(max_length=256)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Tag


class BaseRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class RecipeToIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ("id", "name", "measurement_unit", "amount")
        model = RecipeToIngredient


class RecipeGetListSerializer(serializers.ModelSerializer):
    ingredients = RecipeToIngredientSerializer(many=True,
                                               source='recipe_ingredients')
    author = SignUpSerializer()
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'name',
                  'text',
                  'image',
                  'cooking_time',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        if (self.context["request"].user.is_authenticated
            and Favorite.objects.filter(user=self.context["request"].user,
                                        recipe=obj).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if (self.context["request"].user.is_authenticated
            and ShopList.objects.filter(user=self.context["request"].user,
                                        recipe=obj).exists()):
            return True
        return False


class AddIngredientToRecipe(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeToIngredient
        fields = ('id',
                  'amount')

    def validate_amount(self, value):
        if MIN_AMOUNT_VALUE <= value <= MAX_AMOUNT_VALUE:
            return value
        raise serializers.ValidationError(
            ("amount не в диапазоне "
             f"{MIN_AMOUNT_VALUE} <= amount <= {MAX_AMOUNT_VALUE}")
        )


class RecipesCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = AddIngredientToRecipe(many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        if MIN_COOK_TIME_VALUE <= value <= MAX_COOK_TIME_VALUE:
            return value
        raise serializers.ValidationError(
            ("Cooking_time не в диапазоне "
             f"{MIN_AMOUNT_VALUE} <= cooking_time <= {MAX_AMOUNT_VALUE}")
        )

    def create(self, validated_data):
        ingredient_list = []
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_id = (Ingredient
                             .objects.get(id=ingredient['ingredient']['id']))
            ingredient_list.append(RecipeToIngredient(recipe=recipe,
                                                      ingredient=ingredient_id,
                                                      amount=amount))
        RecipeToIngredient.objects.bulk_create(ingredient_list)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredient_list = []
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags')
        RecipeToIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_id = (Ingredient.objects
                             .get(id=ingredient['ingredient']['id']))
            ingredient_list.append(RecipeToIngredient(recipe=instance,
                                                      ingredient=ingredient_id,
                                                      amount=amount))
        RecipeToIngredient.objects.bulk_create(ingredient_list)
        instance.tags.set(tags)
        return super().update(instance=instance, validated_data=validated_data)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user',
                  'recipe')

    def validate(self, data):
        if Favorite.objects.filter(user=data['user'],
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError({"errors":
                                               "Рецепт уже в избранном"})
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        FavoriteRecipe = Favorite.objects.create(user=user, recipe=recipe)
        FavoriteRecipe.save()
        return BaseRecipeSerializer(recipe).data


class SubscriceListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipe_count = serializers.IntegerField(read_only=True,
                                            source='recipes.count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipe_count')

    def get_is_subscribed(self, obj):
        user = self.context['user']
        return obj.author.filter(user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit is None:
            recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()[:int(limit)]
        return BaseRecipeSerializer(recipes, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, validated_data):
        user = validated_data['user']
        author = validated_data['author']
        if user == author:
            raise serializers.ValidationError(
                {"errors":
                    "Вы не можете подписаться на себя"})
        if Subscribe.objects.filter(user=user,
                                    author=author).exists():
            raise serializers.ValidationError({"errors":
                                               "Вы уже подписаны"})

        return validated_data

    def create(self, validated_data):
        request = self.context.get('request')
        author = validated_data['author']
        user = validated_data['user']
        Subscribe.objects.create(user=user, author=author)
        return SubscriceListSerializer(author, context={'user': author,
                                                        'request':
                                                        request}).data


class ShopListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopList
        fields = ("user", 'recipe')

    def validate(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']

        if ShopList.objects.filter(user=user,
                                   recipe=recipe).exists():
            raise serializers.ValidationError({'errors':
                                               'Рецепт уже в списке'})

        return validated_data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShopList.objects.create(user=user, recipe=recipe)
        return BaseRecipeSerializer(self.context.get('recipe')).data
