from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, List
import uuid

class Message(ABC):
    """Base message class for all pub/sub communications"""
    def __init__(self, message_type: str):
        self.message_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        self.message_type = message_type
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type
        }

@dataclass
class ManagerRegistrationMessage(Message):
    """Registration message for workflow managers"""
    username: str
    email: str
    password: str
    status: str  # 'active', 'inactive', or 'suspended'
    
    def __init__(self, username: str, email: str, password: str, status: str = 'inactive'):
        super().__init__("manager_registration")
        self.username = username
        self.email = email
        self.password = password
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "status": self.status
        })
        return data

@dataclass
class VolunteerRegistrationMessage(Message):
    """Registration message for volunteer nodes"""
    name: str
    cpu_model: str
    cpu_cores: int
    total_ram: int  # RAM in MB
    available_storage: int  # Storage in GB
    operating_system: str
    gpu_available: bool
    gpu_model: Optional[str]
    gpu_memory: Optional[int]  # GPU memory in MB
    ip_address: str
    communication_port: int
    
    def __init__(self, name: str, cpu_model: str, cpu_cores: int,
                 total_ram: int, available_storage: int, operating_system: str,
                 gpu_available: bool, ip_address: str, communication_port: int,
                 gpu_model: Optional[str] = None, gpu_memory: Optional[int] = None):
        super().__init__("volunteer_registration")
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
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "cpu_model": self.cpu_model,
            "cpu_cores": self.cpu_cores,
            "total_ram": self.total_ram,
            "available_storage": self.available_storage,
            "operating_system": self.operating_system,
            "gpu_available": self.gpu_available,
            "gpu_model": self.gpu_model,
            "gpu_memory": self.gpu_memory,
            "ip_address": self.ip_address,
            "communication_port": self.communication_port
        })
        return data

@dataclass
class AuthResponseMessage(Message):
    """Authentication response with token and channel access"""
    client_id: str
    client_type: str  # 'manager' or 'volunteer'
    token: str
    status: str
    channels: List[str]  # List of channels the client has access to
    
    def __init__(self, client_id: str, client_type: str, token: str, 
                 status: str, channels: List[str]):
        super().__init__("auth_response")
        self.client_id = client_id
        self.client_type = client_type
        self.token = token
        self.status = status
        self.channels = channels
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "client_id": self.client_id,
            "client_type": self.client_type,
            "token": self.token,
            "status": self.status,
            "channels": self.channels
        })
        return data

@dataclass
class TaskMessage(Message):
    """Task related messages (submission, assignment, status)"""
    task_id: str
    workflow_id: str
    name: str
    command: str
    token: str  # Authentication token
    status: str = "PENDING"
    required_resources: Dict[str, Any] = None
    docker_image: Optional[str] = None
    dependencies: List[str] = None
    is_subtask: bool = False
    
    def __init__(self, task_id: str, workflow_id: str, name: str, command: str,
                 token: str, status: str = "PENDING", 
                 required_resources: Dict[str, Any] = None,
                 docker_image: Optional[str] = None, dependencies: List[str] = None,
                 is_subtask: bool = False):
        super().__init__("task")
        self.task_id = task_id
        self.workflow_id = workflow_id
        self.name = name
        self.command = command
        self.token = token
        self.status = status
        self.required_resources = required_resources or {}
        self.docker_image = docker_image
        self.dependencies = dependencies or []
        self.is_subtask = is_subtask
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "task_id": self.task_id,
            "workflow_id": self.workflow_id,
            "name": self.name,
            "command": self.command,
            "token": self.token,
            "status": self.status,
            "required_resources": self.required_resources,
            "docker_image": self.docker_image,
            "dependencies": self.dependencies,
            "is_subtask": self.is_subtask
        })
        return data

@dataclass
class VolunteerStatusMessage(Message):
    """Volunteer status and resource updates"""
    volunteer_id: str
    token: str  # Authentication token
    current_status: str  # from VOLUNTEER_STATUS_CHOICES
    resources: Dict[str, Any]  # Current resource usage
    performance: Dict[str, Any]  # Performance metrics
    
    def __init__(self, volunteer_id: str, token: str, current_status: str,
                 resources: Dict[str, Any], performance: Dict[str, Any]):
        super().__init__("volunteer_status")
        self.volunteer_id = volunteer_id
        self.token = token
        self.current_status = current_status
        self.resources = resources
        self.performance = performance
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "volunteer_id": self.volunteer_id,
            "token": self.token,
            "current_status": self.current_status,
            "resources": self.resources,
            "performance": self.performance
        })
        return data

@dataclass
class ResultMessage(Message):
    """Task result messages"""
    task_id: str
    workflow_id: str
    volunteer_id: str
    token: str  # Authentication token
    status: str
    progress: float
    results: Dict[str, Any]
    error_details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    
    def __init__(self, task_id: str, workflow_id: str, volunteer_id: str,
                 token: str, status: str, progress: float, results: Dict[str, Any],
                 error_details: Optional[Dict[str, Any]] = None,
                 execution_time: Optional[float] = None):
        super().__init__("result")
        self.task_id = task_id
        self.workflow_id = workflow_id
        self.volunteer_id = volunteer_id
        self.token = token
        self.status = status
        self.progress = progress
        self.results = results
        self.error_details = error_details
        self.execution_time = execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "task_id": self.task_id,
            "workflow_id": self.workflow_id,
            "volunteer_id": self.volunteer_id,
            "token": self.token,
            "status": self.status,
            "progress": self.progress,
            "results": self.results,
            "error_details": self.error_details,
            "execution_time": self.execution_time
        })
        return data

@dataclass
class HeartbeatMessage(Message):
    """System heartbeat messages"""
    client_id: str
    token: str  # Authentication token
    client_type: str  # 'manager' or 'volunteer'
    status: str
    metrics: Dict[str, Any]
    
    def __init__(self, client_id: str, token: str, client_type: str, 
                 status: str, metrics: Dict[str, Any]):
        super().__init__("heartbeat")
        self.client_id = client_id
        self.token = token
        self.client_type = client_type
        self.status = status
        self.metrics = metrics
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "client_id": self.client_id,
            "token": self.token,
            "client_type": self.client_type,
            "status": self.status,
            "metrics": self.metrics
        })
        return data
