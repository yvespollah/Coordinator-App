"""
Fonctions client pour l'authentification des managers et des volontaires.
"""

import logging
import uuid
import time
import json
import os
from typing import Dict, Any, Optional, Callable, Tuple
from .client import RedisClient
from .message import Message

logger = logging.getLogger(__name__)

# Répertoire pour stocker les réponses
RESPONSES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'auth_responses')
os.makedirs(RESPONSES_DIR, exist_ok=True)

def save_response(request_id: str, response: Dict[str, Any]):
    """
    Enregistre une réponse dans un fichier.
    
    Args:
        request_id: ID de la requête
        response: Données de la réponse
    """
    filename = os.path.join(RESPONSES_DIR, f"{request_id}.json")
    with open(filename, 'w') as f:
        json.dump({
            'response': response,
            'timestamp': time.time()
        }, f)
    
    logger.debug(f"Réponse {request_id} enregistrée dans {filename}")

def get_response(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère une réponse.
    
    Args:
        request_id: ID de la requête
        
    Returns:
        Dict ou None: Données de la réponse si trouvée, None sinon
    """
    filename = os.path.join(RESPONSES_DIR, f"{request_id}.json")
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la réponse {request_id}: {e}")
        return None

def delete_response(request_id: str) -> bool:
    """
    Supprime une réponse.
    
    Args:
        request_id: ID de la requête
        
    Returns:
        bool: True si supprimée, False sinon
    """
    filename = os.path.join(RESPONSES_DIR, f"{request_id}.json")
    if not os.path.exists(filename):
        return False
    
    try:
        os.remove(filename)
        logger.debug(f"Réponse {request_id} supprimée")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la réponse {request_id}: {e}")
        return False

# Fonctions pour les managers

def register_manager(username: str, email: str, password: str, 
                     callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                     timeout: int = 60) -> Tuple[bool, Dict[str, Any]]:
    """
    Enregistre un nouveau manager.
    
    Args:
        username: Nom d'utilisateur
        email: Adresse email
        password: Mot de passe
        callback: Fonction de rappel appelée avec la réponse (optionnel)
        timeout: Délai d'attente en secondes (défaut: 30)
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (Succès, Données de réponse)
    """
    client = RedisClient.get_instance()
    
    # Créer un ID de requête unique
    request_id = str(uuid.uuid4())
    
    # Préparer les données de la requête
    request_data = {
        'username': username,
        'email': email,
        'password': password
    }
    
    # Fonction de rappel pour traiter la réponse
    def handle_response(channel: str, message: Message):
        if message.request_id == request_id:
            # Enregistrer la réponse
            save_response(request_id, message.data)
            
            # Appeler le callback si fourni
            if callback:
                callback(message.data)
            
            # Se désabonner du canal
            client.unsubscribe('auth/register_response', handle_response)
    
    # S'abonner au canal de réponse
    client.subscribe('auth/register_response', handle_response)
    
    # Publier la requête
    client.publish('auth/register', request_data, request_id=request_id)
    
    logger.info(f"Demande d'enregistrement envoyée pour {username} (request_id: {request_id})")
    
    # Attendre la réponse
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = get_response(request_id)
        if response:
            # Supprimer la réponse du fichier
            delete_response(request_id)
            
            # Vérifier le statut
            status = response.get('response', {}).get('status')
            if status == 'success':
                return True, response.get('response', {})
            else:
                return False, response.get('response', {})
        
        # Attendre un peu avant de vérifier à nouveau
        time.sleep(0.1)
    
    # Timeout
    logger.error(f"Timeout lors de l'enregistrement de {username}")
    return False, {'status': 'error', 'message': 'Timeout'}

def login_manager(username: str, password: str, 
                  callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                  timeout: int = 30) -> Tuple[bool, Dict[str, Any]]:
    """
    Authentifie un manager.
    
    Args:
        username: Nom d'utilisateur
        password: Mot de passe
        callback: Fonction de rappel appelée avec la réponse (optionnel)
        timeout: Délai d'attente en secondes (défaut: 30)
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (Succès, Données de réponse)
    """
    client = RedisClient.get_instance()
    
    # Créer un ID de requête unique
    request_id = str(uuid.uuid4())
    
    # Préparer les données de la requête
    request_data = {
        'username': username,
        'password': password
    }
    
    # Fonction de rappel pour traiter la réponse
    def handle_response(channel: str, message: Message):
        if message.request_id == request_id:
            # Enregistrer la réponse
            save_response(request_id, message.data)
            
            # Appeler le callback si fourni
            if callback:
                callback(message.data)
            
            # Se désabonner du canal
            client.unsubscribe('auth/login_response', handle_response)
    
    # S'abonner au canal de réponse
    client.subscribe('auth/login_response', handle_response)
    
    # Publier la requête
    client.publish('auth/login', request_data, request_id=request_id)
    
    logger.info(f"Demande d'authentification envoyée pour {username} (request_id: {request_id})")
    
    # Attendre la réponse
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = get_response(request_id)
        if response:
            # Supprimer la réponse du fichier
            delete_response(request_id)
            
            # Vérifier le statut
            status = response.get('response', {}).get('status')
            if status == 'success':
                return True, response.get('response', {})
            else:
                return False, response.get('response', {})
        
        # Attendre un peu avant de vérifier à nouveau
        time.sleep(0.1)
    
    # Timeout
    logger.error(f"Timeout lors de l'authentification de {username}")
    return False, {'status': 'error', 'message': 'Timeout'}

# Fonctions pour les volontaires

def register_volunteer(name: str, node_id: str, system_info: Dict[str, Any],
                       callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                       timeout: int = 30) -> Tuple[bool, Dict[str, Any]]:
    """
    Enregistre un nouveau volontaire.
    
    Args:
        name: Nom du nœud
        node_id: ID du nœud
        system_info: Informations système (cpu_model, cpu_cores, etc.)
        callback: Fonction de rappel appelée avec la réponse (optionnel)
        timeout: Délai d'attente en secondes (défaut: 30)
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (Succès, Données de réponse)
    """
    client = RedisClient.get_instance()
    
    # Créer un ID de requête unique
    request_id = str(uuid.uuid4())
    
    # Préparer les données de la requête
    request_data = {
        'name': name,
        'node_id': node_id,
        **system_info
    }
    
    # Vérifier que les informations système requises sont présentes
    required_fields = ['cpu_model', 'cpu_cores', 'total_ram', 'available_storage', 
                       'operating_system', 'ip_address', 'communication_port']
    for field in required_fields:
        if field not in request_data:
            logger.error(f"Champ requis manquant: {field}")
            return False, {'status': 'error', 'message': f"Champ requis manquant: {field}"}
    
    # Fonction de rappel pour traiter la réponse
    def handle_response(channel: str, message: Message):
        if message.request_id == request_id:
            # Enregistrer la réponse
            save_response(request_id, message.data)
            
            # Appeler le callback si fourni
            if callback:
                callback(message.data)
            
            # Se désabonner du canal
            client.unsubscribe('auth/volunteer_register_response', handle_response)
    
    # S'abonner au canal de réponse
    client.subscribe('auth/volunteer_register_response', handle_response)
    
    # Publier la requête
    client.publish('auth/volunteer_register', request_data, request_id=request_id)
    
    logger.info(f"Demande d'enregistrement envoyée pour le volontaire {name} (request_id: {request_id})")
    
    # Attendre la réponse
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = get_response(request_id)
        if response:
            # Supprimer la réponse du fichier
            delete_response(request_id)
            
            # Vérifier le statut
            status = response.get('response', {}).get('status')
            if status == 'success':
                return True, response.get('response', {})
            else:
                return False, response.get('response', {})
        
        # Attendre un peu avant de vérifier à nouveau
        time.sleep(0.1)
    
    # Timeout
    logger.error(f"Timeout lors de l'enregistrement du volontaire {name}")
    return False, {'status': 'error', 'message': 'Timeout'}

def login_volunteer(username: str, password: str,
                    callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                    timeout: int = 30) -> Tuple[bool, Dict[str, Any]]:
    """
    Authentifie un volontaire.
    
    Args:
        username: Nom d'utilisateur
        password: Mot de passe
        callback: Fonction de rappel appelée avec la réponse (optionnel)
        timeout: Délai d'attente en secondes (défaut: 30)
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (Succès, Données de réponse)
    """
    client = RedisClient.get_instance()
    
    # Créer un ID de requête unique
    request_id = str(uuid.uuid4())
    
    # Préparer les données de la requête
    request_data = {
        'username': username,
        'password': password
    }
    
    # Fonction de rappel pour traiter la réponse
    def handle_response(channel: str, message: Message):
        if message.request_id == request_id:
            # Enregistrer la réponse
            save_response(request_id, message.data)
            
            # Appeler le callback si fourni
            if callback:
                callback(message.data)
            
            # Se désabonner du canal
            client.unsubscribe('auth/volunteer_login_response', handle_response)
    
    # S'abonner au canal de réponse
    client.subscribe('auth/volunteer_login_response', handle_response)
    
    # Publier la requête
    client.publish('auth/volunteer_login', request_data, request_id=request_id)
    
    logger.info(f"Demande d'authentification envoyée pour le volontaire {username} (request_id: {request_id})")
    
    # Attendre la réponse
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = get_response(request_id)
        if response:
            # Supprimer la réponse du fichier
            delete_response(request_id)
            
            # Vérifier le statut
            status = response.get('response', {}).get('status')
            if status == 'success':
                return True, response.get('response', {})
            else:
                return False, response.get('response', {})
        
        # Attendre un peu avant de vérifier à nouveau
        time.sleep(0.1)
    
    # Timeout
    logger.error(f"Timeout lors de l'authentification du volontaire {username}")
    return False, {'status': 'error', 'message': 'Timeout'}
