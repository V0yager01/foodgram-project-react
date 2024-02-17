import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from user.models import User, Subscribe
from post.models import (Favorite,
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
        if (self.context["request"].user.is_authenticated and
            Favorite.objects.filter(user=self.context["request"].user,
                                    recipe=obj).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if (self.context["request"].user.is_authenticated and
            ShopList.objects.filter(user=self.context["request"].user,
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_id = (Ingredient
                             .objects.get(id=ingredient['ingredient']['id']))
            RecipeToIngredient.objects.create(recipe=recipe,
                                              ingredient=ingredient_id,
                                              amount=amount)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags')
        RecipeToIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_id = (Ingredient.objects
                             .get(id=ingredient['ingredient']['id']))
            RecipeToIngredient.objects.create(recipe=instance,
                                              ingredient=ingredient_id,
                                              amount=amount)
        instance.tags.set(tags)
        return super().update(instance=instance, validated_data=validated_data)


class FavoriteSerializer(serializers.Serializer):
    def validate(self, data):
        if not Recipe.objects.filter(id=self.context['pk']).exists():
                raise serializers.ValidationError({"errors":
                                                   "Recipe do not exists"})

        if (self.context['request'].method == 'POST' and
            (Favorite
             .objects
             .filter(user=self.context['request'].user,
                     recipe=self.context['pk']).exists())):
                raise serializers.ValidationError({"errors":
                                                   "Recipe is favorite"})

        if (self.context['request'].method == 'DELETE' and
            (not Favorite.objects.filter(user=self.context['request'].user,
                                         recipe=self.context['pk']).exists())):
                raise serializers.ValidationError({"errors":
                                                   "Recipe is not favorite"})
        return data

    def create(self, validated_data):
        recipe = Recipe.objects.get(id=self.context['pk'])
        if self.context['request'].method == "POST":
            favorite = (Favorite
                        .objects
                        .create(user=self.context['request'].user,
                                recipe=recipe))
            favorite.save()
            return {'message': BaseRecipeSerializer(recipe).data,
                    'status': 201}
        favorite = Favorite.objects.get(user=self.context['request'].user,
                                        recipe=recipe).delete()
        return {'message': "Рецепт успешно удален из избранного",
                'status': 204}


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
        user = self.context['request'].user
        return obj.author.filter(user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')   
        limit = request.query_params.get('recipes_limit')
        if limit is None:
            recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()[:int(limit)]
        context = {'request': request}
        return BaseRecipeSerializer(recipes, many=True, context=context).data


class SubscribeSerializer(serializers.Serializer):

    def validate(self, validated_data):
        user = self.context.get('request').user
        print(self.context['id'])
        try:
            author = User.objects.get(id=self.context['id'])
        except Exception:
            raise serializers.ValidationError({"errors":
                                               "User do not exists"})
        if user == author:
            raise serializers.ValidationError({"errors":
                                               "You cant subscribe/unsub"})

        if self.context['request'].method == "POST":
            if Subscribe.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError({"errors":
                                                   "You are already subs"})
        else:
            if not Subscribe.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError({"errors":
                                                   "You are already unsub"})

        return validated_data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = User.objects.get(id=self.context['id'])
        if self.context.get('request').method == 'POST':
            Subscribe.objects.create(user=user, author=author)
            return {"data": "Вы подписались", "status": 201}
        sub = Subscribe.objects.get(user=user, author=author)
        print(sub)
        sub.delete()
        return {"data": "Вы отписались", "status": 204}


class ShopListSerializer(serializers.Serializer):

    def validate(self, validated_data):
        id = self.context['id']
        user = self.context['request'].user
        print(id)
        if not Recipe.objects.filter(id=id).exists():
            raise serializers.ValidationError({'errors':
                                               'Recipe do not exists'})
        shoplist_status = ShopList.objects.filter(user=user,
                                                  recipe_id=id).exists()
        if self.context['request'].method == 'POST' and shoplist_status:
            raise serializers.ValidationError({'errors':
                                               'Рецепт уже в списке'})
        elif (self.context['request'].method == 'DELETE'
              and not shoplist_status):
            raise serializers.ValidationError({'errors': 'Рецепт не в списке'})
        return validated_data

    def create(self, validated_data):
        id = self.context['id']
        user = self.context['request'].user
        recipe = Recipe.objects.get(id=id)
        print(id, user)
        if self.context['request'].method == 'POST':
            ShopList.objects.create(user=user, recipe_id=id)
            return {'message': BaseRecipeSerializer(recipe).data,
                    'status': 201}
        ShopList.objects.get(user=user, recipe_id=id).delete()
        return {"message": "Рецепт удален", "status": 204}
