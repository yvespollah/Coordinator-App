"""
Services pour l'enregistrement des messages pub/sub
"""
import json
import logging
from .models import MessageLog

logger = logging.getLogger(__name__)

def log_message(sender_type, sender_id, channel, request_id, message_type, content, receiver_type=None, receiver_id=None):
    """
    Enregistre un message pub/sub dans la base de données
    
    Args:
        sender_type (str): Type de l'expéditeur (manager, volunteer, coordinator)
        sender_id (str): ID réel de l'expéditeur
        channel (str): Canal sur lequel le message a été publié
        request_id (str): ID de la requête
        message_type (str): Type du message (request, response)
        content (dict): Contenu du message
        receiver_type (str, optional): Type du destinataire
        receiver_id (str, optional): ID du destinataire
        
    Returns:
        MessageLog: L'objet MessageLog créé
    """
    try:
        # Convertir le contenu en JSON s'il ne l'est pas déjà
        if isinstance(content, dict):
            content_json = json.dumps(content)
        else:
            content_json = content
            
        # Créer l'entrée de log
        message_log = MessageLog.objects.create(
            sender_type=sender_type,
            sender_id=sender_id,
            receiver_type=receiver_type,
            receiver_id=receiver_id,
            channel=channel,
            request_id=request_id,
            message_type=message_type,
            content=content_json
        )
        
        logger.info(f"Message enregistré: {sender_type}:{sender_id} -> {channel}")
        return message_log
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du message: {e}")
        return None
