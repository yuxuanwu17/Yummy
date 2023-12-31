from smtplib import SMTPAuthenticationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from webapps import settings

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
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    picture = models.FileField()

    def __str__(self):
        return 'Picture of ' + self.food.name


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.CASCADE)
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
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
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
    tips_percentage = models.FloatField(default=0.18)

    def __str__(self):
        return 'Order ' + str(self.id) + ' for ' + self.customer.username
    
    @property
    def tips(self):
        return round(self.total_price * self.tips_percentage, 2)
    
    @property
    def tax(self):
        return round(self.total_price * 0.07, 2)
    
    @property
    def total_after_tax_tips(self):
        return round(self.total_price * (1 + 0.07 + self.tips_percentage), 2)
    


class Table(models.Model):
    orders = models.ManyToManyField(Order, related_name="table", blank=True, editable=True)
    # customer = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, editable=True, null=True)
    open_time = models.TimeField(default='10:00', editable=True)
    close_time = models.TimeField(default='21:00', editable=True)
    capacity = models.IntegerField(editable=True)

    def __str__(self):
        return  'Table ID: '+ str(self.id) + ' Capacity: ' + str(self.capacity)
    

# one order will only be assign to one table
class OrderTable(models.Model):
    order = models.OneToOneField(Order, related_name='order_table', on_delete=models.CASCADE)
    table = models.ForeignKey(Table, related_name='order_table', on_delete=models.CASCADE)

    def __str__(self):
        return 'Order ' + str(self.order.id) + ' at Table ' + str(self.table.id)
    

# class UnconfirmedReservation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.PROTECT)
#     num_customers = models.IntegerField(blank=False)
#     date = models.DateField(editable=True, blank=False)
#     time = models.TimeField(editable=True, blank=False)
#     table = models.ForeignKey(Table, on_delete=models.PROTECT)

class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservations', null=True)
    number_customers = models.IntegerField(blank=False)
    table = models.ForeignKey(Table, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=200, editable=True, blank=False)
    last_name = models.CharField(max_length=200, editable=True, blank=False)
    phone_number = models.CharField(max_length=200, editable=True, blank=False)
    email = models.EmailField(max_length=200, editable=True, blank=False, null=True)
    comment = models.CharField(max_length=200, editable=True, blank=True)
    date = models.DateField(editable=True, blank=False)
    time = models.TimeField(editable=True, blank=False)

    def save(self, *args, **kwargs):
        # Check if this is a new reservation
        if not self.pk:
            is_new_reservation = True
        else:
            is_new_reservation = False

        # Call the original save method
        super(Reservation, self).save(*args, **kwargs)

        # If this is a new reservation, send an email
        if is_new_reservation:
            subject = f'New Reservation for {self.first_name} {self.last_name}'
            message = f'A new reservation has been made by {self.first_name} {self.last_name} for {self.date} at {self.time}. \n Thank you for your reservation!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [self.email]

            try:
                print('Sending email...')
                send_mail(subject, message, from_email, recipient_list)
                print('Email sent successfully.')
            except SMTPAuthenticationError:
                print("Email could not be sent. Authentication error.")
            except Exception as e:
                print(f"Email could not be sent. Error: {e}")

# automatically create a profile for a new user if a new superuser is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            Profile.objects.create(user=instance)
            instance.first_name = instance.username
            instance.save()
            instance.profile.save()
