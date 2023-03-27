import collections

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from Yummy.models import *
from .forms import *


def login_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, "Yummy/login.html", context)

    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'Yummy/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('home'))


def register_action(request):
    context = {}
    if request.method == "GET":
        context['form'] = RegisterForm()
        return render(request, "Yummy/register.html", context)

    form = RegisterForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        context['message'] = form.errors
        return render(request, "Yummy/register.html", context)

    user = User.objects.create_user(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password'],
                                    first_name=form.cleaned_data['first_name'],
                                    last_name=form.cleaned_data['last_name'])

    user.save()
    user = authenticate(username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'])
    login(request, user)
    # Create profile for this new user
    new_profile = Profile(user=request.user, phone_number=form.cleaned_data['phone_number'])
    new_profile.save()

    return redirect('home')


# Create your views here.
def global_action(request):
    response_data = collections.defaultdict(list)
    # {'Meat': [{}, {}], 'Soup': [{}, {}], 'categories' = ['Meat', 'Soup']}
    # {'categories' : ['meat', 'soup'], 'foods': [[{}, {}], []]}
    for model_item in Food.objects.all():
        my_item = {
            "id": model_item.id,
            "name": model_item.name,
            "price": model_item.price,
            "description": model_item.description,
            "picture_dir": model_item.picture_dir,
            "category": model_item.category,
            "calories": model_item.calories,
            "is_spicy": model_item.is_spicy,
            "is_vegetarian": model_item.is_vegetarian,
        }
        if model_item.category.name not in response_data['categories']:
            response_data['categories'].append(model_item.category.name)
        curr_index = response_data['categories'].index(model_item.category.name)
        if curr_index >= len(response_data['foods']):
            response_data['foods'].append([my_item])
        else:
            response_data['foods'][curr_index].append(my_item)
    # print(Profile.objects.get(user=request.user))
    if request.user.is_authenticated:
        profiles = Profile.objects.get(user=request.user)
        response_data['favorite_list'] = [x.name for x in profiles.favorite.all()]

    return render(request, 'Yummy/home.html', response_data)


@login_required
@csrf_exempt
def add_food(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 1))
        user = request.user

        try:
            food = Food.objects.get(id=food_id)

            # Get or create the ongoing order for the user (is_paid=False)
            order, created = Order.objects.get_or_create(customer=user, is_paid=False,
                                                         defaults={'total_price': 0, 'is_takeout': False,
                                                                   'order_time': timezone.now()})

            if action == 'add':
                # Get or create the FoodSet with the specified food
                food_set, created = FoodSet.objects.get_or_create(food=food, defaults={'quantity': 0})

                # If the FoodSet was not created, it may already be related to an order
                if not created and food_set.orders.filter(id=order.id).exists():
                    # The FoodSet already exists and is related to this order, so increment the quantity
                    food_set.quantity += quantity
                else:
                    # The FoodSet is not related to this order, so set the initial quantity
                    food_set.quantity = quantity

                food_set.save()

                # Add the FoodSet to the order's foods field
                order.foods.add(food_set)

                # Update the order's total price
                order.total_price += food.price * quantity
                order.save()

            elif action == 'remove':
                food_set = FoodSet.objects.get(food=food, orders=order)
                food_set.quantity -= quantity
                if food_set.quantity <= 0:
                    food_set.delete()
                else:
                    food_set.save()

                # Update the order's total price
                order.total_price -= food.price * quantity
                order.save()

            return JsonResponse({"success": True}, status=200)

        except (Food.DoesNotExist, FoodSet.DoesNotExist):
            return JsonResponse({"success": False}, status=400)

    return JsonResponse({"success": False}, status=405)  # Method not allowed


@login_required
def reserve_action(request):
    context = {}
    context['form'] = ReservationForm
    return render(request, 'Yummy/reserve.html', context)


@login_required
def order_action(request):
    return render(request, 'Yummy/order.html', {})


@login_required
def option_action(request):
    return render(request, 'Yummy/option.html', {})


@login_required
def summary_action(request):
    return render(request, 'Yummy/summary.html', {})


@login_required
def profile_action(request):
    context = {}

    profile = request.user.profile

    # form = ProfileForm(request.POST, request.FILES, instance=new_item)
    if request.method == "GET":
        context['item'] = profile
        context['favorite'] = profile.favorite.all()
        return render(request, 'Yummy/profile.html', context)

    return render(request, 'Yummy/profile.html', context)


def dish_action(request):
    return render(request, 'Yummy/dish.html', {})


@login_required
def favorite_food_action_menu(request, id):
    # Get my info first
    my_info = Profile.objects.get(user=request.user)

    # Add otherid into my following
    curr_food = get_object_or_404(Food, id=id)
    print("curr food's name", curr_food.name)

    my_info.favorite.add(curr_food)
    my_info.save()

    print("my_info", my_info)
    for food in my_info.favorite.all():
        print(food.name)
    print("=====================")

    return redirect(reverse('home'))


@login_required
def unfavorite_food_action_menu(request, id):
    # Get my info first
    my_info = Profile.objects.get(user=request.user)

    # Add otherid into my following
    curr_food = get_object_or_404(Food, id=id)

    my_info.favorite.remove(curr_food)
    my_info.save()
    return redirect(reverse('home'))
