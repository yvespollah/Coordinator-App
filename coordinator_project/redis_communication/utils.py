"""
Utilitaires divers pour le module de communication Redis.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
import jwt
from django.conf import settings
from volunteer.models import Volunteer

logger = logging.getLogger(__name__)

def generate_token(user_id: str, role: str, expiration_hours: int = 24) -> str:
    """
    Génère un token JWT pour l'authentification.
    
    Args:
        user_id: ID du client
        role: Type de client (coordinator, manager, volunteer)
        expiration_hours: Durée de validité en heures
        
    Returns:
        str: Token JWT
    """
    secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
    
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': int(time.time()) + expiration_hours * 3600,
        'iat': int(time.time())
    }
    
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Vérifie un token JWT.
    
    Args:
        token: Token JWT à vérifier
        
    Returns:
        Dict ou None: Payload du token si valide, None sinon
    """
    secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expiré")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token invalide")
        return None

def format_timestamp(timestamp: float) -> str:
    """
    Formate un timestamp en chaîne ISO 8601.
    
    Args:
        timestamp: Timestamp UNIX
        
    Returns:
        str: Chaîne au format ISO 8601
    """
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).isoformat()



def get_available_volunteers() -> List[Dict[str, Any]]:
    """
    Récupère la liste des volontaires disponibles depuis la base de données.
    
    Returns:
        List[Dict[str, Any]]: Liste des volontaires avec leurs informations de ressources
    """
    try:
        # Récupérer tous les volontaires avec le statut 'available'
        volunteers = Volunteer.objects.filter(current_status='available')
        
        # Formater les données des volontaires pour le workflow
        formatted_volunteers = []
        for volunteer in volunteers:
            formatted_volunteer = {
                "volunteer_id": str(volunteer.id),
                "username": volunteer.username,
                "resources": {
                    "cpu_cores": volunteer.cpu_cores,
                    "memory_mb": volunteer.total_ram,
                    "disk_space_mb": volunteer.available_storage * 1024,  # Convertir GB en MB
                    "gpu": volunteer.gpu_available
                }
            }
            formatted_volunteers.append(formatted_volunteer)
        
        logger.error(f"Récupéré {formatted_volunteers} volontaires disponibles")
        return formatted_volunteers
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des volontaires: {e}")
        # En cas d'erreur, retourner une liste vide
        return []

def get_coordinator_token():
    """
    Récupère le token JWT du coordinateur.
    
    Returns:
        str: Token JWT
    """
    try:
        with open('.coordinator/redis_communication/token', 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("Le fichier token n'a pas été trouvé")
        return None