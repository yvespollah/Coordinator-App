"""
Configuration des routes WebSocket pour la communication en temps réel.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Route pour la connexion WebSocket Redis
    # Format: ws://127.0.0.1:8090/ws/redis/?token=xxx&type=manager
    re_path(r'ws/redis/$', consumers.RedisConsumer.as_asgi()),
]
