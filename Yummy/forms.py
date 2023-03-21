from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from Yummy.models import *


# from phonenumber_field.modelfields import PhoneNumberField

# https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-a-phone-number-in-django-models

MAX_USERNAME_LENGTH = 20
MAX_PASSWORD_LENGTH = 20
MAX_NAME_LENGTH = 20
MAX_PHONE_LENGTH = 20
MAX_COMMENTS_LENGTH = 100
MAX_UPLOAD_SIZE = 250000000

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label='Username')
    password = forms.CharField(max_length=200, label='Password', widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200,
                               label='Password',
                               widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=200,
                                       label='Confirm Password',
                                       widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=20, label='First Name')
    last_name = forms.CharField(max_length=20, label='Last Name')
    phone_number = forms.CharField(max_length=50, label='Phone Number')

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ReservationForm(forms.Form):
    first_name = forms.CharField(max_length=MAX_NAME_LENGTH, label="First Name")
    last_name = forms.CharField(max_length=MAX_NAME_LENGTH, label="Last Name")
    phone_number = forms.CharField(max_length=MAX_PHONE_LENGTH, label="Phone Number")
    comment = forms.CharField(max_length=MAX_COMMENTS_LENGTH, label="Special Comment")
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
