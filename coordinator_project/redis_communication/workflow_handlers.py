"""
Gestionnaires pour les workflows dans le système de communication Redis.
"""

import json
import logging
import uuid
import traceback
from typing import Dict, Any, Optional
from django.utils import timezone

from redis_communication.client import RedisClient
from redis_communication.message import Message
from redis_communication.utils import verify_token
from redis_communication.handlers import save_pending_request, delete_pending_request

logger = logging.getLogger(__name__)

def workflow_submission_handler(channel: str, message: Message):
    """
    Gestionnaire pour les soumissions de workflows.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    try:
        logger.info(f"Demande de soumission de workflow reçue: {message.to_dict()}")
        
        # Extraire les données du message
        data = message.data
        request_id = message.request_id
        
        
        
        # Enregistrer la requête en attente
        save_pending_request(request_id, data)
        
        # Extraire les informations du workflow
        workflow_id = data.get('workflow_id')
        workflow_name = data.get('workflow_name')
        workflow_type = data.get('workflow_type')
        owner = data.get('owner', '')
        estimated_resources = data.get('estimated_resources', {})
        
        logger.info(f"Workflow {workflow_name} ({workflow_id}) soumis par {owner}")
        
        # Vérifier les ressources estimées
        if not estimated_resources:
            logger.warning(f"Aucune ressource estimée fournie pour le workflow {workflow_id}")
            estimated_resources = {
                "estimated_cpu_cores": 2,
                "estimated_memory_mb": 1024,
                "estimated_disk_space_mb": 500,
                "gpu_required": False
            }


        # Enregistrer le workflow dans la base de données
        from manager.models import Workflow, Manager
        manager = Manager.objects.get(id=owner)
        workflow = Workflow(
            id=workflow_id,
            name=workflow_name,
            description=data.get('description', ''),
            workflow_type=workflow_type,
            owner=manager,
            estimated_resources=estimated_resources,
            priority=data.get('priority', 1),
        )
        workflow.save()        


        
        # TODO: Rechercher des volontaires disponibles avec les ressources nécessaires
        # Pour l'instant, simuler une réponse positive
        
        # Générer un ID de workflow pour le coordinateur

        # Récupérer la liste des volontaires disponibles depuis la base de données
        from .utils import get_available_volunteers
        assigned_volunteers = get_available_volunteers()
        
        # Si aucun volontaire n'est disponible, utiliser des données de test
        if not assigned_volunteers:
            logger.warning("Aucun volontaire disponible dans la base de données, utilisation de données de test")
            assigned_volunteers = [
                {
                    "volunteer_id": str(uuid.uuid4()),
                    "username": "volunteer1_test",
                    "resources": {
                        "cpu_cores": 1,
                        "memory_mb": 1024,
                        "disk_space_mb": 1024,
                        "gpu": False
                    }
                },
                {
                    "volunteer_id": str(uuid.uuid4()),
                    "username": "volunteer2_test",
                    "resources": {
                        "cpu_cores": 2,
                        "memory_mb": 2048,
                        "disk_space_mb": 2000,
                        "gpu": False
                    }
                }
            ] 
        else:
            logger.error(f"Utilisation de {assigned_volunteers} volontaires réels pour le workflow")
        
        # Envoyer une réponse de succès
        client = RedisClient.get_instance()
        from .utils import get_coordinator_token
        token = get_coordinator_token()
        client.publish('workflow/submit_response', {
            'status': 'success',
            'message': 'Workflow accepté',
            'workflow_id': str(workflow.id),
            'volunteers': assigned_volunteers
        }, request_id=request_id, token=token, message_type="response")
        
        logger.info(f"Workflow {workflow.id} accepté")
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la soumission du workflow: {e}")
        logger.error(traceback.format_exc())
        
        try:
            # Récupérer l'ID du workflow s'il existe
            workflow_id = message.data.get('workflow_id', 'inconnu')
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            from .utils import get_coordinator_token
            token = get_coordinator_token()
            client.publish('workflow/submit_response', {
                'status': 'error',
                'message': f"Erreur lors du traitement: {str(e)}",
                'workflow_id': workflow_id
            }, request_id=message.request_id, token=token, message_type="response")
            
            # Supprimer la requête en attente si elle existe
            delete_pending_request(message.request_id)
            
        except Exception as inner_e:
            logger.error(f"Erreur lors de l'envoi de la réponse d'erreur: {inner_e}")
