from csv import DictReader

from django.core.management.base import BaseCommand

from recipe.models import Ingredient


PATH = 'recipe/management/commands/ingredients.csv'


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(
                PATH, 'r',
                encoding='UTF-8'
        ) as ingredients:
            data_list = []
            for row in DictReader(ingredients):
                data_list.append(Ingredient(**row))
            Ingredient.objects.bulk_create(data_list)
