"""
Modèles pour le module de communication.
Gère les canaux et les permissions.
"""

from mongoengine import Document, StringField, ListField, BooleanField, DateTimeField
from datetime import datetime

class Channel(Document):
    """
    Représente un canal de communication Redis.
    
    Attributes:
        name: Nom du canal (ex: 'tasks/submission')
        description: Description du canal
        created_at: Date de création
        active: Si le canal est actif
        require_auth: Si l'authentification est requise pour ce canal
        allowed_publishers: Liste des rôles autorisés à publier
        allowed_subscribers: Liste des rôles autorisés à s'abonner
    """
    name = StringField(required=True, primary_key=True)
    description = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    active = BooleanField(default=True)
    require_auth = BooleanField(default=False)
    allowed_publishers = ListField(StringField(), default=list)
    allowed_subscribers = ListField(StringField(), default=list)
    
    meta = {
        'collection': 'channels',
        'indexes': ['name', 'active']
    }
    
    def __str__(self):
        return f"{self.name} - {self.description}"
