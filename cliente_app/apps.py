# cliente_app/apps.py
from django.apps import AppConfig

class ClienteAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cliente_app'

    def ready(self):
        import cliente_app.signals  # ✅ Este é o correto
