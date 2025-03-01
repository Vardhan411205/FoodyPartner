from django.apps import AppConfig


class JooConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'joo'

    def ready(self):
        pass  # No signals to import anymore
