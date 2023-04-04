from django.contrib import admin
from django.urls import path

from Yummy.models import *
from Yummy.forms import FoodForm


# # Register your models here.
admin.site.register(Food)
admin.site.register(FoodPicture)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(FoodSet)
admin.site.register(Comment)

