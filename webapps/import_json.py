# import_json.py
import json
from django.core.files import File
from django.core.serializers import deserialize
from django.apps import apps
import os
from Yummy.models import Category, Food, Table


def import_data_from_json_file(json_file_path):
    cwd = os.getcwd()
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    for item in json_data:
        category, _ = Category.objects.get_or_create(name=item['category'])
        # check if food with the same name already exists
        if Food.objects.filter(name=item['name']).exists():
            continue
        food = Food(
            name=item['name'],
            price=item['price'],
            description=item['description'],
            picture_dir=item['picture_dir'],
            category=category,
            calories=item['calories'],
            is_spicy=bool(item['is_spicy']),
            is_vegetarian=bool(item['is_vegetarian']),
        )
        # Save the instance before assigning the image
        food.save()

def create_initial_table():
    if len(Table.objects.all()) == 0:
        for i in range(10):
            Table.objects.create(capacity=4)
        for i in range(2):
            Table.objects.create(capacity=10)
