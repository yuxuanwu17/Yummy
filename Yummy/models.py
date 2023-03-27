from django.db import models
from django.contrib.auth.models import User

BOOL_CHOICES = ((None, 'Please Select'), (True, 'Yes'), (False, 'No'))

class Category(models.Model):
    name = models.CharField(max_length=500)


class Food(models.Model):
    name = models.CharField(max_length=500)
    price = models.FloatField()
    description = models.CharField(max_length=500, blank=True)
    picture_dir = models.CharField(max_length=500, blank = True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True)
    calories = models.FloatField(blank=True)
    # 1 for spicy and 0 for non-spicy
    is_spicy = models.BooleanField(choices=BOOL_CHOICES, default=False, blank=True)
    is_vegetarian = models.BooleanField(choices=BOOL_CHOICES, default=False, blank=True)


# a model to save the uploaded dish picture to the file
class FoodPicture(models.Model):
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    picture = models.FileField()

    def __str__(self):
        return 'name=' + self.name


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=200, editable=True, blank=True)
    favorite = models.ManyToManyField(Food, related_name='favoring', blank=True)

    def __str__(self):
        return 'userid=' + str(self.user.id) + ', phone_number=' + self.phone_number


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
    is_takeout = models.BooleanField(choices=BOOL_CHOICES,default=False)
    is_paid = models.BooleanField(choices=BOOL_CHOICES,default=False)
    total_price = models.FloatField()


class Table(models.Model):
    orders = models.ManyToManyField(Order, related_name="table")
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    open_time = models.DateTimeField()


class Reservation(models.Model):
    num_customers = models.IntegerField(blank=False)
    table = models.ForeignKey(Table, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=200, editable=True, blank=False)
    last_name = models.CharField(max_length=200, editable=True, blank=False)
    phone_number = models.CharField(max_length=200, editable=True, blank=False)
    comment = models.CharField(max_length=200, editable=True, blank=True)
