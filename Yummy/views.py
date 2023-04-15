import collections
import datetime
import json
from django.contrib import messages
import os

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
import datetime
from Yummy.models import *
from .forms import *
from dateutil.parser import parse


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

    return redirect(reverse('home'))


# display pre-stored dishes
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

    if request.user.is_authenticated:
        profiles, _ = Profile.objects.get_or_create(user=request.user)
        print(profiles)
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

        order_total = 0.0
        for foodset in food_quantities:
            price = Food.objects.get(id=foodset['food_id']).price
            quantity = foodset['quantity']
            order_total += price * quantity
        order.total_price = order_total
        order.save()

        return JsonResponse(
            {"success": True, "order_id": order.id, "total_price": order.total_price,
             "food_quantities": list(food_quantities)}, status=200)
    except Order.DoesNotExist:
        return JsonResponse({"success": False}, status=400)


@login_required
def reserve_action(request):
    context = {}
    user = request.user
    if request.method == 'GET':
        context['form'] = ReservationForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.profile.phone_number, })
        return render(request, 'Yummy/reserve.html', context)

    new_filter = {
        'date': request.POST['date'],
        'start_time': datetime.datetime.strptime(request.POST['time'], '%H:%M').time(),
        'end_time': (datetime.datetime.strptime(request.POST['time'], '%H:%M') + datetime.timedelta(hours=2)).time(),
        'number_customers': request.POST['number_customers']
    }

    # tables = Table.objects.filter(
    #     capacity__gte=new_filter['number_customers'],
    #     open_time__gte=new_filter['start_time'],
    #     close_time__lte=new_filter['end_time']
    # )
    # Initial tables filtering
    tables = Table.objects.filter(capacity__gte=new_filter['number_customers'])
    # Filter by start_time
    tables = tables.filter(open_time__lte=new_filter['start_time'])
    # Filter by end_time
    tables = tables.filter(close_time__gte=new_filter['end_time'])

    reservations = Reservation.objects.filter(
        date=new_filter['date'],
        time__range=((datetime.datetime.strptime(request.POST['time'], '%H:%M') - datetime.timedelta(hours=2)).time()
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
        customer=user,
        table=filtered_tables[0],
        date=new_filter['date'],
        time=new_filter['start_time'],
        number_customers=new_filter['number_customers'],
        first_name=request.POST['first_name'],
        last_name=request.POST['last_name'],
        phone_number=request.POST['phone_number'],
        comment=request.POST['comment']
    )
    new_reservation.save()
    context['reserve_message'] = 'You are all set. Enjoy your meal!'
    context['table_reserved'] = True
    return render(request, 'Yummy/reserve.html', context)

@csrf_exempt
def fetch_events(request):
    start_date_str = request.GET.get('start', None)
    end_date_str = request.GET.get('end', None)
    print("start, end input")
    print(start_date_str, end_date_str)
    if start_date_str and end_date_str:
        start_date = parse(start_date_str).date()
        end_date = parse(end_date_str).date()

        reservations = Reservation.objects.filter(date__range=[start_date, end_date])
        reserved_tables = reservations.values('date', 'time', 'number_customers').annotate(total=Count('table'))
        total_tables = Table.objects.count()

        print(total_tables)

        event_list = []

        for reserved in reserved_tables:
            date = reserved['date']
            time = reserved['time']
            number_customers = reserved['number_customers']
            total_reserved = reserved['total']

            available_tables = total_tables - total_reserved

            event_list.append({
                'title': f'Available Tables: {available_tables}',
                'start': datetime.datetime.combine(date, time).strftime('%Y-%m-%dT%H:%M:%S'),
                'end': (datetime.datetime.combine(date, time) + datetime.timedelta(hours=2)).strftime(
                    '%Y-%m-%dT%H:%M:%S'),
                'color': 'red' if available_tables == 0 else 'transparent',
                'textColor': 'transparent',
                'rendering': 'background',
                'available_tables': available_tables
            })

        return JsonResponse(event_list, safe=False)


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
    user = request.user
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')

        OPEN_TIME = datetime.time(10,00,00)
        CLOSE_TIME = datetime.time(21,00,00)
        print(datetime.datetime.now().time())
        if datetime.datetime.now().time() < OPEN_TIME or datetime.datetime.now().time() > CLOSE_TIME:
            print('Close')
            return JsonResponse({"success": False, "error_message": "Sorry we are closed now."},
                                        status=400)
        else:
            print('opening')

        try:
            order = Order.objects.get(id=order_id)
            if action == 'take-out':
                order.is_takeout = True
                order.save()
                # if the order is take out and OrderTable exists, need to delete the OrderTable object for this order
                if OrderTable.objects.filter(order=order).exists():
                    OrderTable.objects.filter(order=order).delete()

            elif action == 'dine-in':
                order.is_takeout = False
                order.save()
                
                if 'party_size' not in request.POST or request.POST['party_size'] == '':
                    return JsonResponse({"success": False, "error_message": "Please enter a valid number for your party size."},
                                        status=400)
                else:
                    # check if customer have any reservation 
                    # customer can order either 30 minutes before their reservation, or 1.5 hour after the reservation
                    user_reservation = Reservation.objects.filter(customer=user, date=datetime.datetime.today(),
                                                                  time__range=((datetime.datetime.now() - datetime.timedelta(hours=2)).time(),
                                                                               (datetime.datetime.now() - datetime.timedelta(minutes=30)).time()))
                    
                    if user_reservation:
                        print(user_reservation)
                        reserved_table = user_reservation[0].table
                        # if OrderTable.objects.filter(order=order).exists():
                        try:
                            order_table = OrderTable.objects.get(order=order)
                            order_table.table = reserved_table
                            order_table.save()
                            order.save()
                        except OrderTable.DoesNotExist:
                            new_order_table = OrderTable.objects.create(order=order, table=reserved_table)
                            new_order_table.save()

                    else:
                        # if no reservation, find an available table and assign to this order
                        party_size = request.POST['party_size']

                        new_filter = {
                            'date': datetime.date.today(),
                            'start_time': datetime.datetime.now().time(),
                            'end_time': (datetime.datetime.now() + datetime.timedelta(hours=2)).time(),
                            'number_customers': party_size
                        }
                        print(new_filter)
                        try:
                            # 1. Filter out the tables by capacity and open/close time
                            tables = Table.objects.filter(capacity__gte=new_filter['number_customers'])
                            # tables = tables.filter(open_time__lte=new_filter['start_time'])
                            # tables = tables.filter(close_time__gte=new_filter['end_time'])
                            print(tables)

                            # 2. Filter out the tables being reserved within 2 hours before and 2 hours later
                            reservations = Reservation.objects.filter(
                            date=new_filter['date'],
                            time__range=((datetime.datetime.now() - datetime.timedelta(hours=2)).time(),
                                         (datetime.datetime.now() + datetime.timedelta(hours=2)).time())
                            )
                            unavailable_tableid = [reservation.table.id for reservation in reservations]
                            filtered_tables = tables.exclude(id__in=unavailable_tableid)

                            # 3. Filter out the tables which are occupied right now
                            orders = Order.objects.filter(is_takeout = False, order_table__isnull = False,
                                                        order_time__gte=(datetime.datetime.now() - datetime.timedelta(hours=2)))
                                                                            
                            unavailable_tableid = [order.order_table for order in orders]
                            filtered_tables = filtered_tables.exclude(id__in=unavailable_tableid)

                            if len(filtered_tables) == 0:
                                return JsonResponse({"success": False, "error_message": "All tables are being reserved or occupied right now."},
                                                status=400)
                            else:
                                assigned_table = filtered_tables[0]
                            # if OrderTable.objects.filter(order=order).exists():
                            try:
                                order_table = OrderTable.objects.get(order=order)
                                order_table.table = assigned_table
                                order_table.save()
                                order.save()
                            except OrderTable.DoesNotExist:
                                new_order_table = OrderTable.objects.create(order=order, table=assigned_table)
                                new_order_table.save()

                        except Table.DoesNotExist:
                            return JsonResponse({"success": False, "error_message": "Please enter a valid table number."},
                                                status=400)
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

    try:
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
    
    except Order.DoesNotExist:
            message = 'Order ID {} does not exist.'.format(order_id)
            messages.error(request, message)
            return redirect('home')


@login_required
def profile_action(request):
    context = {}
    profile = request.user.profile
    orders = Order.objects.filter(customer=request.user)  # , is_paid = True
    reservations = Reservation.objects.filter(customer=request.user)

    if request.method == "GET":
        context['item'] = profile
        favorite = profile.favorite.all()
        phone_number = profile.phone_number
        context['favorite'] = favorite
        context['phone_number'] = phone_number
        context['reservations'] = reservations.order_by('date','time').reverse
        if len(reservations) == 0:
            context['no_reservation_message'] = "You don't have any reservations."
        if len(favorite) == 0:
            context['no_favorite_message'] = "You don't have any favorite dishes."
        if len(orders) == 0:
            context['no_order_message'] = "You don't have any past orders."
        else:
            context['orders'] = orders.order_by('order_time').reverse
            context['today_date'] = datetime.datetime.today().date()
            context['today_time'] = datetime.datetime.now().time()
    else:
        if 'phone_number' in request.POST:
            phone_number = request.POST['phone_number']
            if len(phone_number) != 10:
                message = 'Invalid phone number'
                messages.warning(request, message)
                return redirect('profile')
            else:
                profile.phone_number = phone_number
                profile.save()
                message = 'Phone number updated successfully. It will take effect from your next reservation.'
                messages.success(request, message)
                return redirect('profile')
        
    return render(request, 'Yummy/profile.html', context)


def cancel_reservation_action(request, id):
    try:
        reservation = Reservation.objects.get(id=id)
        reservation.delete()
        message = 'Reservation canceled.'
        messages.success(request, message)
        return redirect('profile')
    except Reservation.DoesNotExist:
        message = 'Error happened when canceling this reservation. Please contact the restaurant.'
        messages.error(request, message)
        return redirect('profile')


def dish_action(request, id):
    try:
        target_food = Food.objects.get(id=id)
        context = {}
        context['comment_form'] = CommentForm()
        context['comments'] = target_food.comments.all().order_by('creation_time').reverse
        context['f'] = target_food

        # get number of user like this dish
        count = target_food.favoring.count()
        context['count'] = count

        if request.user.is_authenticated:
            profiles = Profile.objects.get(user=request.user)
            context['favorite_list'] = [x.name for x in profiles.favorite.all()]

        if 'text' in request.POST:
            new_comment = Comment.objects.create(text=request.POST['text'],
                                                creation_time=timezone.now(),
                                                creator=request.user, )
            new_comment.post_under.add(target_food)
        return render(request, 'Yummy/dish.html', context)
    except Food.DoesNotExist:
        message = 'Dish with ID {} does not exist.'.format(id)
        messages.error(request, message)
        return redirect('home')


def get_comments(request):
    # values('text', 'creator__first_name', 'creator__last_name', 'creation_time'): This retrieves the specified
    # fields from the filtered comments: 'text', 'creator__first_name', 'creator__last_name', and 'creation_time'.
    # Note that creator__first_name and creator__last_name are used to access the related User model fields
    # 'first_name' and 'last_name', respectively.
    comments = Comment.objects.filter(post_under=request.GET.get('item_id')).values('text', 'creator__first_name',
                                                                                    'creator__last_name',
                                                                                    'creation_time')

    # Convert the creation_time to the desired format
    for comment in comments:
        comment['formatted_creation_time'] = comment['creation_time'].strftime('%B %d, %Y, %I:%M %p')

    return JsonResponse(list(comments)[::-1], safe=False)


def get_favorite_count(request, item_id):
    # Replace this line with the code to get the updated count for the given item_id
    count = Food.objects.get(id=item_id).favoring.count()
    return JsonResponse({"count": count})


@login_required
def favorite_food_action(request):
    # Get my info first
    try:
        my_info = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        message = 'Profile does not exist.'
        messages.error(request, message)
        return redirect('home')

    # Get the food_id and action from the request data
    food_id = request.POST.get('food_id')
    action = request.POST.get('action')

    # Get the food item
    try:
        curr_food = Food.objects.get(id=food_id)

        if action == 'favorite':
            my_info.favorite.add(curr_food)
        elif action == 'unfavorite':
            my_info.favorite.remove(curr_food)

        my_info.save()
        # get number of user like this dish
        count = curr_food.favoring.count()

        return JsonResponse({'success': True, 'num_ppl_fav': count}, status=200)
    
    except Food.DoesNotExist:
        return JsonResponse({'success': False}, status=400)


@login_required
# @staff_member_required
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
            try:
                category = Category.objects.get(name=category)
            except Category.DoesNotExist:
                message = 'Category does not exist'
                messages.error(request, message)
                return redirect('home')

            # create new objects
            new_dish = Food.objects.create(name=name, price=price, description=desc, category=category,
                                           calories=calories, is_spicy=is_spicy, is_vegetarian=is_vegetarian)
            new_picture = FoodPicture.objects.create(food=new_dish, picture=picture)

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

        # Create profile for new staff user
        new_profile = Profile(user=user, phone_number=form.cleaned_data['phone_number'])
        new_profile.save()
        message = 'New staff ' + user.first_name + ' ' + user.last_name + ' created.'
        messages.success(request, message)
        return redirect('home')

    else:
        message = 'You are not authorized to do this action.'
        messages.error(request, message)
        return redirect('home')


@login_required
def checkout(request):
    curr_profile = get_object_or_404(Profile, id=request.user.id)
    context = {"profile": curr_profile}
    print(curr_profile.phone_number)
    return render(request, "Yummy/checkout.html", context)


@login_required
def payment_success(request):
    # change the payment status of the most recent order of current user
    # Get the ongoing order for the user (is_paid=False)
    try:
        order = Order.objects.get(customer=request.user, is_paid=False, is_completed=False)
        # update the order time to the time that customer actually paid and submit order
        order.order_time = datetime.datetime.now()
        order.is_paid = True
        order.save()
        context = {}
        return render(request, "Yummy/payment_success.html", context)
    
    except Order.DoesNotExist:
        message = 'Order does not exist.'
        messages.error(request, message)
        return redirect('home')


@login_required
# @staff_member_required
def new_tables_actions(request):
    context = {}
    user = request.user
    if not user.is_staff:
        message = 'You are not authorized to do this action.'
        messages.error(request, message)
        return redirect('home')

# Display all the tables in the restaurant
    if request.method == "GET":
        results = Table.objects.values('capacity').annotate(dcount=Count('capacity')).order_by()
        context['results'] = results
        return render(request, "Yummy/new_tables.html", context)

    if request.method == "POST":
        if 'capacity' not in request.POST or request.POST['capacity'] == '':
            message = 'Invalid input of capacity, please enter a number'
            messages.error(request, message)
            return redirect('new_tables')
        if 'number_to_add' not in request.POST or request.POST['number_to_add'] == '':
            message = 'Invalid input of number of tables to add, please enter a number'
            messages.error(request, message)
            return redirect('new_tables')

        capacity = float(request.POST['capacity'])
        number_to_add = float(request.POST['number_to_add'])
        if capacity <= 0 or number_to_add <= 0:
            message = 'Input must be greater than zero'
            messages.error(request, message)
            return redirect('new_tables')

        # create tables according to the number and capacity user input
        if capacity.is_integer() and number_to_add.is_integer():
            new_tables = []
            for i in range(int(number_to_add)):
                new_tables.append(Table(capacity=int(capacity)))

            Table.objects.bulk_create(new_tables)
            message = 'New tables added successfully'
            messages.success(request, message)
            results = Table.objects.values('capacity').annotate(dcount=Count('capacity')).order_by()
            context['results'] = results
            return render(request, 'Yummy/new_tables.html', context)

        else:
            message = 'Input must be an integer'
            messages.error(request, message)
            return redirect('new_tables')


@login_required
# @staff_member_required
def view_orders_action(request):
    context = {}
    user = request.user
    if not user.is_staff:
        message = 'You are not authorized to do this action.'
        messages.error(request, message)
        return redirect('home')
    else:
        # can only view the submitted orders
        orders = Order.objects.filter(is_paid=True)
        context['orders'] = orders.order_by('is_completed', '-order_time')
        return render(request, 'Yummy/view_orders.html', context)


@login_required
# @staff_member_required
def complete_order_action(request, order_id):
    user = request.user
    if not user.is_staff:
        message = 'You are not authorized to do this action.'
        messages.error(request, message)
        return redirect('home')
    else:
        try:
            order = Order.objects.get(id=order_id)
            order.is_completed = True
            order.save()
            print(order.is_completed)
            return redirect('view_orders')
        except Order.DoesNotExist:
            message = 'Order ID {} does not exist.'.format(order_id)
            messages.error(request, message)
            return redirect('view_orders')


@login_required
# @staff_member_required
def delete_dish_action(request, dish_id):
    user = request.user
    if not user.is_staff:
        message = 'You are not authorized to do this action.'
        messages.error(request, message)
        return redirect('home')
    else:
        try:
            dish = Food.objects.get(id=dish_id)
            dish_name = dish.name
            dish.delete()
            message = 'Dish '+ dish_name + ' deleted.'
            messages.success(request, message)
            return redirect('home')
        except Food.DoesNotExist:
            message = 'Dish ID {} does not exist.'.format(dish_id)
            messages.error(request, message)
            return redirect('home')
    


@login_required
# @staff_member_required
def edit_dish_action(request, dish_id):
    user = request.user
    context = {}
    if not user.is_staff:
        message = 'You are not authorized to do this action.'
        messages.error(request, message)
        return redirect('home')
    else:
        try:
            dish = Food.objects.get(id=dish_id)
            picture_dir = dish.picture_dir

            try:
                dish_picture = FoodPicture.objects.get(food=dish)
            except FoodPicture.DoesNotExist:  # create a FoodPicture object for Food does not have this object
                # get the directory
                file_path = os.path.abspath(__file__) # /Users/kellyhsieh/s23_team_1/Yummy/views.py
                base_dir = os.path.abspath(os.path.join(file_path, '../'))
                file_name =picture_dir[4:]
                dish_picture = FoodPicture.objects.create(food=dish)
                with open(base_dir+'/static/'+picture_dir, 'rb') as f:
                    dish_picture.picture.save(file_name, f, save=True)

            if request.method == "GET":
                # display form with dish info
                    initial = {'dish_name': dish.name, 'price': dish.price, 'category': dish.category,
                    'description': dish.description, 'calories': dish.calories,
                    'is_spicy': dish.is_spicy, 'is_vegetarian': dish.is_vegetarian}

                    edit_form = FoodForm(initial=initial, disable_clean=True, picture_required=False)
                    context['form'] = edit_form
                    context['dish'] = dish
                    return render(request, 'Yummy/edit_dish.html', context)
            
            elif request.method == "POST":
                # update dish info and save
                form = FoodForm(data=request.POST, files=request.FILES, disable_clean=True, picture_required=False)
                if not form.is_valid():
                    print('form not valid')
                    context['dish'] = dish
                    context['form'] = form
                    context['message'] = form.errors
                    return render(request, 'Yummy/edit_dish.html', context)
                
                context['dish'] = dish
                category = form.cleaned_data['category']
                
                dish.name = form.cleaned_data['dish_name']
                dish.price = form.cleaned_data['price']
                dish.description = form.cleaned_data['description']
                dish.calories = form.cleaned_data['calories']
                dish.category = get_object_or_404(Category, name=category)
                dish.is_spicy = form.cleaned_data['is_spicy']
                dish.is_vegetarian = form.cleaned_data['is_vegetarian']
                dish.save()

                if form.cleaned_data['picture']:
                    new_picture = form.cleaned_data['picture']
                else:
                    # if no new picture uploaded by user, use the original picture.
                    new_picture = dish_picture.picture

                dish_picture.picture = new_picture
                dish.picture_dir = 'img/' + dish_picture.picture.name

                dish.save()
                dish_picture.save()
                print('save new picture')
            
                return redirect('dish', id=dish.id)  
            
        except Food.DoesNotExist:
            message = 'Dish with ID {} does not exist.'.format(dish_id)
            messages.error(request, message)
            return redirect('home')
