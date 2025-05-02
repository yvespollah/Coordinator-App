from django.apps import AppConfig
from .sub import subscribe_to_manager_channel
import threading


class ManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manager'

    def ready(self):
        from coordinator_project.db import connect_db
        connect_db()
        threading.Thread(target=subscribe_to_manager_channel, daemon=True).start()
