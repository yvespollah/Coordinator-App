"""
Gestionnaires pour la gestion des performances des volontaires.
"""

import json
import logging
import traceback
from typing import Dict, Any, Optional
from django.utils import timezone

from redis_communication.client import RedisClient
from redis_communication.message import Message
from volunteer.models import Volunteer
from manager.models import TaskAssignment, Task, Workflow

logger = logging.getLogger(__name__)

# Dictionnaire pour suivre les tâches déjà traitées et éviter les doublons
processed_task_events = {}

def update_volunteer_score(volunteer_id: str, task_status: str, task_id: str = None):
    """
    Met à jour le score de confiance d'un volontaire en fonction du statut de la tâche.
    
    Args:
        volunteer_id: ID du volontaire
        task_status: Statut de la tâche (completed, failed, etc.)
        task_id: ID de la tâche (pour éviter les doublons)
    
    Returns:
        bool: True si la mise à jour a réussi, False sinon
    """
    try:
        # Éviter les doublons de traitement pour une même tâche
        if task_id:
            event_key = f"{volunteer_id}_{task_id}_{task_status}"
            if event_key in processed_task_events:
                logger.info(f"Événement déjà traité: {event_key}")
                return False
            processed_task_events[event_key] = True
        
        # Récupérer le volontaire
        volunteer = Volunteer.objects(id=volunteer_id).first()
        if not volunteer:
            logger.error(f"Volontaire non trouvé: {volunteer_id}")
            return False
        
        # Initialiser les performances si nécessaire
        if 'tasks_total' not in volunteer.performance:
            volunteer.performance['tasks_total'] = 0
        if 'tasks_completed' not in volunteer.performance:
            volunteer.performance['tasks_completed'] = 0
        if 'tasks_failed' not in volunteer.performance:
            volunteer.performance['tasks_failed'] = 0
        
        # Mettre à jour les compteurs
        volunteer.performance['tasks_total'] = int(volunteer.performance.get('tasks_total', 0)) + 1
        
        if task_status.lower() in ['completed', 'success', 'done']:
            volunteer.performance['tasks_completed'] = int(volunteer.performance.get('tasks_completed', 0)) + 1
        elif task_status.lower() in ['failed', 'error', 'timeout']:
            volunteer.performance['tasks_failed'] = int(volunteer.performance.get('tasks_failed', 0)) + 1
        
        # Calculer le score de confiance
        tasks_completed = int(volunteer.performance.get('tasks_completed', 0))
        tasks_total = int(volunteer.performance.get('tasks_total', 0))
        
        if tasks_total > 0:
            trust_score = (tasks_completed / tasks_total) * 100
            volunteer.performance['trust_score'] = round(trust_score, 2)
        else:
            volunteer.performance['trust_score'] = 0
        
        # Enregistrer les modifications
        volunteer.save()
        
        logger.info(f"Score de confiance mis à jour pour {volunteer_id}: {volunteer.performance}")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du score: {e}")
        logger.error(traceback.format_exc())
        return False

def task_status_handler(channel: str, message: Message):
    """
    Gestionnaire pour les mises à jour de statut des tâches.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    try:
        logger.info(f"Mise à jour de statut de tâche reçue: {message.to_dict()}")
        
        # Extraire les données du message
        data = message.data
        
        # Vérifier si les données nécessaires sont présentes
        if not data or 'task_id' not in data or 'status' not in data or 'volunteer_id' not in data:
            logger.error(f"Données manquantes dans le message: {data}")
            return
        
        task_id = data.get('task_id')
        status = data.get('status')
        volunteer_id = data.get('volunteer_id')
        
        # Mettre à jour le score du volontaire
        if status.lower() in ['completed', 'success', 'done', 'failed', 'error', 'timeout']:
            update_volunteer_score(volunteer_id, status, task_id)
    
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire de statut de tâche: {e}")
        logger.error(traceback.format_exc())

def task_assignment_handler(channel: str, message: Message):
    """
    Gestionnaire pour les assignations de tâches.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    try:
        logger.info(f"Assignation de tâche reçue: {message.to_dict()}")
        
        # Extraire les données du message
        data = message.data
        
        # Vérifier si les assignments sont présents
        if not data or 'assignments' not in data:
            logger.error(f"Données d'assignation manquantes dans le message: {data}")
            return

        # Traiter chaque groupe d'assignations
        for volunteer_id, tasks_data in data['assignments'].items():
            volunteer = Volunteer.objects(id=volunteer_id).first()
            workflow = Workflow.objects(id=data.get('workflow_id')).first() 
            if not workflow:
                logger.error(f"Workflow non trouvé pour l'ID: {data.get('workflow_id')}")
                continue
            if not volunteer:
                logger.error(f"Volontaire non trouvé: {volunteer_id}")
                continue

            # Traiter chaque tâche assignée au volontaire
            for task_data in tasks_data:
                try:
                    # Récupérer ou créer la tâche
                    task_id = task_data.get('task_id')
                    task = Task.objects(id=task_id).first()
                    
                    if not task:
                        # Créer la tâche si elle n'existe pas
                        task = Task(
                            id=task_id,
                            workflow=workflow,
                            name=task_data.get('name', ''),
                            description=task_data.get('description', ''),
                            command=task_data.get('command', ''),
                            dependencies=task_data.get('dependencies', []),
                            status='PENDING',
                            is_subtask=task_data.get('is_subtask', False),
                            progress=0,
                            created_at=timezone.now(),
                            start_time=None,
                            end_time=None,
                            required_resources=task_data.get('required_resources', {}), 
                            attempts= workflow.attempts or 3,
                            metadata = {'file_server': task_data.get('file_server')},
                            estimated_execution_time=task_data.get('estimated_execution_time', 0),
                            input_data=task_data.get('input_data', {}),
                            docker_information= dict(task_data.get('docker_information', {})),
                            input_data_size=task_data.get('input_data_size', 0),
                            parameters=task_data.get('parameters', []),
                        )
                        task.save()

                    # Créer l'assignation
                    assignment = TaskAssignment(
                        task=task,
                        volunteer=volunteer,
                        status='ASSIGNED',
                        assigned_at=timezone.now()
                    )
                    assignment.save()

                    # Mettre à jour la tâche
                    task.assigned_to = volunteer
                    task.save()

                    # Mettre à jour le volontaire
                    volunteer.last_activity = timezone.now()
                    if not hasattr(volunteer, 'performance'):
                        volunteer.performance = {}
                    volunteer.performance['tasks_total'] = volunteer.performance.get('tasks_total', 0) + 1
                    volunteer.save()

                    logger.info(f"Tâche {task_id} assignée au volontaire {volunteer_id}")

                except Exception as e:
                    logger.error(f"Erreur lors de l'assignation de la tâche {task_data.get('task_id')}: {e}")
                    logger.error(traceback.format_exc())
                    continue

    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire d'assignation de tâche: {e}")
        logger.error(traceback.format_exc())

def register_handlers():
    """
    Enregistre les gestionnaires d'événements pour les performances des volontaires.
    """
    client = RedisClient.get_instance()
    
    # Enregistrer les gestionnaires pour les mises à jour de statut des tâches
    client.subscribe('task/status', task_status_handler)
    
    # Enregistrer les gestionnaires pour les assignations de tâches
    client.subscribe('task/assignment', task_assignment_handler)
    
    logger.info("Gestionnaires de performances des volontaires enregistrés")
