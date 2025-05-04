"""
Modèles MongoDB pour le système de coordination.
Utilise MongoEngine comme ODM (Object-Document Mapper).
"""

import secrets
from datetime import datetime, timedelta
from mongoengine import Document, StringField, DictField, DateTimeField, BooleanField, ListField

class ConnectionState(Document):
    """
    État de connexion pour les managers et volunteers.
    Stocké dans la collection 'connection_states' de MongoDB.
    """
    
    # Champs d'identification
    id = StringField(primary_key=True, default=lambda: secrets.token_hex(8))
    type = StringField(required=True, choices=['manager', 'volunteer'])
    token = StringField(required=True, default=lambda: secrets.token_hex(16))
    
    # État de la connexion
    is_connected = BooleanField(default=True)
    last_heartbeat = DateTimeField(default=datetime.utcnow)
    
    # Canaux de communication
    channels = ListField(StringField(), default=list)
    
    # Informations supplémentaires
    name = StringField(required=True)
    location = StringField()  # Ville/Région
    
    # Métadonnées spécifiques au type
    metadata = DictField(default=dict)  # Pour volunteer: CPU, RAM, etc. Pour manager: organisation, etc.
    
    # Configuration MongoDB
    meta = {
        'collection': 'connection_states',
        'indexes': [
            'id',              # Pour recherche rapide par ID
            'type',            # Pour filtrer par type
            'token',           # Pour l'authentification
            'is_connected',    # Pour trouver les connexions actives
            ('type', 'is_connected'),  # Pour les stats par type
            'last_heartbeat'   # Pour le nettoyage des connexions mortes
        ],
        'ordering': ['-last_heartbeat']  # Plus récent d'abord
    }

    def __str__(self):
        """Représentation lisible de l'état"""
        status = 'Connecté' if self.is_connected else 'Déconnecté'
        return f"{self.type}:{self.name} ({self.id}) - {status}"
    
    def update_heartbeat(self):
        """Met à jour le timestamp du dernier heartbeat"""
        self.last_heartbeat = datetime.utcnow()
        self.is_connected = True
        self.save()
    
    def disconnect(self):
        """Marque la connexion comme déconnectée"""
        self.is_connected = False
        self.save()
    
    @property
    def is_active(self):
        """
        Vérifie si la connexion est active basé sur le dernier heartbeat.
        Une connexion est considérée inactive après 5 minutes sans heartbeat.
        """
        if not self.is_connected:
            return False
            
        timeout = datetime.utcnow() - timedelta(minutes=5)
        return self.last_heartbeat > timeout
    
    @classmethod
    def cleanup_inactive(cls):
        """
        Marque comme déconnectées toutes les connexions sans heartbeat
        depuis plus de 5 minutes.
        """
        timeout = datetime.utcnow() - timedelta(minutes=5)
        cls.objects(
            last_heartbeat__lt=timeout,
            is_connected=True
        ).update(
            set__is_connected=False
        )
    
    @classmethod
    def get_stats(cls):
        """
        Retourne des statistiques sur les connexions.
        """
        stats = {
            'total': cls.objects.count(),
            'connected': cls.objects(is_connected=True).count(),
            'managers': cls.objects(type='manager').count(),
            'volunteers': cls.objects(type='volunteer').count(),
            'active_managers': cls.objects(type='manager', is_connected=True).count(),
            'active_volunteers': cls.objects(type='volunteer', is_connected=True).count(),
        }
        
        # Ajoute les stats par région si disponible
        locations = cls.objects(location__exists=True).distinct('location')
        if locations:
            stats['by_location'] = {
                location: cls.objects(location=location).count()
                for location in locations
            }
            
        return stats
