import collections
import datetime
import json
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.contrib import admin

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
    messages.success(request, 'Logged out successfully.')
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

    return render(request, 'Yummy/menu.html', response_data)


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
            order, created = Order.objects.get_or_create(customer=user, is_paid=False, is_completed=False,
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

            return JsonResponse({"success": True, "total_price": order.total_price, "food_quantity": food_set.quantity},
                                status=200)

        except (Food.DoesNotExist, FoodSet.DoesNotExist):
            return JsonResponse({"success": False}, status=400)

    return JsonResponse({"success": False}, status=405)  # Method not allowed


@login_required
def get_order_total_price(request):
    user = request.user

    try:
        order = Order.objects.get(customer=user, is_paid=False, is_completed=False)
        food_quantities = order.foods.values('food_id', 'quantity')
        return JsonResponse(
            {"success": True, "order_id": order.id, "total_price": order.total_price,
             "food_quantities": list(food_quantities)}, status=200)
    except Order.DoesNotExist:
        return JsonResponse({"success": False}, status=400)


@login_required
def reserve_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = ReservationForm()
        return render(request, 'Yummy/reserve.html', context)

    new_filter = {
        'date': request.POST['date'],
        'start_time': datetime.datetime.strptime(request.POST['time'], '%H:%M').time(),
        'end_time': (datetime.datetime.strptime(request.POST['time'], '%H:%M') + datetime.timedelta(hours=2)).time(),
        'number_customers': request.POST['number_customers']
    }

    tables = Table.objects.filter(
        capacity__gte=new_filter['number_customers'],
        open_time__lte=new_filter['start_time'],
        close_time__gte=new_filter['end_time']
    )

    reservations = Reservation.objects.filter(
        date = new_filter['date'],
        time__range = ((datetime.datetime.strptime(request.POST['time'], '%H:%M') - datetime.timedelta(hours=2)).time()
                       , datetime.datetime.strptime(request.POST['time'], '%H:%M').time())
    )
    unavailable_tableid = [reservation.table.id for reservation in reservations]
    filtered_tables = tables.exclude(id__in=unavailable_tableid)

    if len(filtered_tables) == 0:
        context['form'] = ReservationForm(initial={
            'date': new_filter['date'],
            'time': new_filter['start_time'],
            'number_customers': new_filter['number_customers'],
            'first_name': request.POST['first_name'],
            'last_name': request.POST['last_name'],
            'phone_number': request.POST['phone_number']
        })
        context['reserve_message'] = 'Sorry, no available table at that time. Please try another time.'
        return render(request, 'Yummy/reserve.html', context)

    new_reservation = Reservation(
        table=filtered_tables[0],
        date=new_filter['date'],
        time=new_filter['start_time'],
        number_customers=new_filter['number_customers'],
        first_name=request.POST['first_name'],
        last_name=request.POST['last_name'],
        phone_number=request.POST['phone_number'],
        comment = request.POST['comment']
    )
    new_reservation.save()
    context['reserve_message'] = 'You are all set. Enjoy your meal!'
    context['table_reserved'] = True
    return render(request, 'Yummy/reserve.html', context)


@login_required
def option_action(request):
    context = {}
    response = get_order_total_price(request)
    json_response = json.loads(response.content)
    print(json_response)
    if json_response['success']:
        order_id = json_response['order_id']
        context['order_id'] = order_id
        return render(request, 'Yummy/option.html', context)
    else:
        messages.warning(request, 'Your cart is empty. Please at least add 1 dish to your cart.')
        return redirect('home')


@login_required
@csrf_exempt
def set_take_out(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        print(action)

        try:
            order = Order.objects.get(id=order_id)
            if action == 'take-out':
                order.is_takeout = True
                order.save()
                # if the order is take out and OrderTable exists, need to delete the OrderTable object for this order
                if OrderTable.objects.filter(order=order).exists():
                    OrderTable.objects.filter(order=order).delete()
                    
            if action == 'dine-in':
                order.is_takeout = False
                order.save()
                if 'table_number' not in request.POST or request.POST['table_number'] == '':
                    return JsonResponse({"success": False, "error_message": "Please enter a valid table number."}, status=400)
                else:
                    table_number = request.POST['table_number']
                    try:
                        table = Table.objects.get(id=table_number)
                        if OrderTable.objects.filter(order=order).exists():
                            order_table = OrderTable.objects.get(order=order)
                            order_table.table = table
                            table.orders.add(order)
                            order_table.save()
                            order.save()
                            table.save()
                        else:
                            new_order_table = OrderTable.objects.create(order=order, table=table)
                            new_order_table.save()
                        
                    except Table.DoesNotExist:
                        return JsonResponse({"success": False, "error_message": "Please enter a valid table number."}, status=400)
                
            return JsonResponse({"success": True, 'Cache-Control': 'no-cache'}, status=200)
        except (Order.DoesNotExist):
            return JsonResponse({"success": False}, status=400)


@login_required
def summary_action(request):
    context = {}
    user = request.user
    response = get_order_total_price(request)
    json_response = json.loads(response.content)
    order_id = json_response['order_id']

    order = Order.objects.get(id=order_id)
    if not order.is_takeout:
        order_table = get_object_or_404(OrderTable, order=order)
        table = order_table.table
        context['table'] = table

    food_set = order.foods.all()
    context['order'] = order
    context['food_set'] = food_set
    context['pretax'] = order.total_price
    context['tax'] = round(order.total_price * 0.07, 2)
    context['tips'] = round(order.total_price * 0.18, 2)
    context['total'] = order.total_price + context['tax'] + context['tips']

    return render(request, 'Yummy/summary.html', context)


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


def dish_action(request, id):
    target_food = Food.objects.get(id=id)
    context = {}
    context['comment_form'] = CommentForm()
    context['comments'] = target_food.comments.all().order_by('creation_time').reverse
    context['f'] = target_food
    if request.user.is_authenticated:
        profiles = Profile.objects.get(user=request.user)
        context['favorite_list'] = [x.name for x in profiles.favorite.all()]

    if 'text' in request.POST:
        new_comment = Comment.objects.create(text=request.POST['text'],
                               creation_time=timezone.now(),
                               creator=request.user,)
        new_comment.post_under.add(target_food)
    return render(request, 'Yummy/dish.html', context)


@login_required
def favorite_food_action(request):
    # Get my info first
    my_info = Profile.objects.get(user=request.user)

    # Get the food_id and action from the request data
    food_id = request.POST.get('food_id')
    action = request.POST.get('action')

    # Get the food item
    curr_food = get_object_or_404(Food, id=food_id)

    if action == 'favorite':
        my_info.favorite.add(curr_food)
    elif action == 'unfavorite':
        my_info.favorite.remove(curr_food)

    my_info.save()

    return JsonResponse({'success': True})


@login_required
@staff_member_required
def new_dish_action(request):
    context = {}
    user = request.user
    # All the staff (including super user) can add new dishes
    if not user.is_staff:
        messages.error(request, 'You are not authorized to use this function.')
        return redirect('home')
    else:
        if request.method == 'POST':
            form = FoodForm(data=request.POST, files=request.FILES)
            if not form.is_valid():
                print(form.errors)
                context['message'] = form.errors
                context['form'] = form
                return render(request, 'Yummy/new_dish.html', context)

            name = form.cleaned_data['dish_name']
            price = form.cleaned_data['price']
            desc = form.cleaned_data['description']
            calories = form.cleaned_data['calories']
            category = form.cleaned_data['category']
            is_spicy = form.cleaned_data['is_spicy']
            is_vegetarian = form.cleaned_data['is_vegetarian']
            picture = form.cleaned_data['picture']

            # get the Category object with var. category
            category = Category.objects.get(name=category)

            # create new objects
            new_dish = Food.objects.create(name=name, price=price, description=desc, category=category,
                                           calories=calories, is_spicy=is_spicy, is_vegetarian=is_vegetarian)
            new_picture = FoodPicture.objects.create(food=new_dish, picture=picture)
            print('created new dish')

            # get the picture directory from FoodPicture object
            new_dish.picture_dir = 'img/' + new_picture.picture.name
            new_dish.save()
            messages.success(request, 'New dish created')
            return redirect('home')

        else:
            form = FoodForm()
            return render(request, 'Yummy/new_dish.html', {'form': form})


@login_required
def register_staff_action(request):
    context = {}
    if request.user.is_superuser:
        if request.method == "GET":
            context['form'] = RegisterForm()
            return render(request, "Yummy/register_staff.html", context)

        form = RegisterForm(request.POST)
        context['form'] = form

        if not form.is_valid():
            context['message'] = form.errors
            return render(request, "Yummy/register_staff.html", context)

        user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        is_staff=True)

        user.save()
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        # login(request, user)
        # Create profile for this new user
        new_profile = Profile(user=user, phone_number=form.cleaned_data['phone_number'])
        new_profile.save()
        message = 'New staff ' + user.first_name + ' ' + user.last_name + ' created.'
        messages.success(request, message)
        return redirect('home')


@login_required
def checkout(request):
    curr_profile = get_object_or_404(Profile, id=request.user.id)
    context = {"profile":curr_profile}
    print(curr_profile.phone_number)
    return render(request, "Yummy/checkout.html", context)

@login_required
def payment_success(request):
    context = {}
    return render(request, "Yummy/payment_success.html", context)