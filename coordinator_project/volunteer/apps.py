from django.apps import AppConfig


class VolunteerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'volunteer'

    def ready(self):
        from coordinator_project.db import connect_db
        connect_db()