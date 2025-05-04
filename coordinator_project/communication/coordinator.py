"""
Coordinator: Gère la communication entre les managers et les volunteers.
Utilise Redis pour le pub/sub et MongoDB pour le stockage persistant.
"""

import json
import secrets
from datetime import datetime
import redis
from typing import Dict, Any, List

from .models import ConnectionState
from .constants import (
    REGISTRATION_CHANNEL,
    MANAGER_TASKS_CHANNEL,
    VOLUNTEER_TASKS_CHANNEL,
    VOLUNTEER_STATUS_CHANNEL,
    VOLUNTEER_RESULTS_CHANNEL,
    MANAGER_STATUS_CHANNEL,
    AUTH_CHANNEL
)

class Coordinator:
    """
    Classe principale qui coordonne toute la communication du système.
    Gère les inscriptions, les tâches, les résultats et les états.
    """

    def __init__(self, redis_host='localhost', redis_port=6379):
        """
        Initialise le coordinateur avec une connexion Redis.
        
        Args:
            redis_host (str): Hôte Redis (défaut: localhost)
            redis_port (int): Port Redis (défaut: 6379)
        """
        # Connexion principale à Redis
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True  # Décode automatiquement les réponses en UTF-8
        )
        
        # Client pub/sub pour la messagerie
        self.pubsub = self.redis.pubsub()
        
        # Abonnement aux canaux principaux
        self.pubsub.subscribe(REGISTRATION_CHANNEL)     # Inscriptions
        self.pubsub.subscribe(MANAGER_TASKS_CHANNEL)    # Nouvelles tâches
        self.pubsub.subscribe(VOLUNTEER_STATUS_CHANNEL) # États des volunteers
        self.pubsub.subscribe(VOLUNTEER_RESULTS_CHANNEL)# Résultats des tâches

    def generate_token(self) -> str:
        """
        Génère un token sécurisé pour l'authentification.
        
        Returns:
            str: Token sécurisé de 32 bytes encodé en base64
        """
        return secrets.token_urlsafe(32)

    def get_channels_for_client(self, client_type: str) -> List[str]:
        """
        Détermine les canaux autorisés selon le type de client.
        
        Args:
            client_type (str): Type de client ('manager' ou 'volunteer')
        
        Returns:
            List[str]: Liste des canaux autorisés
        """
        if client_type == 'manager':
            return [
                MANAGER_TASKS_CHANNEL,     # Pour envoyer des tâches
                MANAGER_STATUS_CHANNEL,    # Pour recevoir les états
                VOLUNTEER_RESULTS_CHANNEL  # Pour recevoir les résultats
            ]
        return [
            VOLUNTEER_TASKS_CHANNEL,     # Pour recevoir des tâches
            VOLUNTEER_STATUS_CHANNEL,    # Pour envoyer son état
            VOLUNTEER_RESULTS_CHANNEL    # Pour envoyer les résultats
        ]

    def validate_token(self, client_id: str, token: str) -> bool:
        """
        Valide le token d'authentification d'un client.
        
        Args:
            client_id (str): ID unique du client
            token (str): Token à valider
        
        Returns:
            bool: True si valide, False sinon
        """
        try:
            # Vérifie si le token est valide et le client connecté
            ConnectionState.objects.get(
                client_id=client_id,
                token=token,
                is_connected=True
            )
            return True
        except ConnectionState.DoesNotExist:
            return False

    def handle_registration(self, message_data: Dict[str, Any]):
        """
        Gère les demandes d'inscription des clients.
        
        Args:
            message_data (Dict): Données d'inscription
        """
        message_type = message_data.get('message_type')
        
        if message_type == 'manager_registration':
            try:
                # 1. Vérifie si le manager existe
                manager = Manager.objects.get(username=message_data['username'])
                
                # 2. Génère les identifiants
                client_id = f"manager_{secrets.token_hex(4)}"
                token = self.generate_token()
                
                # 3. Crée l'état de connexion
                ConnectionState(
                    client_id=client_id,
                    client_type='manager',
                    token=token,
                    connection_metadata={
                        'username': message_data['username'],
                        'email': message_data['email']
                    }
                ).save()
                
                # 4. Envoie la réponse d'authentification
                channels = self.get_channels_for_client('manager')
                auth_response = {
                    'client_id': client_id,
                    'token': token,
                    'channels': channels,
                    'status': 'active'
                }
                self.redis.publish(AUTH_CHANNEL, json.dumps(auth_response))
                
            except Manager.DoesNotExist:
                print(f"Manager non trouvé: {message_data['username']}")

    def handle_task(self, message_data: Dict[str, Any]):
        """
        Gère les tâches soumises par les managers.
        
        Args:
            message_data (Dict): Données de la tâche
        """
        # 1. Validation du token
        client_id = message_data.get('client_id')
        token = message_data.get('token')
        
        if not self.validate_token(client_id, token):
            print(f"Token invalide pour {client_id}")
            return
            
        try:
            # 2. Met à jour la tâche
            task = Task.objects.get(id=message_data['task_id'])
            task.status = 'PENDING'
            task.save()
            
            # 3. Transfère aux volunteers
            self.redis.publish(VOLUNTEER_TASKS_CHANNEL, json.dumps(message_data))
            
        except Task.DoesNotExist:
            print(f"Tâche non trouvée: {message_data['task_id']}")

    def handle_result(self, message_data: Dict[str, Any]):
        """
        Gère les résultats envoyés par les volunteers.
        
        Args:
            message_data (Dict): Données du résultat
        """
        # 1. Validation du token
        client_id = message_data.get('volunteer_id')
        token = message_data.get('token')
        
        if not self.validate_token(client_id, token):
            return
            
        try:
            # 2. Met à jour la tâche avec les résultats
            task = Task.objects.get(id=message_data['task_id'])
            task.status = message_data['status']
            task.results = message_data.get('results', {})
            task.end_time = datetime.utcnow()
            task.save()
            
            # 3. Informe le manager
            self.redis.publish(MANAGER_STATUS_CHANNEL, json.dumps(message_data))
            
        except Task.DoesNotExist:
            print(f"Tâche non trouvée: {message_data['task_id']}")

    def handle_volunteer_status(self, message_data: Dict[str, Any]):
        """
        Gère les mises à jour d'état des volunteers.
        
        Args:
            message_data (Dict): Données d'état
        """
        # 1. Validation du token
        client_id = message_data.get('volunteer_id')
        token = message_data.get('token')
        
        if not self.validate_token(client_id, token):
            return
            
        try:
            # 2. Met à jour l'état du volunteer
            volunteer = Volunteer.objects.get(id=client_id)
            volunteer.current_status = message_data['current_status']
            volunteer.last_update = datetime.utcnow()
            volunteer.save()
            
            # 3. Met à jour l'état de connexion
            conn_state = ConnectionState.objects.get(client_id=client_id)
            conn_state.last_heartbeat = datetime.utcnow()
            conn_state.save()
            
        except Volunteer.DoesNotExist:
            print(f"Volunteer non trouvé: {client_id}")

    def run(self):
        """
        Boucle principale du coordinateur.
        Écoute et traite en continu les messages de tous les canaux.
        """
        print("Démarrage du Coordinateur...")
        
        while True:  # Boucle infinie
            # 1. Récupère un message
            message = self.pubsub.get_message()
            
            # 2. Traite uniquement les vrais messages (pas les messages système)
            if message and message['type'] == 'message':
                try:
                    # 3. Parse le JSON
                    data = json.loads(message['data'])
                    channel = message['channel']
                    
                    # 4. Route vers le bon gestionnaire
                    if channel == REGISTRATION_CHANNEL:
                        self.handle_registration(data)
                    elif channel == MANAGER_TASKS_CHANNEL:
                        self.handle_task(data)
                    elif channel == VOLUNTEER_RESULTS_CHANNEL:
                        self.handle_result(data)
                    elif channel == VOLUNTEER_STATUS_CHANNEL:
                        self.handle_volunteer_status(data)
                        
                except json.JSONDecodeError:
                    print(f"Message mal formaté: {message['data']}")
                except Exception as e:
                    print(f"Erreur de traitement: {str(e)}")

if __name__ == '__main__':
    coordinator = Coordinator()
    coordinator.run()
