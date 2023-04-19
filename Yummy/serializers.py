from rest_framework import serializers
from .models import Food, FoodSet, Order

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'

class FoodSetSerializer(serializers.ModelSerializer):
    food = FoodSerializer()

    class Meta:
        model = FoodSet
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    foods = FoodSetSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
