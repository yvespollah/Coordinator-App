"""
Gestionnaires pour les événements de statut et progression des tâches.
"""

import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any

from redis_communication.message import Message
from redis_communication.volunteer_performance_handlers import update_volunteer_score
from manager.models import Task, TaskAssignment

logger = logging.getLogger(__name__)

def handle_task_started(channel: str, message: Message):
    """
    Gestionnaire pour l'événement de démarrage d'une tâche.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')

        if not task_id or not volunteer_id:
            logger.error("Task ID ou Volunteer ID manquant")
            return

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status='ASSIGNED'
        )
        assignment.status = 'STARTED'
        assignment.started_at = datetime.now(timezone.utc)
        assignment.save()

        # Mettre à jour la tâche
        task = Task.objects.get(id=task_id)
        task.status = 'RUNNING'
        task.start_time = datetime.now(timezone.utc)
        task.save()

        logger.info(f"Tâche {task_id} démarrée par le volontaire {volunteer_id}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement du démarrage de la tâche: {e}")
        logger.error(traceback.format_exc())

def handle_task_progress(channel: str, message: Message):
    """
    Gestionnaire pour les mises à jour de progression des tâches.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')
        progress = data.get('progress', 0)

        if not all([task_id, volunteer_id]):
            logger.error("Données manquantes dans la mise à jour de progression")
            return

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status__in=['STARTED', 'RESUMED']
        )
        assignment.progress = progress
        assignment.save()

        # Mettre à jour la tâche
        task = Task.objects.get(id=task_id)
        task.progress = progress
        task.save()

        logger.info(f"Progression de la tâche {task_id}: {progress}%")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la progression: {e}")
        logger.error(traceback.format_exc())

def handle_task_completed(channel: str, message: Message):
    """
    Gestionnaire pour la complétion des tâches.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')
        results = data.get('results', {})

        if not all([task_id, volunteer_id]):
            logger.error("Données manquantes dans la notification de complétion")
            return

        now = datetime.now(timezone.utc)

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status__in=['STARTED', 'RESUMED']
        )
        assignment.status = 'COMPLETED'
        assignment.completed_at = now
        assignment.progress = 100
        if assignment.started_at:
            assignment.completion_time = (now - assignment.started_at).total_seconds()
        assignment.save()

        # Mettre à jour la tâche
        task = Task.objects.get(id=task_id)
        task.status = 'COMPLETED'
        task.progress = 100
        task.end_time = now
        task.results = results
        task.save()

        # Mettre à jour le score du volontaire
        update_volunteer_score(volunteer_id, 'completed', task_id)

        logger.info(f"Tâche {task_id} terminée avec succès par le volontaire {volunteer_id}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de la complétion de la tâche: {e}")
        logger.error(traceback.format_exc())

def handle_task_failed(channel: str, message: Message):
    """
    Gestionnaire pour les échecs de tâches.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')
        error = data.get('error')

        if not all([task_id, volunteer_id]):
            logger.error("Données manquantes dans la notification d'échec")
            return

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status__in=['STARTED', 'RESUMED']
        )
        assignment.status = 'FAILED'
        assignment.completed_at = datetime.now(timezone.utc)
        assignment.failure_reason = error
        assignment.save()

        # Mettre à jour la tâche
        task = Task.objects.get(id=task_id)
        task.status = 'FAILED'
        task.end_time = datetime.now(timezone.utc)
        task.error_details = {'error': error, 'volunteer_id': str(volunteer_id)}
        task.attempts += 1
        task.save()

        # Mettre à jour le score du volontaire
        update_volunteer_score(volunteer_id, 'failed', task_id)

        logger.error(f"Tâche {task_id} échouée par le volontaire {volunteer_id}: {error}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'échec de la tâche: {e}")
        logger.error(traceback.format_exc())

def handle_task_paused(channel: str, message: Message):
    """
    Gestionnaire pour la mise en pause des tâches.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')

        if not all([task_id, volunteer_id]):
            logger.error("Données manquantes dans la notification de pause")
            return

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status__in=['STARTED', 'RESUMED']
        )
        assignment.status = 'PAUSED'
        assignment.save()

        # Mettre à jour la tâche 
        task = Task.objects.get(id=task_id)
        task.status = 'PAUSED'
        task.save()

        logger.info(f"Tâche {task_id} mise en pause par le volontaire {volunteer_id}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de la pause de la tâche: {e}")
        logger.error(traceback.format_exc())

def handle_task_resumed(channel: str, message: Message):
    """
    Gestionnaire pour la reprise des tâches.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')

        if not all([task_id, volunteer_id]):
            logger.error("Données manquantes dans la notification de reprise")
            return

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status='PAUSED'
        )
        assignment.status = 'RESUMED'
        assignment.save()

        # Mettre à jour la tâche
        task = Task.objects.get(id=task_id)
        task.status = 'RUNNING'
        task.save()

        logger.info(f"Tâche {task_id} reprise par le volontaire {volunteer_id}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de la reprise de la tâche: {e}")
        logger.error(traceback.format_exc())

def handle_task_timeout(channel: str, message: Message):
    """
    Gestionnaire pour les timeouts de tâches.
    """
    try:
        data = message.data
        task_id = data.get('task_id')
        volunteer_id = data.get('volunteer_id')

        if not all([task_id, volunteer_id]):
            logger.error("Données manquantes dans la notification de timeout")
            return

        # Mettre à jour l'assignation
        assignment = TaskAssignment.objects.get(
            task=task_id,
            volunteer=volunteer_id,
            status__in=['STARTED', 'RESUMED']
        )
        assignment.status = 'TIMEOUT'
        assignment.completed_at = datetime.now(timezone.utc)
        assignment.failure_reason = "Task execution timeout"
        assignment.save()

        # Mettre à jour la tâche
        task = Task.objects.get(id=task_id)
        task.status = 'FAILED'
        task.end_time = datetime.now(timezone.utc)
        task.error_details = {
            'error': 'Task execution timeout',
            'volunteer_id': str(volunteer_id)
        }
        task.attempts += 1
        task.save()

        # Mettre à jour le score du volontaire
        update_volunteer_score(volunteer_id, 'timeout', task_id)

        logger.warning(f"Timeout pour la tâche {task_id} sur le volontaire {volunteer_id}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement du timeout de la tâche: {e}")
        logger.error(traceback.format_exc())

def register_handlers(client):
    """
    Enregistre les gestionnaires d'événements pour le statut des tâches.
    """
    client.subscribe('task/started', handle_task_started)
    client.subscribe('task/progress', handle_task_progress)
    client.subscribe('task/completed', handle_task_completed)
    client.subscribe('task/failed', handle_task_failed)
    client.subscribe('task/paused', handle_task_paused)
    client.subscribe('task/resumed', handle_task_resumed)
    client.subscribe('task/timeout', handle_task_timeout)

    logger.info("Gestionnaires de statut des tâches enregistrés")