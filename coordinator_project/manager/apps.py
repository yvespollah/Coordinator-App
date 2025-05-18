from django.apps import AppConfig



class ManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manager'

    def ready(self):
        from coordinator_project.db import connect_db
        connect_db()

