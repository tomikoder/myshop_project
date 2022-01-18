from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.http import JsonResponse
from django.shortcuts import render
from .custom_signals import user_is_created
from django.core.exceptions import FieldDoesNotExist

def user_field2(user, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if not field:
        return
    User = get_user_model()
    try:
        field_meta = User._meta.get_field(field)
    except FieldDoesNotExist:
        if not hasattr(user, field):
            return
    if args:
        v = args[0]
        setattr(user, field, v)
    else:
        # Getter
        return getattr(user, field)


class MyDefaultAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_email, user_field as user_field1, user_username

        data = form.cleaned_data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        username = data.get("username")
        address = data.get("address")
        region = data.get("region")
        city = data.get("city")
        postal_code = data.get("postal_code")
        postal_code = int(''.join(postal_code.split('-')))
        phone_number = data.get("phone_number")
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field1(user, "first_name", first_name)
        if last_name:
            user_field1(user, "last_name", last_name)
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        user_field1(user, "address", address)
        user_field1(user, "city", city)
        user_field1(user, "region", region)
        user_field2(user, "postal_code", postal_code)
        user_field2(user, "phone_number", phone_number)
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
            user_is_created.send(sender=MyDefaultAdapter)
        return user

    def confirm_email(self, request, email_address):
        """
        Marks the email address as confirmed on the db
        """
        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()

    def respond_email_verification_sent(self, request, user):
        return HttpResponse("Email jest niezweryfikowany.")






