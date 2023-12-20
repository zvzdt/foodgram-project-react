import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(f'{data_path}/data/ingredients.csv',
                  'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                _, created = Ingredients.objects.get_or_create(
                    name=row[0],
                    defaults={'measurement_unit': row[1]}
                )
                if created:
                    self.stdout.write(f'Ингредиен создан: {row[0]}')
                else:
                    self.stdout.write(f'Ингредиент {row[0]} уже существует')
            self.stdout.write(self.style.SUCCESS('Данные успешно загружены.'))


# import csv
# from django.db import transaction
# from recipes.models import Ingredients

# @transaction.atomic
# def load_data_from_csv():
#     with open('data/ingredients.csv', newline='') as csvfile:
#         csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
#         next(csv_reader)  # skip header row
#         ingredients_to_create = []
#         existing_ingredients = set(Ingredients.objects.values_list('name', flat=True))
#         for row in csv_reader:
#             name = row[0].strip()
#             measurement_unit = row[1].strip()
#             if name not in existing_ingredients:
#                 ingredient = Ingredients(name=name, measurement_unit=measurement_unit)
#                 ingredients_to_create.append(ingredient)
#                 existing_ingredients.add(name)
#         Ingredients.objects.bulk_create(ingredients_to_create)
#     print('Данные успешно загружены.')
