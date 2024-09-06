from django.apps import AppConfig


class UniworldConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'uniworld'

    def ready(self):
        import uniworld.signals
