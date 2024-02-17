from csv import reader

from django.core.management.base import BaseCommand

from post.models import Ingredient


path = 'post/management/commands/ingredients.csv'


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(
                path, 'r',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                Ingredient.objects.create(
                    name=row[0], measurement_unit=row[1],
                )
