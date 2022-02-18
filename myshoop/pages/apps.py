from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = 'pages'
    def ready(self):
        from .signals import add_minipics
