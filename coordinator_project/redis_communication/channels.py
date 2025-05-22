"""
Définition et gestion des canaux de communication.
"""

from enum import Enum
from typing import Dict, List, Set
from .client import RedisClient

class ChannelCategory(Enum):
    """Catégories de canaux dans le système."""
    AUTH = "auth"
    TASK = "task"
    COORDINATION = "coord"
    VOLUNTEER = "volunteer"
    MANAGER = "manager"
    SYSTEM = "system"

class ChannelRegistry:
    """
    Registre des canaux disponibles dans le système.
    """
    
    # Canaux par défaut du système
    DEFAULT_CHANNELS = {
        # Canaux d'authentification
        "auth/register": "Inscription des managers et volunteers",
        "auth/register_response": "Réponses d'inscription",
        "auth/login": "Connexion des managers et volunteers",
        "auth/login_response": "Réponses d'authentification",
        "auth/volunteer_register": "Inscription des volunteers",
        "auth/volunteer_login": "Connexion des volunteers",
        
        # Canaux des tâches
        "task/new": "Nouvelles tâches des managers",
        "task/assign": "Attribution des tâches aux volunteers",
        "task/status": "État des tâches en cours",
        "task/result": "Résultats des tâches terminées",
        
        
        # Canaux des volunteers
        "volunteer/register": "Inscription des volunteers",
        "volunteer/register_response": "Réponses d'inscription des volunteers",
        "volunteer/available": "Liste des volunteers disponibles",
        "volunteer/resources": "Ressources des volunteers",
        
        # Canaux des managers
        "manager/status": "État des managers",
        "manager/requests": "Requêtes spéciales des managers",
        
        # Canaux des workflows
        "workflow/submit": "Soumission des workflows",
        "workflow/submit_response": "Réponses aux soumissions de workflows",
        "workflow/status": "État des workflows",
        "workflow/result": "Résultats des workflows",
        "workflow/cancel": "Annulation des workflows"
    }
    
    def __init__(self):
        """Initialise le registre des canaux."""
        self.channels: Dict[str, str] = {}
        self.subscribers: Dict[str, Set[str]] = {}
        
        # Ajouter les canaux par défaut
        for channel, description in self.DEFAULT_CHANNELS.items():
            self.add_channel(channel, description)
    
    def add_channel(self, name: str, description: str) -> bool:
        """
        Ajoute un canal au registre.
        
        Args:
            name: Nom du canal
            description: Description du canal
            
        Returns:
            bool: True si ajouté, False si existe déjà
        """
        if name in self.channels:
            return False
        
        self.channels[name] = description
        self.subscribers[name] = set()
        return True
    
    def remove_channel(self, name: str) -> bool:
        """
        Supprime un canal du registre.
        
        Args:
            name: Nom du canal
            
        Returns:
            bool: True si supprimé, False si n'existe pas
        """
        if name not in self.channels:
            return False
        
        del self.channels[name]
        del self.subscribers[name]
        return True
    
    def get_channels(self, category: ChannelCategory = None) -> List[str]:
        """
        Récupère la liste des canaux, éventuellement filtrée par catégorie.
        
        Args:
            category: Catégorie de canaux (optionnel)
            
        Returns:
            List[str]: Liste des noms de canaux
        """
        if category is None:
            return list(self.channels.keys())
        
        prefix = f"{category.value}/"
        return [channel for channel in self.channels if channel.startswith(prefix)]
    
    def get_description(self, channel: str) -> str:
        """
        Récupère la description d'un canal.
        
        Args:
            channel: Nom du canal
            
        Returns:
            str: Description du canal ou chaîne vide si non trouvé
        """
        return self.channels.get(channel, "")
    
    def add_subscriber(self, channel: str, client_id: str) -> bool:
        """
        Ajoute un abonné à un canal.
        
        Args:
            channel: Nom du canal
            client_id: ID du client
            
        Returns:
            bool: True si ajouté, False si le canal n'existe pas
        """
        if channel not in self.subscribers:
            return False
        
        self.subscribers[channel].add(client_id)
        return True
    
    def remove_subscriber(self, channel: str, client_id: str) -> bool:
        """
        Supprime un abonné d'un canal.
        
        Args:
            channel: Nom du canal
            client_id: ID du client
            
        Returns:
            bool: True si supprimé, False si le canal ou l'abonné n'existe pas
        """
        if channel not in self.subscribers:
            return False
        
        if client_id in self.subscribers[channel]:
            self.subscribers[channel].remove(client_id)
            return True
        
        return False
    
    def get_subscribers(self, channel: str) -> Set[str]:
        """
        Récupère la liste des abonnés d'un canal.
        
        Args:
            channel: Nom du canal
            
        Returns:
            Set[str]: Ensemble des IDs des abonnés
        """
        return self.subscribers.get(channel, set())


# Instance globale du registre de canaux
registry = ChannelRegistry()


def register_handlers(client: RedisClient):
    """
    Enregistre les gestionnaires d'événements pour les canaux par défaut.
    
    Args:
        client: Instance du client Redis
    """
    # Importer ici pour éviter les imports circulaires
    from .handlers import (
        manager_registration_handler,
        manager_login_handler,
        volunteer_registration_handler,
        volunteer_login_handler
    )
    
    # Importer les gestionnaires de workflow
    from .workflow_handlers import workflow_submission_handler
    
    # Définir les gestionnaires pour chaque canal
    handlers = {
        # Canaux d'authentification
        "auth/register": manager_registration_handler,
        "auth/login": manager_login_handler,
        "auth/volunteer_register": volunteer_registration_handler,
        "auth/volunteer_login": volunteer_login_handler,
        
        # Canaux de workflow
        "workflow/submit": workflow_submission_handler,
        
        # Canaux système
        "system/error": lambda channel, message: \
            print(f"Erreur système reçue: {message.data}"),
        
        # Canaux de coordination
        "coord/heartbeat": lambda channel, message: \
            print(f"Heartbeat reçu de {message.sender['type']}:{message.sender['id']}"),
        "coord/emergency": lambda channel, message: \
            print(f"URGENCE: {message.data} reçu de {message.sender['type']}:{message.sender['id']}")
    }
    
    # S'abonner à tous les canaux
    for channel, handler in handlers.items():
        client.subscribe(channel, handler)
    
    return True
