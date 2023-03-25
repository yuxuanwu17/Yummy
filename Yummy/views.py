import collections

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
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
    return render(request, 'Yummy/home.html', {})


def test_action(request):
    response_data = collections.defaultdict(list)
    # {'Meat': [{}, {}], 'Soup': [{}, {}], 'categories' = ['Meat', 'Soup']}

    # {'categories' : ['meat', 'soup'], 'foods': [[{}, {}], []]}
    for model_item in Food.objects.all():
        my_item = {
            "name": model_item.name,
            "price": model_item.price,
            "description": model_item.description,
            "picture_dir": model_item.picture_dir,
            "category": model_item.category,
            "calories": model_item.calories,
            "is_spicy": model_item.is_spicy,
            "is_vegetarian": model_item.is_vegetarian
        }
        if model_item.category.name not in response_data['categories']:
            response_data['categories'].append(model_item.category.name)
        curr_index = response_data['categories'].index(model_item.category.name)
        if curr_index >= len(response_data['foods']):
            response_data['foods'].append([my_item])
        else:
            response_data['foods'][curr_index].append(my_item)
    # order_map: define the order of category order

    # get all the category objects
    #category_list = response_data.keys()
    #print(category_list)
    #response_data['categories'] = category_list
    # response_data.append(category)
    # response_data['n'] = range(len(response_data['categories']))
    print(response_data)
    return render(request, 'Yummy/home_test.html', response_data)


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
    return render(request, 'Yummy/profile.html', {})


def dish_action(request):
    return render(request, 'Yummy/dish.html', {})
