from allauth.account.forms import SignupForm, SetPasswordField, UserForm, LoginForm
from django import forms
from django.db import transaction
from allauth.account import app_settings
from allauth.utils import set_form_field_order
from .custom_validators import validate_sign, validate_length, validate_number
from django.contrib.auth import get_user_model
from .models import Book_Rate

class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop(
            "render_value", app_settings.PASSWORD_INPUT_RENDER_VALUE
        )
        kwargs["widget"] = forms.PasswordInput(
            render_value=render_value,
            attrs={"placeholder": kwargs.get("label"), "class": "form-control"},
        )
        autocomplete = kwargs.pop("autocomplete", None)
        kwargs["widget"].attrs["autocomplete"] = autocomplete
        super(PasswordField, self).__init__(*args, **kwargs)


class CustomSignupForm(SignupForm):
    lista_województw = (
        ('1', 'Dolnośląskie'),
        ('2', 'Kujawsko-Pomorskie'),
        ('3', 'Lubelskie'),
        ('4', 'Lubuskie'),
        ('5', 'Łódzkie'),
        ('6', 'Małopolskie'),
        ('7', 'Mazowieckie'),
        ('8', 'Opolskie'),
        ('9', 'Podkarpackie'),
        ('10', 'Podlaskie'),
        ('11', 'Pomorskie'),
        ('12', 'Śląskie'),
        ('13', 'Świętokrzyskie'),
        ('14', 'Warmińsko-Mazurskie'),
        ('15', 'Wielkopolskie'),
        ('16', 'Zachodniopomorskie'),
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": "Adres email",
                "autocomplete": "email",
                "class": "form-control",
                "aria-describedby":  "emailHelp"
            }
        )
    )
    first_name = forms.CharField(max_length=30, label="Imię", widget=forms.TextInput(attrs={"class": "form-control"},))
    last_name = forms.CharField(max_length=30, label="Nazwisko", widget=forms.TextInput(attrs={"class": "form-control"},))
    city = forms.CharField(max_length=20, label='Miejscowość', widget=forms.TextInput(attrs={"class": "form-control"},))
    region = forms.CharField(widget=forms.Select(choices=lista_województw, attrs={"class": "custom-select custom-select-sm"},))
    address = forms.CharField(max_length=30, label="Ulica + numer domu, mieszkania", widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby":  "addressHelp"},))
    postal_code = forms.CharField(max_length=6, label="Kod pocztowy xx-xxx", widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby":  "postalHelp"},))
    phone_number = forms.IntegerField(localize=True, label="Numer teleffonu", widget=forms.NumberInput(attrs={"class": "form-control"},))
    reg = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={"class": "form-check-input", "aria-describedby":  "regulaminHelp", "type": "checkbox"},))
    postal_code.validators.append(validate_sign)
    postal_code.validators.append(validate_length)
    phone_number.validators.append(validate_number)
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(
            label=("Hasło"), autocomplete="new-password"
        )
        self.fields["password2"] = PasswordField(label=("Podaj hasło jeszcze raz"))

class CustomLoginForm(LoginForm):
    password = PasswordField(label=("Hasło"), autocomplete="current-password")
    remember = forms.BooleanField(label=("Pamiętaj mnie"), required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input", "type": "checkbox"},))

    def __init__(self, *args, **kwargs):
        login_widget = forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": ("E-mail address"),
                "autocomplete": "email",
                "class": "form-control",
            }
        )
        login_field = forms.EmailField(label=("E-mail"), widget=login_widget)
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["login"] = login_field
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]

class CommentForm(forms.Form):
    subject = forms.CharField(min_length=2, max_length=30, label='temat', widget=forms.TextInput(attrs={"class": "form-control", "id": "subject"},))
    content = forms.CharField(min_length=20, max_length=500, widget=forms.Textarea(attrs={"class": "form-control", "rows": 5, "id": "content"}))

class NumberOfItems(forms.Form):
    num = forms.IntegerField(min_value=1, max_value=99, initial=1, widget=forms.NumberInput(attrs={"class": "form-control", "id": "number"}))
