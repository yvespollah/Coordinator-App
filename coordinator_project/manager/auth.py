"""
Utilitaires d'authentification pour les managers.
Gère la génération et la vérification des tokens JWT.
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import Manager

def generate_manager_token(manager_id, expiration_hours=24):
    """
    Génère un token JWT pour un manager.
    
    Args:
        manager_id: ID du manager
        expiration_hours: Durée de validité du token en heures
        
    Returns:
        str: Token JWT
    """
    payload = {
        'user_id': str(manager_id),
        'role': 'manager',
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    
    return token

def verify_manager_token(token):
    """
    Vérifie un token JWT de manager.
    
    Args:
        token: Token JWT à vérifier
        
    Returns:
        tuple: (is_valid, manager_id, error_message)
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Vérifier le rôle
        if payload.get('role') != 'manager':
            return False, None, "Invalid role"
        
        # Vérifier que le manager existe
        manager_id = payload.get('user_id')
        try:
            manager = Manager.objects.get(id=manager_id)
            if manager.status != 'active':
                return False, None, "Manager account is not active"
            return True, manager_id, None
        except Manager.DoesNotExist:
            return False, None, "Manager not found"
        
    except jwt.ExpiredSignatureError:
        return False, None, "Token expired"
    except jwt.InvalidTokenError:
        return False, None, "Invalid token"
    except Exception as e:
        return False, None, str(e)
