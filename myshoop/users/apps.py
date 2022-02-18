from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    def ready(self):
        from .signals import populate_additional_db




