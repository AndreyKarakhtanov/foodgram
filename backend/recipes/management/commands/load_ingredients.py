import json
import os

from django.core.management.base import BaseCommand
from foodgram_backend.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients to database'

    def handle(self, *args, **kwargs):
        file_name = 'ingredients.json'
        json_file = os.path.join(BASE_DIR, file_name)
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
                obj_list = [Ingredient(**data_dict) for data_dict in data_list]
                Ingredient.objects.bulk_create(obj_list)
        except FileNotFoundError:
            print(f'Файл {file_name} со списком ингредиентов не найден.')
        except Exception as e:
            print(f'Ошибка при загрузке ингредиентов: {e}')
