"""
Client Redis universel pour la communication entre les composants du système.
"""

import json
import logging
import threading
import time
import uuid
import sys
from typing import Dict, Callable, Any, List, Optional
import redis
from django.conf import settings

from .message import Message, MessageType
from .exceptions import ChannelError, ConnectionError

# Configuration du logging pour afficher les messages dans la console
logger = logging.getLogger(__name__)

# Ajouter un gestionnaire de console si aucun n'existe déjà
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)  # Définir le niveau de log à INFO

class RedisClient:
    """
    Client Redis universel pour la communication entre les composants du système.
    Implémente le pattern Singleton pour garantir une instance unique.
    """
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, config=None):
        """
        Récupère l'instance unique du client Redis ou en crée une nouvelle.
        
        Args:
            config: Configuration optionnelle pour surcharger les paramètres par défaut
            
        Returns:
            RedisClient: L'instance unique du client
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config)
            return cls._instance
    
    def __init__(self, config=None):
        """
        Initialise le client Redis avec la configuration fournie ou les paramètres par défaut.
        
        Args:
            config: Configuration optionnelle (host, port, db, etc.)
        """
        if RedisClient._instance is not None:
            raise RuntimeError("Utilisez RedisClient.get_instance() pour obtenir l'instance")
        
        self.config = config or {}
        self.client_type = self.config.get('client_type', 'coordinator')
        self.client_id = self.config.get('client_id', str(uuid.uuid4()))
        
        # Paramètres de connexion
        self.host = self.config.get('host', getattr(settings, 'REDIS_PROXY_HOST', 'localhost'))
        self.port = self.config.get('port', getattr(settings, 'REDIS_PROXY_PORT', 6380))
        self.db = self.config.get('db', getattr(settings, 'REDIS_DB', 0))
        
        # Client Redis
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=True
        )
        
        # PubSub pour les abonnements
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        
        # Gestionnaires d'événements par canal
        self.handlers: Dict[str, List[Callable]] = {}
        
        # Thread d'écoute
        self.listen_thread = None
        self.running = False
        
        # Statistiques
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'last_activity': time.time(),
            'start_time': time.time()
        }
        
        logger.info(f"Client Redis initialisé: {self.client_type}:{self.client_id} @ {self.host}:{self.port}")
    
    def start(self):
        """
        Démarre le thread d'écoute des messages et s'abonne à tous les canaux enregistrés.
        """
        if self.running:
            logger.warning("Le client est déjà en cours d'exécution")
            return True
        
        # Tenter de se connecter à Redis
        try:
            # Vérifier la connexion Redis
            self.redis.ping()
            logger.info("Connexion au serveur Redis établie")
            
            # Initialiser le pubsub
            self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
            
            # S'abonner à tous les canaux enregistrés en une seule commande
            channels = list(self.handlers.keys())
            if channels:
                self.pubsub.subscribe(*channels)
                logger.info(f"Abonné à {len(channels)} canaux: {', '.join(channels)}")
            
            # Démarrer le thread d'écoute
            self.running = True
            self.listen_thread = threading.Thread(
                target=self._listen_loop,
                name=f"RedisListener-{self.client_id[:8]}"
            )
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            logger.info(f"Client Redis démarré: {self.client_type}:{self.client_id}")
            return True
            
        except redis.ConnectionError as e:
            logger.error(f"Erreur de connexion Redis: {e}")
            logger.error(f"Assurez-vous que le proxy Redis est démarré sur {self.host}:{self.port}")
            return False
        except Exception as e:
            logger.error(f"Impossible de démarrer le client Redis: {e}")
            return False
    
    def stop(self):
        """
        Arrête le thread d'écoute et ferme les connexions.
        """
        if not self.running:
            return
        
        self.running = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)
        
        # Désabonnement de tous les canaux
        self.pubsub.unsubscribe()
        self.pubsub.close()
        
        logger.info(f"Client Redis arrêté: {self.client_type}:{self.client_id}")
    
    def subscribe(self, channel: str, handler: Callable[[str, Any], None]):
        """
        S'abonne à un canal et associe un gestionnaire d'événements.
        
        Args:
            channel: Nom du canal
            handler: Fonction de rappel qui sera appelée avec (channel, message)
        """
        # Ajouter le gestionnaire
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)
        
        # S'abonner au canal Redis seulement si le client est démarré
        if self.running and self.pubsub:
            try:
                # Vérifier si nous sommes déjà abonné à ce canal
                current_channels = [c.decode('utf-8') if isinstance(c, bytes) else c 
                                  for c in self.pubsub.channels.keys()]
                
                if channel not in current_channels:
                    self.pubsub.subscribe(channel)
                    logger.info(f"Abonné au canal: {channel}")
                else:
                    logger.debug(f"Déjà abonné au canal: {channel}")
            except Exception as e:
                logger.warning(f"Impossible de s'abonner au canal {channel}: {e}")
        else:
            logger.debug(f"Canal {channel} ajouté à la liste d'abonnements en attente")
            
        return True
    
    def unsubscribe(self, channel: str, handler: Optional[Callable] = None):
        """
        Se désabonne d'un canal et supprime le(s) gestionnaire(s) associé(s).
        
        Args:
            channel: Nom du canal
            handler: Gestionnaire spécifique à supprimer (si None, tous les gestionnaires sont supprimés)
        """
        if channel in self.handlers:
            if handler is None:
                # Supprimer tous les gestionnaires
                self.handlers[channel] = []
            else:
                # Supprimer un gestionnaire spécifique
                self.handlers[channel] = [h for h in self.handlers[channel] if h != handler]
            
            # Si plus aucun gestionnaire, se désabonner du canal
            if not self.handlers[channel]:
                self.pubsub.unsubscribe(channel)
                del self.handlers[channel]
                
        logger.info(f"Désabonné du canal: {channel}")
        return True
    
    def publish(self, channel: str, message_data: Any, request_id: str = None, token: str = None, message_type: str = None, real_sender_id: str = None):
        """
        Publie un message sur un canal et enregistre le message dans la base de données.
        
        Args:
            channel: Nom du canal
            message_data: Données du message
            request_id: ID de requête optionnel (généré automatiquement si non fourni)
            token: Token JWT pour l'authentification (optionnel)
            message_type: Type de message (request ou response)
            real_sender_id: ID réel de l'expéditeur (manager_id, volunteer_id, etc.)
            
        Returns:
            str: ID de la requête
        """
        # Déterminer le type de message en fonction du canal si non spécifié
        if message_type is None:
            if '_response' in channel:
                message_type = "response"
            else:
                message_type = "request"
                
        logger.info(f"Publication d'un message de type '{message_type}' sur le canal {channel}")
        
        # Utiliser l'ID réel de l'expéditeur s'il est fourni
        sender_id = real_sender_id or self.client_id
        
        # Créer un message standardisé
        message = Message(
            request_id=request_id or str(uuid.uuid4()),
            sender={
                'type': self.client_type,
                'id': sender_id
            },
            message_type=message_type,
            data=message_data,
            token=token
        )

        # Ajouter le token JWT si fourni
        if token:
            message.token = token
            logger.info(f"Token JWT ajouté au message pour le canal {channel}")
        
        # Publier le message
        try:
            # Sérialiser le message
            json_message = message.to_json()
            
            # Publier sur Redis
            self.redis.publish(channel, json_message)
            self.stats['messages_sent'] += 1
            self.stats['last_activity'] = time.time()
            
            # Enregistrer le message dans la base de données
            try:
                # Import ici pour éviter les importations circulaires
                from message_logging.services import log_message
                
                # Déterminer le destinataire en fonction du canal
                receiver_type = None
                receiver_id = None
                
                if channel.startswith('manager/'):
                    receiver_type = 'manager'
                elif channel.startswith('volunteer/'):
                    receiver_type = 'volunteer'
                elif channel.startswith('coordinator/'):
                    receiver_type = 'coordinator'
                
                # Enregistrer le message
                log_message(
                    sender_type=self.client_type,
                    sender_id=sender_id,
                    channel=channel,
                    request_id=message.request_id,
                    message_type=message_type,
                    content=message_data,
                    receiver_type=receiver_type,
                    receiver_id=receiver_id
                )
            except Exception as log_error:
                logger.error(f"Erreur lors de l'enregistrement du message: {log_error}")
            
            logger.debug(f"Message publié sur {channel}: {message.request_id}")
            return message.request_id
        except Exception as e:
            logger.error(f"Erreur lors de la publication sur {channel}: {e}")
            raise ChannelError(f"Erreur de publication: {e}")
    
    def _listen_loop(self):
        """
        Boucle d'écoute des messages dans un thread séparé.
        """
        connection_error_count = 0
        max_connection_errors = 3  # Nombre maximal d'erreurs avant de logguer
        
        while self.running:
            try:
                # Récupérer les messages avec un timeout court
                message = self.pubsub.get_message(timeout=0.1)
                
                # Réinitialiser le compteur d'erreurs si nous recevons un message
                if message:
                    connection_error_count = 0
                
                if message and message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    try:
                        # Logs pour déboguer le problème de parsing
                        # logger.info(f"Message brut reçu sur {channel}: {data}")
                        
                        # Décoder le message
                        msg_obj = Message.from_json(data)
                        
                        # Vérifier si les données sont correctement extraites
                        # logger.info(f"Message désérialisé: {msg_obj.to_dict()}")
                        
                        # Mettre à jour les statistiques
                        self.stats['messages_received'] += 1
                        self.stats['last_activity'] = time.time()
                        
                        # Appeler les gestionnaires pour ce canal
                        if channel in self.handlers:
                            for handler in self.handlers[channel]:
                                try:
                                    handler(channel, msg_obj)
                                except Exception as e:
                                    import traceback
                                    logger.error(f"Erreur dans le gestionnaire pour {channel}: {e}")
                                    logger.error(traceback.format_exc())
                    except json.JSONDecodeError:
                        logger.error(f"Message non JSON sur {channel}: {data}")
                    except Exception as e:
                        import traceback
                        logger.error(f"Erreur lors du traitement du message: {e}")
                        logger.error(traceback.format_exc())
                
                # Petite pause pour éviter de surcharger le CPU
                time.sleep(0.01)
                
            except redis.ConnectionError as e:
                connection_error_count += 1
                
                # Ne logguer l'erreur que si elle persiste
                if connection_error_count >= max_connection_errors:
                    logger.error(f"Erreur de connexion Redis persistante: {e}")
                    connection_error_count = 0  # Réinitialiser pour éviter de spammer les logs
                
                # Attendre avant de réessayer
                time.sleep(2.0)
                
                # Tenter de se reconnecter seulement si nous avons perdu la connexion
                if not self.is_connected():
                    try:
                        # Réinitialiser la connexion Redis
                        self.redis = redis.Redis(
                            host=self.host,
                            port=self.port,
                            db=self.db,
                            decode_responses=True,
                            socket_timeout=5.0,
                            socket_connect_timeout=5.0
                        )
                        
                        # Vérifier la connexion
                        if self.is_connected():
                            # Réinitialiser le pubsub
                            self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
                            
                            # Se réabonner à tous les canaux en une seule commande
                            channels = list(self.handlers.keys())
                            if channels:
                                self.pubsub.subscribe(*channels)
                                logger.info(f"Reconnecté et réabonné à {len(channels)} canaux")
                    except Exception as reconnect_error:
                        if connection_error_count >= max_connection_errors:
                            logger.error(f"Échec de la reconnexion: {reconnect_error}")
                
            except redis.RedisError as e:
                logger.error(f"Erreur Redis: {e}")
                time.sleep(1.0)  # Attendre avant de réessayer
            except Exception as e:
                logger.error(f"Erreur inattendue dans la boucle d'écoute: {e}")
                time.sleep(1.0)
    
    def is_connected(self):
        """
        Vérifie si le client est connecté au serveur Redis.
        
        Returns:
            bool: True si connecté, False sinon
        """
        try:
            # Tenter une opération simple pour vérifier la connexion
            self.redis.ping()
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            return False
        except Exception as e:
            logger.debug(f"Erreur lors de la vérification de la connexion: {e}")
            return False
    
    def get_stats(self):
        """
        Récupère les statistiques du client.
        
        Returns:
            dict: Statistiques d'utilisation
        """
        return {
            **self.stats,
            'subscribed_channels': list(self.handlers.keys()),
            'uptime': time.time() - self.stats.get('start_time', time.time()),
            'connected': self.is_connected()
        }
