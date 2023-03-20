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
    return redirect(reverse('login'))


def register_action(request):
    context = {}
    if request.method == "GET":
        context['form'] = RegisterForm
        return render(request, "Yummy/register.html", context)

    form = RegisterForm(request.POST)
    if not form.is_valid():
        context['message'] = form.errors
        context['form'] = RegisterForm
        return render(request, "Yummy/register.html", context)

    user = User.objects.create_user(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password'],
                                    first_name=form.cleaned_data['first_name'],
                                    last_name=form.cleaned_data['last_name'])

    user.save()

    login(request, user)
    # Create profile for this new user
    new_profile = Profile(user=request.user, phone_number=form.cleaned_data['phone_number'])
    new_profile.save()

    return redirect('home')


# Create your views here.
def global_action(request):
    return render(request, 'Yummy/home.html', {})


@login_required
def reserve_action(request):
    return render(request, 'Yummy/reserve.html', {})


@login_required
def order_action(request):
    return render(request, 'Yummy/order.html', {})
