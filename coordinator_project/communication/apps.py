from django.apps import AppConfig
from coordinator_project.db import connect_db

class CommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communication'

    def ready(self):
        """Initialize the communication module"""
        # Connect to MongoDB
        connect_db()
        
        # Import and initialize the communication manager
        from .coordinator import Coordinator
        
        # Start the coordinator in a separate thread
        import threading
        coordinator = Coordinator()
        threading.Thread(target=coordinator.run, daemon=True).start()
