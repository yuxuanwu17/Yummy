from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from Yummy.models import *
from .forms import *


# Create your views here.
def login_action(request):
    context = {}
    if request.method == "GET":
        logout(request)
        context['form'] = LoginForm
        return render(request, "Yummy/login.html", context)

    form = LoginForm(request.POST)
    if not form.is_valid():
        context['message'] = form.errors
        context['form'] = LoginForm
        return render(request, "Yummy/login.html", context)

    user = authenticate(username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'])

    if user is None:
        context['message'] = 'Invalid username/password'
        context['form'] = LoginForm
        return render(request, "Yummy/login.html", context)

    login(request, user)

    return redirect('option')


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

    user = User.objects.create_user(form.cleaned_data['username'],
                                    form.cleaned_data['password'],
                                    first_name=form.cleaned_data['first_name'],
                                    last_name=form.cleaned_data['last_name'], )
    user.save()

    login(request, user)
    # Create profile for this new user
    new_profile = Profile(user=request.user, phone_number=form.cleaned_data['phone_number'])
    new_profile.save()

    return redirect('option')


# Create your views here.
def global_action(request):
    return render(request, 'Yummy/base.html', {})
