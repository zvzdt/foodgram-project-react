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
                    self.stdout.write(f'Создан игредиент: {row[0]}')
                else:
                    self.stdout.write(f'Ингредиент {row[0]} уже существует')
            self.stdout.write(self.style.SUCCESS('Данные успешно загружены.'))
