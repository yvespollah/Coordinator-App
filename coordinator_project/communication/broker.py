"""
Broker de messages utilisant Redis pour la communication pub/sub.
Gère les canaux de communication entre les managers et les volunteers.
"""

from typing import List, Optional, Callable, Any
import redis
import json
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Channel:
    """
    Représente un canal de communication.
    
    Attributes:
        name: Nom du canal (ex: 'tasks/submission')
        description: Description du canal
        created_at: Date de création
        active: Si le canal est actif
        subscribers: Nombre d'abonnés actifs
    """
    name: str
    description: str
    created_at: datetime
    active: bool = True
    subscribers: int = 0

class MessageBroker:
    """
    Broker central pour la communication pub/sub via Redis.
    Gère les canaux de communication et le routage des messages.
    """
    
    def __init__(self, host='localhost', port=6379, db=0):
        """
        Initialise la connexion Redis et configure les canaux par défaut.
        
        Args:
            host: Hôte Redis (défaut: localhost)
            port: Port Redis (défaut: 6379)
            db: Base de données Redis (défaut: 0)
        """
        # Connexion Redis
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db,
            decode_responses=True  # Décode automatiquement les réponses en UTF-8
        )
        self.pubsub = self.redis_client.pubsub()
        
        # Stockage des canaux
        self._channels: dict[str, Channel] = {}
        
        # Initialise les canaux par défaut
        self._initialize_default_channels()
        
        logger.info("MessageBroker initialisé avec succès")

    def _initialize_default_channels(self):
        """Configure les canaux par défaut du système."""
        default_channels = [
            # Canaux d'authentification
            ("auth/register", "Inscription des managers et volunteers"),
            ("auth/response", "Réponses d'authentification"),
            
            # Canaux des tâches
            ("tasks/new", "Nouvelles tâches des managers"),
            ("tasks/assign", "Attribution des tâches aux volunteers"),
            ("tasks/status/#", "État des tâches en cours"),
            ("tasks/result/#", "Résultats des tâches terminées"),
            
            # Canaux de coordination
            ("coord/heartbeat/#", "Signaux de vie des participants"),
            ("coord/status", "État global du système"),
            
            # Canaux des volunteers
            ("volunteer/available", "Liste des volunteers disponibles"),
            ("volunteer/resources", "Ressources des volunteers"),
            
            # Canaux des managers
            ("manager/status", "État des managers"),
            ("manager/requests", "Requêtes spéciales des managers")
        ]
        
        for channel_name, description in default_channels:
            self.create_channel(channel_name, description)
            
        logger.info(f"Canaux par défaut initialisés: {len(default_channels)} canaux")

    def create_channel(self, channel_name: str, description: str) -> bool:
        """
        Crée un nouveau canal de communication.
        
        Args:
            channel_name: Nom du canal (ex: 'tasks/new')
            description: Description du canal
            
        Returns:
            bool: True si créé, False si existe déjà
        """
        if channel_name in self._channels:
            logger.warning(f"Canal {channel_name} existe déjà")
            return False
            
        channel = Channel(
            name=channel_name,
            description=description,
            created_at=datetime.utcnow()
        )
        self._channels[channel_name] = channel
        
        logger.info(f"Canal créé: {channel_name}")
        return True

    def delete_channel(self, channel_name: str) -> bool:
        """
        Supprime un canal existant.
        
        Args:
            channel_name: Nom du canal à supprimer
            
        Returns:
            bool: True si supprimé, False si n'existe pas
        """
        if channel_name not in self._channels:
            logger.warning(f"Canal {channel_name} n'existe pas")
            return False
            
        # Désabonne tout le monde
        pattern = f"{channel_name}*"
        self.pubsub.punsubscribe(pattern)
        
        del self._channels[channel_name]
        logger.info(f"Canal supprimé: {channel_name}")
        return True

    def list_channels(self) -> List[Channel]:
        """Liste tous les canaux disponibles."""
        return list(self._channels.values())

    def get_channel(self, channel_name: str) -> Optional[Channel]:
        """
        Obtient les informations d'un canal.
        
        Args:
            channel_name: Nom du canal
            
        Returns:
            Channel ou None si pas trouvé
        """
        return self._channels.get(channel_name)

    def subscribe(self, channel: str, callback: Callable[[str, Any], None]):
        """
        S'abonne à un canal avec une fonction de callback.
        
        Args:
            channel: Nom du canal
            callback: Fonction appelée quand un message arrive
            
        Example:
            def on_task(channel, data):
                print(f"Nouvelle tâche: {data}")
            
            broker.subscribe('tasks/new', on_task)
        """
        if channel not in self._channels:
            raise ValueError(f"Canal {channel} n'existe pas")
            
        def message_handler(message):
            try:
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    callback(channel, data)
                    
            except Exception as e:
                logger.error(f"Erreur dans message_handler: {e}")
                
        self.pubsub.subscribe(**{channel: message_handler})
        self._channels[channel].subscribers += 1
        
        logger.info(f"Abonné au canal: {channel}")
        
    def publish(self, channel: str, message: Any) -> bool:
        """
        Publie un message sur un canal.
        
        Args:
            channel: Nom du canal
            message: Message à publier (sera converti en JSON)
            
        Returns:
            bool: True si publié, False si erreur
            
        Example:
            broker.publish('tasks/new', {
                'task_id': '123',
                'type': 'analyse',
                'data': {'file': 'data.csv'}
            })
        """
        if channel not in self._channels:
            logger.error(f"Canal {channel} n'existe pas")
            return False
            
        try:
            message_data = json.dumps(message)
            self.redis_client.publish(channel, message_data)
            logger.debug(f"Message publié sur {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la publication: {e}")
            return False

    def start_listening(self):
        """Démarre l'écoute des messages dans un thread séparé."""
        try:
            self.pubsub.run_in_thread(sleep_time=0.001)
            logger.info("Écoute des messages démarrée")
        except Exception as e:
            logger.error(f"Erreur au démarrage de l'écoute: {e}")

    def stop_listening(self):
        """Arrête l'écoute des messages."""
        try:
            self.pubsub.close()
            logger.info("Écoute des messages arrêtée")
        except Exception as e:
            logger.error(f"Erreur à l'arrêt de l'écoute: {e}")

    def get_channel_stats(self, channel_name: str) -> dict:
        """
        Obtient des statistiques sur un canal.
        
        Args:
            channel_name: Nom du canal
            
        Returns:
            dict: Statistiques du canal
        """
        channel = self._channels.get(channel_name)
        if not channel:
            return {}
            
        return {
            'name': channel.name,
            'description': channel.description,
            'created_at': channel.created_at.isoformat(),
            'active': channel.active,
            'subscribers': channel.subscribers,
            'messages_today': self.redis_client.get(f"stats:{channel_name}:today") or 0
        }
