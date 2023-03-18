from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=200, editable=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=500)


class Food(models.Model):
    name = models.CharField(max_length=500)
    price = models.FloatField()
    description = models.CharField(max_length=500)
    picture = models.ImageField()
    content_type = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    calories = models.FloatField()
    # 1 for spicy and 0 for non-spicy
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)


class Comment(models.Model):
    text = models.CharField(max_length=500)
    creation_time = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    post_under = models.ManyToManyField(Food, related_name="comments")


# handle quantities of different foods
class FoodSet(models.Model):
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    quantity = models.IntegerField()


class Order(models.Model):
    foods = models.ManyToManyField(FoodSet, related_name="orders")
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    order_time = models.DateTimeField()
    # whether the food is take out or not
    is_takeout = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    total_price = models.FloatField()


class Table(models.Model):
    orders = models.ManyToManyField(Order, related_name="table")
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    open_time = models.DateTimeField()
