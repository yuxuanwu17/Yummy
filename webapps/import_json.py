# import_json.py
import json
from django.core.files import File
from django.core.serializers import deserialize
from django.apps import apps

from Yummy.models import Category, Food


def import_data_from_json_file(json_file_path):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    for item in json_data:
        category, _ = Category.objects.get_or_create(name=item['category'])
        food = Food(
            name=item['name'],
            price=item['price'],
            description=item['description'],
            category=category,
            calories=item['calories'],
            is_spicy=bool(item['is_spicy']),
            is_vegetarian=bool(item['is_vegetarian']),
        )
        # Save the instance before assigning the image
        food.save()

