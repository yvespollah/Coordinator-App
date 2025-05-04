"""
CommunicationManager: Le "bureau de poste" de notre système.
Il gère la distribution des messages entre les différents composants.
"""

from typing import Dict, Any, Optional, List, Callable
from .broker import MessageBroker
from .messages import Message, TaskMessage, ResultMessage
from .constants import (
    REGISTRATION_CHANNEL,    # Canal pour les inscriptions
    AUTH_CHANNEL,           # Canal pour l'authentification
    MANAGER_TASKS_CHANNEL,  # Canal des tâches des managers
    MANAGER_STATUS_CHANNEL, # Canal des états pour les managers
    VOLUNTEER_TASKS_CHANNEL,# Canal des tâches pour les volunteers
    VOLUNTEER_STATUS_CHANNEL,# Canal des états des volunteers
    VOLUNTEER_RESULTS_CHANNEL,# Canal des résultats
    MSG_TYPE_REGISTRATION,   # Type: inscription
    MSG_TYPE_AUTH,          # Type: authentification
    MSG_TYPE_TASK,          # Type: tâche
    MSG_TYPE_RESULT,        # Type: résultat
    MSG_TYPE_STATUS,        # Type: état
    MSG_TYPE_HEARTBEAT      # Type: battement de cœur
)

class CommunicationManager:
    """
    Le "bureau de poste" qui gère toute la communication.
    C'est un singleton (une seule instance possible).
    
    Exemple d'utilisation:
        manager = CommunicationManager()
        
        # Pour recevoir des messages
        def mon_handler(message):
            print(f"Nouveau message: {message}")
        manager.register_handler(MANAGER_TASKS_CHANNEL, mon_handler)
        
        # Pour envoyer un message
        message = TaskMessage(task_id="123", command="analyse")
        manager.publish_message(MANAGER_TASKS_CHANNEL, message)
    """
    
    # Variable de classe pour le singleton
    _instance = None
    
    def __new__(cls):
        """
        Assure qu'une seule instance existe.
        C'est important car on ne veut pas plusieurs gestionnaires
        qui se marchent sur les pieds.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialise le manager (une seule fois).
        Crée le broker de messages et prépare les gestionnaires.
        """
        if not self._initialized:
            # Broker = connexion à Redis
            self.broker = MessageBroker()
            # Dictionnaire des gestionnaires par canal
            self._message_handlers: Dict[str, List[Callable]] = {}
            # Prépare les canaux par défaut
            self._initialize_handlers()
            self._initialized = True
    
    def _initialize_handlers(self):
        """
        Prépare les listes de gestionnaires pour chaque canal.
        Chaque canal peut avoir plusieurs gestionnaires.
        """
        self._message_handlers = {
            REGISTRATION_CHANNEL: [],      # Pour les inscriptions
            AUTH_CHANNEL: [],             # Pour l'authentification
            MANAGER_TASKS_CHANNEL: [],    # Pour les tâches des managers
            MANAGER_STATUS_CHANNEL: [],   # Pour les états aux managers
            VOLUNTEER_TASKS_CHANNEL: [],  # Pour les tâches aux volunteers
            VOLUNTEER_STATUS_CHANNEL: [], # Pour les états des volunteers
            VOLUNTEER_RESULTS_CHANNEL: [] # Pour les résultats
        }
    
    def start(self):
        """
        Démarre l'écoute des messages.
        À appeler quand on veut commencer à recevoir des messages.
        """
        self.broker.start_listening()
    
    def stop(self):
        """
        Arrête l'écoute des messages.
        À appeler quand on veut arrêter de recevoir des messages.
        """
        self.broker.stop_listening()
    
    def register_handler(self, channel: str, handler: Callable):
        """
        Enregistre une fonction qui sera appelée quand un message arrive.
        
        Args:
            channel: Le canal à écouter (ex: MANAGER_TASKS_CHANNEL)
            handler: La fonction à appeler (ex: def mon_handler(message))
        
        Exemple:
            def traiter_tache(message):
                print(f"Nouvelle tâche: {message}")
            
            manager.register_handler(MANAGER_TASKS_CHANNEL, traiter_tache)
        """
        # Crée la liste si le canal n'existe pas
        if channel not in self._message_handlers:
            self._message_handlers[channel] = []
        
        # Ajoute le handler à la liste
        self._message_handlers[channel].append(handler)
        
        # Fonction qui sera appelée par Redis
        def message_callback(channel: str, data: Dict[str, Any]):
            # Récupère tous les handlers pour ce canal
            handlers = self._message_handlers.get(channel, [])
            # Appelle chaque handler avec le message
            for handler in handlers:
                handler(data)
        
        # S'abonne au canal dans Redis
        self.broker.subscribe(channel, message_callback)
    
    def unregister_handler(self, channel: str, handler: Callable) -> bool:
        """
        Retire un handler d'un canal.
        
        Args:
            channel: Le canal (ex: MANAGER_TASKS_CHANNEL)
            handler: La fonction à retirer
            
        Returns:
            bool: True si retiré, False si pas trouvé
        """
        if channel not in self._message_handlers:
            return False
        
        try:
            self._message_handlers[channel].remove(handler)
            return True
        except ValueError:
            return False
    
    def publish_message(self, channel: str, message: Message) -> bool:
        """
        Envoie un message sur un canal.
        
        Args:
            channel: Le canal où envoyer (ex: MANAGER_TASKS_CHANNEL)
            message: Le message à envoyer (doit hériter de Message)
            
        Returns:
            bool: True si envoyé, False si erreur
            
        Exemple:
            task = TaskMessage(task_id="123", command="analyse")
            manager.publish_message(MANAGER_TASKS_CHANNEL, task)
        """
        return self.broker.publish(channel, message.to_dict())
    
    def create_channel(self, name: str, description: str) -> bool:
        """
        Crée un nouveau canal de communication.
        
        Args:
            name: Nom du canal
            description: Description du canal
            
        Returns:
            bool: True si créé, False si erreur
        """
        return self.broker.create_channel(name, description)
    
    def delete_channel(self, name: str) -> bool:
        """
        Supprime un canal existant.
        
        Args:
            name: Nom du canal à supprimer
            
        Returns:
            bool: True si supprimé, False si erreur
        """
        return self.broker.delete_channel(name)
    
    def get_channel_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtient les informations sur un canal.
        
        Args:
            name: Nom du canal
            
        Returns:
            Dict avec les infos ou None si pas trouvé
        """
        channel = self.broker.get_channel(name)
        if channel:
            return {
                "name": channel.name,
                "description": channel.description,
                "created_at": channel.created_at,
                "active": channel.active
            }
        return None
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """
        Liste tous les canaux disponibles.
        
        Returns:
            Liste des canaux avec leurs infos
        """
        channels = self.broker.list_channels()
        return [
            {
                "name": channel.name,
                "description": channel.description,
                "created_at": channel.created_at,
                "active": channel.active
            }
            for channel in channels
        ]
