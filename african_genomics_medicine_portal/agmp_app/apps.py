from django.apps import AppConfig


class AgmpAppConfig(AppConfig):
    name = 'agmp_app'
    default_auto_field = 'django.db.models.BigAutoField'

    #removed auto generated latitude and longitude values
    # def ready(self):
    #     import agmp_app.signals


