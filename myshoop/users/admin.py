from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from.models import AdditionalData


CustomUser = get_user_model()

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ['email', 'username',]

admin.site.register(CustomUser, CustomUserAdmin)

