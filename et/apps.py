
from django.apps import AppConfig


class EtConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "et"

    # Do NOT access the DB here. Keep ready() empty or use signals that run after migrations.
    def ready(self):
        # keep empty to avoid "Accessing the database during app initialization" warnings
        return
