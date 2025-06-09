from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime

class MessageLog(Document):
    """Modèle pour enregistrer tous les messages pub/sub dans le système"""
    # Informations sur l'expéditeur
    sender_type = StringField(max_length=50, help_text="Type de l'expéditeur (manager, volunteer, coordinator)")
    sender_id = StringField(max_length=255, help_text="ID réel de l'expéditeur")
    
    # Informations sur le destinataire
    receiver_type = StringField(max_length=50, null=True, blank=True, help_text="Type du destinataire")
    receiver_id = StringField(max_length=255, null=True, blank=True, help_text="ID du destinataire si connu")
    
    # Informations sur le message
    channel = StringField(max_length=255, help_text="Canal sur lequel le message a été publié")
    request_id = StringField(max_length=255, help_text="ID de la requête")
    message_type = StringField(max_length=50, help_text="Type du message (request, response)")
    content = StringField(help_text="Contenu du message au format JSON")
    
    # Métadonnées
    timestamp = DateTimeField(default=datetime.now, help_text="Date et heure d'enregistrement du message")
    is_processed = BooleanField(default=False, help_text="Indique si le message a été traité")
    
    class Meta:
        verbose_name = "Log de message"
        verbose_name_plural = "Logs de messages"
        ordering = ["-timestamp"]
        meta = {
        'indexes': [
            'timestamp',
            {'fields': ['message'], 'unique': False},
            {'fields': ['is_processed'], 'unique': False},
            {'fields': ['sender_id'], 'unique': False},
            {'fields': ['receiver_id'], 'unique': False},
            {'fields': ['channel'], 'unique': False},
            {'fields': ['request_id'], 'unique': False},
            {'fields': ['message_type'], 'unique': False},
            {'fields': ['is_processed'], 'unique': False},
        ]
    }
    
    def __str__(self):
        return f"{self.sender_type}:{self.sender_id} -> {self.channel} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
