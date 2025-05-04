import sys
import os
import json
import time
import redis
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coordinator_project.communication.messages import (
    ManagerRegistrationMessage,
    VolunteerRegistrationMessage,
    AuthResponseMessage,
    TaskMessage,
    ResultMessage,
    VolunteerStatusMessage
)
from coordinator_project.communication.constants import *

# Nouveaux canaux (correspondant à ceux de broker.py)
AUTH_REGISTER_CHANNEL = "auth/register"
AUTH_RESPONSE_CHANNEL = "auth/response"
TASKS_NEW_CHANNEL = "tasks/new"
TASKS_ASSIGN_CHANNEL = "tasks/assign"
TASKS_STATUS_CHANNEL = "tasks/status"
TASKS_RESULT_CHANNEL = "tasks/result"
VOLUNTEER_AVAILABLE_CHANNEL = "volunteer/available"
VOLUNTEER_RESOURCES_CHANNEL = "volunteer/resources"
MANAGER_STATUS_CHANNEL = "manager/status"

class TestClient:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.token = None
        self.client_id = None
        self.channels = []
        
    def subscribe(self, channel):
        """Subscribe to a channel"""
        self.pubsub.subscribe(channel)
        print(f"Abonné au canal: {channel}")
        
    def publish(self, channel, message):
        """Publish a message to a channel"""
        if isinstance(message, (ManagerRegistrationMessage, VolunteerRegistrationMessage,
                              AuthResponseMessage, TaskMessage, ResultMessage,
                              VolunteerStatusMessage)):
            message = json.dumps(message.to_dict())
        elif isinstance(message, dict):
            message = json.dumps(message)
            
        self.redis.publish(channel, message)
        print(f"Message publié sur {channel}: {message[:100]}...")
        
    def get_message(self):
        """Get a message from subscribed channels"""
        message = self.pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                return json.loads(message['data'])
            except json.JSONDecodeError:
                return {"raw_data": message['data']}
        return None

def simulate_manager():
    """Simulate a manager client"""
    manager = TestClient()
    
    # S'abonner aux canaux pertinents
    manager.subscribe(AUTH_RESPONSE_CHANNEL)
    manager.subscribe(TASKS_RESULT_CHANNEL + "/#")  # Wildcard pour tous les résultats
    
    # Enregistrer en tant que manager
    reg_data = {
        'username': 'test_manager',
        'email': 'manager@test.com',
        'password': 'test123',
        'status': 'active'
    }
    
    print("Manager: Envoi de l'enregistrement...")
    manager.publish(AUTH_REGISTER_CHANNEL, reg_data)
    
    # Attendre la réponse d'authentification
    print("Manager: En attente de la réponse d'authentification...")
    auth_received = False
    start_time = time.time()
    
    while time.time() - start_time < 5 and not auth_received:  # Timeout après 5 secondes
        message = manager.get_message()
        if message:
            print(f"Manager a reçu: {message}")
            if 'token' in message:
                manager.token = message['token']
                manager.client_id = message.get('id', 'unknown_id')
                auth_received = True
                print(f"Manager: Token reçu: {manager.token}")
        time.sleep(0.1)
    
    if not auth_received:
        print("Manager: Aucune réponse d'authentification reçue, on continue quand même")
    
    # Soumettre une tâche de test
    task = {
        'task_id': f"task_{int(time.time())}",
        'name': "Tâche de test",
        'command': "echo 'Hello World'",
        'required_resources': {"cpu_cores": 1, "ram_mb": 512}
    }
    
    print("Manager: Soumission d'une tâche...")
    manager.publish(TASKS_NEW_CHANNEL, task)
    return manager

def simulate_volunteer():
    """Simulate a volunteer client"""
    volunteer = TestClient()
    
    # S'abonner aux canaux pertinents
    volunteer.subscribe(AUTH_RESPONSE_CHANNEL)
    volunteer.subscribe(TASKS_ASSIGN_CHANNEL)
    volunteer.subscribe(TASKS_NEW_CHANNEL)
    
    # Enregistrer en tant que volunteer
    reg_data = {
        'name': 'test_volunteer',
        'location': 'Yaoundé',
        'resources': {
            'cpu_cores': 4,
            'ram_gb': 8,
            'gpu': 'NVIDIA RTX 3060'
        }
    }
    
    print("Volunteer: Envoi de l'enregistrement...")
    volunteer.publish(AUTH_REGISTER_CHANNEL, reg_data)
    
    # Attendre la réponse d'authentification
    print("Volunteer: En attente de la réponse d'authentification...")
    auth_received = False
    start_time = time.time()
    
    while time.time() - start_time < 5 and not auth_received:  # Timeout après 5 secondes
        message = volunteer.get_message()
        if message:
            print(f"Volunteer a reçu: {message}")
            if 'token' in message:
                volunteer.token = message['token']
                volunteer.client_id = message.get('id', 'unknown_id')
                auth_received = True
                print(f"Volunteer: Token reçu: {volunteer.token}")
        time.sleep(0.1)
    
    if not auth_received:
        print("Volunteer: Aucune réponse d'authentification reçue, on continue quand même")
    
    # Envoyer une mise à jour de statut
    status = {
        'id': volunteer.client_id,
        'status': 'available',
        'resources': {
            'cpu_usage': 10,
            'ram_usage': 2048,
            'gpu_usage': 0
        }
    }
    
    print("Volunteer: Envoi d'une mise à jour de statut...")
    volunteer.publish(VOLUNTEER_AVAILABLE_CHANNEL, status)
    return volunteer

def main():
    """Main test function"""
    print("Démarrage de la simulation de test...")
    
    # Démarrer le volunteer (écoute)
    volunteer = simulate_volunteer()
    
    # Attendre un peu pour que le volunteer soit prêt
    time.sleep(1)
    
    # Démarrer le manager (envoie des tâches)
    manager = simulate_manager()
    
    # Surveiller les messages pendant un moment
    print("\nSurveillance des messages pendant 30 secondes...")
    start_time = time.time()
    
    while time.time() - start_time < 30:
        # Vérifier les messages pour le volunteer
        message = volunteer.get_message()
        if message:
            print(f"Volunteer a reçu: {message}")
            
            # Si c'est une tâche, simuler son achèvement
            if message.get('task_id'):
                task_id = message.get('task_id')
                result = {
                    'task_id': task_id,
                    'status': 'completed',
                    'progress': 100,
                    'results': {"output": "Tâche terminée avec succès"},
                    'execution_time': 1.5,
                    'completed_at': datetime.utcnow().isoformat()
                }
                
                result_channel = f"{TASKS_RESULT_CHANNEL}/{task_id}"
                print(f"Volunteer: Envoi du résultat de la tâche sur {result_channel}...")
                volunteer.publish(result_channel, result)
        
        # Vérifier les messages pour le manager
        message = manager.get_message()
        if message:
            print(f"Manager a reçu: {message}")
        
        time.sleep(0.1)
    
    print("Simulation de test terminée!")

if __name__ == "__main__":
    main()
