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
from django.conf import settings

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
    
    def __init__(self, host=None, port=None, db=None):
        """
        Initialise la connexion Redis et configure les canaux par défaut.
        
        Args:
            host: Hôte Redis (défaut: settings.REDIS_HOST ou localhost)
            port: Port Redis (défaut: settings.REDIS_PORT ou 6379)
            db: Base de données Redis (défaut: settings.REDIS_DB ou 0)
        """
        # Utiliser les paramètres fournis ou les valeurs par défaut des settings
        self.use_proxy = getattr(settings, 'USE_REDIS_PROXY', False)
        
        if self.use_proxy:
            # Utiliser le proxy Redis
            self.redis_host = host or getattr(settings, 'REDIS_PROXY_HOST', 'localhost')
            self.redis_port = port or getattr(settings, 'REDIS_PROXY_PORT', 6380)
            self.redis_db = db or getattr(settings, 'REDIS_PROXY_DB', 0)
            logger.info(f"MessageBroker utilise le proxy Redis: {self.redis_host}:{self.redis_port}")
        else:
            # Utiliser Redis directement
            self.redis_host = host or getattr(settings, 'REDIS_HOST', 'localhost')
            self.redis_port = port or getattr(settings, 'REDIS_PORT', 6379)
            self.redis_db = db or getattr(settings, 'REDIS_DB', 0)
            logger.info(f"MessageBroker utilise Redis directement: {self.redis_host}:{self.redis_port}")
        
        # Connexion Redis
        self.redis_client = redis.Redis(
            host=self.redis_host, 
            port=self.redis_port, 
            db=self.redis_db,
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
            ("auth/register_response", "Réponses d'inscription"),
            ("auth/login", "Connexion des managers et volunteers"),
            ("auth/login_response", "Réponses d'authentification"),
            
            # Canaux des tâches
            ("tasks/new", "Nouvelles tâches des managers"),
            ("tasks/assign", "Attribution des tâches aux volunteers"),
            ("tasks/status/#", "État des tâches en cours"),
            ("tasks/result/#", "Résultats des tâches terminées"),
            
            # Canaux de coordination
            ("coord/heartbeat/#", "Signaux de vie des participants"),
            ("coord/status", "État global du système"),
            ("coord/emergency", "Messages d'urgence"),
            
            # Canaux des volunteers
            ("volunteer/register", "Inscription des volunteers"),
            ("volunteer/register_response", "Réponses d'inscription des volunteers"),
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
            self.create_channel(channel, f"Canal créé automatiquement: {channel}")
            
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
        """
        try:
            # Créer le canal s'il n'existe pas
            if channel not in self._channels:
                self.create_channel(channel, f"Canal créé automatiquement: {channel}")
                
            # Convertir le message en JSON
            if isinstance(message, str):
                json_message = message
            else:
                json_message = json.dumps(message)
                
            # Publier le message
            self.redis_client.publish(channel, json_message)
            logger.debug(f"Message publié sur {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la publication sur {channel}: {e}")
            return False
            
    def start_listening(self):
        """
        Démarre l'écoute des messages en mode bloquant.
        Utilise les callbacks définis avec subscribe().
        """
        logger.info("Démarrage de l'écoute des messages")
        self.pubsub.run_in_thread(sleep_time=0.01)
        
    def stop_listening(self):
        """Arrête l'écoute des messages."""
        logger.info("Arrêt de l'écoute des messages")
        self.pubsub.close()
