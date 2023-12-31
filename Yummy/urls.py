"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from Yummy import views
from django.urls import path

urlpatterns = [
    path('', views.global_action, name='home'),
    path('login', views.login_action, name='login'),
    path('register', views.register_action, name='register'),
    path('logout', views.logout_action, name='logout'),
    path('reserve', views.reserve_action, name='reserve'),
    path('option', views.option_action, name='option'),
    path('summary', views.summary_action, name='summary'),
    path('profile', views.profile_action, name='profile'),
    path('dish/<int:id>', views.dish_action, name='dish'),
    path('favorite_food_action/', views.favorite_food_action, name="favorite_food_action"),
    path('add_food/', views.add_food, name='add_food'),
    path('new_dish', views.new_dish_action, name='new_dish'),
    path('register_staff', views.register_staff_action, name='register_staff'),
    path('get_order_total_price/', views.get_order_total_price, name='get_order_total_price'),
    path('set_take_out/', views.set_take_out, name='set_take_out'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('new_tables', views.new_tables_actions, name='new_tables'),
    path('view_orders', views.view_orders_action, name='view_orders'),
    path('cancel_reservation_action/<int:id>', views.cancel_reservation_action, name='cancel_reservation_action'),
    path('get_comments/', views.get_comments, name='get_comments'),
    path('favorite_count/<int:item_id>/', views.get_favorite_count, name='favorite_count'),
    path('fetch_events/', views.fetch_events, name='fetch_events'),
    path('complete_order/<int:order_id>/', views.complete_order_action, name='complete_order'),
    path('delete_dish/<int:dish_id>/', views.delete_dish_action, name='delete_dish'),
    path('edit_dish/<int:dish_id>/', views.edit_dish_action, name='edit_dish'),
    path('api/order/', views.OrderAPIView.as_view(), name='order_api'),
    path('delete_comment_action/<int:id>', views.delete_comment_action, name='delete_comment_action'),
    path('get_tips', views.get_tips, name='get_tips'),
]
