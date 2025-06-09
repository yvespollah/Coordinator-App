"""
Gestionnaires pour les demandes d'assignation et de réassignation de tâches.
"""

import json
import logging
import traceback
import uuid
from typing import Dict, Any, Optional
from django.utils import timezone

from redis_communication.client import RedisClient
from redis_communication.message import Message
from redis_communication.utils import get_coordinator_token, get_available_volunteers
from task.models import Task
from volunteer.models import Volunteer
from manager.models import Manager

logger = logging.getLogger(__name__)

def task_assignment_request_handler(channel: str, message: Message):
    """
    Gestionnaire pour les demandes de réassignation de tâches.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    try:
        logger.info(f"Demande de réassignation de tâche reçue: {message.to_dict()}")
        
        # Extraire les données du message
        data = message.data
        
        # Vérifier si les données nécessaires sont présentes
        if not data or 'task_id' not in data:
            logger.error(f"Données manquantes dans le message: {data}")
            return
        
        task_id = data.get('task_id')
        manager_id = data.get('manager_id')
        estimated_resources = data.get('estimated_resources', {})
        
        # Récupérer la tâche
        from manager.models import Task
        task = Task.objects.filter(id=task_id).first()
        if not task:
            logger.error(f"Tâche non trouvée: {task_id}")
            # Envoyer une réponse d'erreur
            send_assignment_response(task_id, manager_id, success=False, error="Tâche non trouvée")
            return
        
        # Récupérer le manager
        manager = None
        if manager_id:
            manager = Manager.objects.filter(id=manager_id).first()
            if not manager:
                logger.warning(f"Manager non trouvé: {manager_id}")
        
        # Marquer la tâche comme en attente de réassignation
        task.status = 'pending_reassignment'
        task.save()
        
        # Rechercher des volontaires disponibles avec les ressources nécessaires
        available_volunteers = get_available_volunteers()
        
        # Filtrer les volontaires en fonction des ressources estimées
        suitable_volunteers = []
        for volunteer in available_volunteers:
            if meets_resource_requirements(volunteer, estimated_resources):
                suitable_volunteers.append(volunteer)
        
        if not suitable_volunteers:
            logger.warning(f"Aucun volontaire disponible pour la tâche {task_id}")
            # Envoyer une réponse d'échec
            send_assignment_response(task_id, manager_id, success=False, error="Aucun volontaire disponible")
            return
        
        # Trier les volontaires par score de confiance décroissant
        suitable_volunteers.sort(
            key=lambda v: v.get('performance', {}).get('trust_score', 0), 
            reverse=True
        )
        
        # Sélectionner le meilleur volontaire
        selected_volunteer = suitable_volunteers[0]
        volunteer_id = selected_volunteer['volunteer_id']
        
        # Mettre à jour la tâche avec le nouveau volontaire
        task.assigned_volunteer = volunteer_id
        task.status = 'assigned'
        task.save()
        
        
        # Envoyer une réponse de succès au manager
        send_assignment_response(task_id, manager_id, success=True, volunteer_id=volunteer_id)
        
        logger.info(f"Tâche {task_id} réassignée au volontaire {volunteer_id}")
    
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire de demande d'assignation de tâche: {e}")
        logger.error(traceback.format_exc())
        
        # Envoyer une réponse d'erreur
        send_assignment_response(
            task_id=data.get('task_id') if data and 'task_id' in data else None,
            manager_id=data.get('manager_id') if data and 'manager_id' in data else None,
            success=False,
            error=str(e)
        )

def meets_resource_requirements(volunteer: Dict[str, Any], required_resources: Dict[str, Any]) -> bool:
    """
    Vérifie si un volontaire répond aux exigences de ressources.
    
    Args:
        volunteer: Informations du volontaire
        required_resources: Ressources requises
        
    Returns:
        bool: True si le volontaire répond aux exigences, False sinon
    """
    if not required_resources:
        return True
    
    volunteer_resources = volunteer.get('resources', {})
    
    # Vérifier les ressources CPU
    if 'cpu_cores' in required_resources and volunteer_resources.get('cpu_cores', 0) < required_resources['cpu_cores']:
        return False
    
    # Vérifier la mémoire
    if 'memory_mb' in required_resources and volunteer_resources.get('memory_mb', 0) < required_resources['memory_mb']:
        return False
    
    # Vérifier l'espace disque
    if 'disk_space_mb' in required_resources and volunteer_resources.get('disk_space_mb', 0) < required_resources['disk_space_mb']:
        return False
    
    # Vérifier le GPU
    if 'gpu' in required_resources and required_resources['gpu'] and not volunteer_resources.get('gpu', False):
        return False
    
    return True

def send_assignment_response(task_id, manager_id, success, volunteer_id=None, error=None):
    """
    Envoie une réponse à une demande d'assignation de tâche.
    
    Args:
        task_id: ID de la tâche
        manager_id: ID du manager
        success: Indique si l'assignation a réussi
        volunteer_id: ID du volontaire assigné (si succès)
        error: Message d'erreur (si échec)
    """
    client = RedisClient.get_instance()
    token = get_coordinator_token()
    
    # Préparer les données pour Redis
    data = {
        'task_id': str(task_id) if task_id else None,
        'manager_id': str(manager_id) if manager_id else None,
        'success': success,
        'timestamp': timezone.now().isoformat()
    }
    
    if success and volunteer_id:
        data['volunteer_id'] = volunteer_id
    
    if not success and error:
        data['error'] = error
    
    # Publier le message
    client.publish(
        'task/reassignment/response',
        data,
        request_id=str(uuid.uuid4()),
        token=token,
        message_type='response',
        real_sender_id='coordinator'
    )
    
    logger.info(f"Réponse d'assignation envoyée au manager {manager_id} pour la tâche {task_id}: {'succès' if success else 'échec'}")

def register_handlers():
    """
    Enregistre les gestionnaires d'événements pour les assignations de tâches.
    """
    client = RedisClient.get_instance()
    
    # Enregistrer le gestionnaire pour les demandes de réassignation de tâches
    # Le manager utilise 'task/reassignment' pour les demandes de réassignation
    client.subscribe('task/reassignment', task_assignment_request_handler)
    
    logger.info("Gestionnaires d'assignation de tâches enregistrés")
