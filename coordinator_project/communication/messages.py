"""
Définition des formats de messages pour la communication Redis.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
import json

class BaseMessage:
    """Message de base pour la communication Redis."""
    
    def __init__(self):
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        return {
            'request_id': self.request_id,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class ManagerRegistrationMessage(BaseMessage):
    """Message d'enregistrement d'un manager."""
    
    def __init__(self, username: str, email: str, password: str, 
                 client_ip: Optional[str] = None, 
                 client_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.username = username
        self.email = email
        self.password = password
        self.client_ip = client_ip
        self.client_info = client_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'client_ip': self.client_ip,
            'client_info': self.client_info
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class ManagerRegistrationResponseMessage(BaseMessage):
    """Réponse à un message d'enregistrement d'un manager."""
    
    def __init__(self, status: str, message: str,
                manager_id: Optional[str] = None, 
                username: Optional[str] = None,
                email: Optional[str] = None,
                request_id: Optional[str] = None):
        super().__init__()
        # Si request_id est fourni, on l'utilise au lieu de générer un nouveau
        if request_id:
            self.request_id = request_id
        self.status = status
        self.message = message
        self.manager_id = manager_id
        self.username = username
        self.email = email
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'status': self.status,
            'message': self.message,
            'manager_id': self.manager_id,
            'username': self.username,
            'email': self.email
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class ManagerLoginMessage(BaseMessage):
    """Message de connexion d'un manager."""
    
    def __init__(self, username: str, password: str,
                client_ip: Optional[str] = None,
                client_info: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.username = username
        self.password = password
        self.client_ip = client_ip
        self.client_info = client_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'username': self.username,
            'password': self.password,
            'client_ip': self.client_ip,
            'client_info': self.client_info
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class ManagerLoginResponseMessage(BaseMessage):
    """Réponse à un message de connexion d'un manager."""
    
    def __init__(self, status: str, message: str,
                token: Optional[str] = None,
                refresh_token: Optional[str] = None,
                manager_id: Optional[str] = None,
                username: Optional[str] = None,
                email: Optional[str] = None,
                role: str = 'manager',
                request_id: Optional[str] = None):
        super().__init__()
        # Si request_id est fourni, on l'utilise au lieu de générer un nouveau
        if request_id:
            self.request_id = request_id
        self.status = status
        self.message = message
        self.token = token
        self.refresh_token = refresh_token
        self.manager_id = manager_id
        self.username = username
        self.email = email
        self.role = role
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'status': self.status,
            'message': self.message,
            'token': self.token,
            'refresh_token': self.refresh_token,
            'manager_id': self.manager_id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class VolunteerRegistrationMessage(BaseMessage):
    """Message d'enregistrement d'un volunteer."""
    
    def __init__(self, name: str, cpu_model: str, cpu_cores: int,
                total_ram: int, available_storage: int, operating_system: str,
                gpu_available: bool = False, gpu_model: Optional[str] = None,
                gpu_memory: Optional[int] = None, ip_address: str = '0.0.0.0',
                communication_port: int = 8000, preferences: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.name = name
        self.cpu_model = cpu_model
        self.cpu_cores = cpu_cores
        self.total_ram = total_ram
        self.available_storage = available_storage
        self.operating_system = operating_system
        self.gpu_available = gpu_available
        self.gpu_model = gpu_model
        self.gpu_memory = gpu_memory
        self.ip_address = ip_address
        self.communication_port = communication_port
        self.preferences = preferences or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'cpu_model': self.cpu_model,
            'cpu_cores': self.cpu_cores,
            'total_ram': self.total_ram,
            'available_storage': self.available_storage,
            'operating_system': self.operating_system,
            'gpu_available': self.gpu_available,
            'gpu_model': self.gpu_model,
            'gpu_memory': self.gpu_memory,
            'ip_address': self.ip_address,
            'communication_port': self.communication_port,
            'preferences': self.preferences
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class VolunteerRegistrationResponseMessage(BaseMessage):
    """Réponse à un message d'enregistrement d'un volunteer."""
    
    def __init__(self, status: str, message: str,
                volunteer_id: Optional[str] = None, 
                name: Optional[str] = None,
                request_id: Optional[str] = None):
        super().__init__()
        # Si request_id est fourni, on l'utilise au lieu de générer un nouveau
        if request_id:
            self.request_id = request_id
        self.status = status
        self.message = message
        self.volunteer_id = volunteer_id
        self.name = name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'status': self.status,
            'message': self.message,
            'volunteer_id': self.volunteer_id,
            'name': self.name
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class VolunteerLoginMessage(BaseMessage):
    """Message de connexion d'un volunteer."""
    
    def __init__(self, volunteer_id: str, name: str, client_ip: Optional[str] = None):
        super().__init__()
        self.volunteer_id = volunteer_id
        self.name = name
        self.client_ip = client_ip
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'volunteer_id': self.volunteer_id,
            'name': self.name,
            'client_ip': self.client_ip
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class VolunteerLoginResponseMessage(BaseMessage):
    """Réponse à un message de connexion d'un volunteer."""
    
    def __init__(self, status: str, message: str,
                token: Optional[str] = None, refresh_token: Optional[str] = None,
                volunteer_id: Optional[str] = None, name: Optional[str] = None,
                role: str = 'volunteer',
                request_id: Optional[str] = None):
        super().__init__()
        # Si request_id est fourni, on l'utilise au lieu de générer un nouveau
        if request_id:
            self.request_id = request_id
        self.status = status
        self.message = message
        self.token = token
        self.refresh_token = refresh_token
        self.volunteer_id = volunteer_id
        self.name = name
        self.role = role
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'status': self.status,
            'message': self.message,
            'token': self.token,
            'refresh_token': self.refresh_token,
            'volunteer_id': self.volunteer_id,
            'name': self.name,
            'role': self.role
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class TaskMessage(BaseMessage):
    """Message de tâche."""
    
    def __init__(self, workflow_id: str, task_id: str, name: str, command: str,
                required_resources: Optional[Dict[str, Any]] = None,
                dependencies: Optional[List[str]] = None,
                token: Optional[str] = None):
        super().__init__()
        self.workflow_id = workflow_id
        self.task_id = task_id
        self.name = name
        self.command = command
        self.required_resources = required_resources or {}
        self.dependencies = dependencies or []
        self.token = token  # Token JWT pour l'authentification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'workflow_id': self.workflow_id,
            'task_id': self.task_id,
            'name': self.name,
            'command': self.command,
            'required_resources': self.required_resources,
            'dependencies': self.dependencies,
            'token': self.token
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class TaskStatusMessage(BaseMessage):
    """Message de statut de tâche."""
    
    def __init__(self, workflow_id: str, task_id: str, status: str,
                progress: float = 0.0, message: Optional[str] = None,
                token: Optional[str] = None):
        super().__init__()
        self.workflow_id = workflow_id
        self.task_id = task_id
        self.status = status
        self.progress = progress
        self.message = message
        self.token = token  # Token JWT pour l'authentification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'workflow_id': self.workflow_id,
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'token': self.token
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())


class TaskResultMessage(BaseMessage):
    """Message de résultat de tâche."""
    
    def __init__(self, workflow_id: str, task_id: str, status: str,
                results: Optional[Dict[str, Any]] = None,
                error_details: Optional[Dict[str, Any]] = None,
                execution_time: float = 0.0, token: Optional[str] = None):
        super().__init__()
        self.workflow_id = workflow_id
        self.task_id = task_id
        self.status = status  # 'success' ou 'error'
        self.results = results or {}
        self.error_details = error_details
        self.execution_time = execution_time
        self.token = token  # Token JWT pour l'authentification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire."""
        base_dict = super().to_dict()
        base_dict.update({
            'workflow_id': self.workflow_id,
            'task_id': self.task_id,
            'status': self.status,
            'results': self.results,
            'error_details': self.error_details,
            'execution_time': self.execution_time,
            'token': self.token
        })
        return base_dict
    
    def to_json(self) -> str:
        """Convertit le message en JSON."""
        return json.dumps(self.to_dict())
