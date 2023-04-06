import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

BOOL_CHOICES = ((None, 'Please Select'), (True, 'Yes'), (False, 'No'))

class Category(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


# a model to save the uploaded dish picture to the file
class FoodPicture(models.Model):
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    picture = models.FileField()

    def __str__(self):
        return 'Picture of ' + self.food.name


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=200, editable=True, blank=True)
    favorite = models.ManyToManyField(Food, related_name='favoring', blank=True)

    def __str__(self):
        return 'userid=' + str(self.user.id) + ', username=' + self.user.username


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
    # table = models.ForeignKey(Table, on_delete=models.PROTECT, blank=True, related_name='table')
    # whether the food is take out or not
    is_takeout = models.BooleanField(choices=BOOL_CHOICES, default=False)
    is_paid = models.BooleanField(choices=BOOL_CHOICES, default=False)
    is_completed = models.BooleanField(choices=BOOL_CHOICES, default=False)
    total_price = models.FloatField()

    def __str__(self):
        return 'Order ' + str(self.id) + ' for ' + self.customer.username
    


class Table(models.Model):
    orders = models.ManyToManyField(Order, related_name="table", blank=True, editable=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, editable=True, null=True)
    open_time = models.TimeField(default='11:00', editable=True)
    close_time = models.TimeField(default='21:00', editable=True)
    capacity = models.IntegerField(editable=True)

    def __str__(self):
        return  str(self.id) 

# class UnconfirmedReservation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.PROTECT)
#     num_customers = models.IntegerField(blank=False)
#     date = models.DateField(editable=True, blank=False)
#     time = models.TimeField(editable=True, blank=False)
#     table = models.ForeignKey(Table, on_delete=models.PROTECT)

class Reservation(models.Model):
    number_customers = models.IntegerField(blank=False)
    table = models.ForeignKey(Table, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=200, editable=True, blank=False)
    last_name = models.CharField(max_length=200, editable=True, blank=False)
    phone_number = models.CharField(max_length=200, editable=True, blank=False)
    comment = models.CharField(max_length=200, editable=True, blank=True)
    date = models.DateField(editable=True, blank=False)
    time = models.TimeField(editable=True, blank=False)

# automatically create a profile for a new user if a new superuser is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            Profile.objects.create(user=instance)
            instance.first_name = instance.username
            instance.save()
            instance.profile.save()
