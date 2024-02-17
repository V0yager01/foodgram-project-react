from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

foodgram_v1_router = DefaultRouter()

foodgram_v1_router.register(
    'users',
    views.UserViewSet,
    basename='register'
)
foodgram_v1_router.register(
    'tags',
    views.TagViewSet,
    basename='tags'
)
foodgram_v1_router.register(
    'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
foodgram_v1_router.register(
    'recipes',
    views.RecipesViewSet,
    basename='recipes'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(foodgram_v1_router.urls)),
]
