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
    path('order', views.order_action, name='order'),

]
