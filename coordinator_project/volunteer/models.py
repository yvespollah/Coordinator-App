import uuid
from mongoengine import (
    Document, StringField, IntField, DateTimeField, DictField, BooleanField, UUIDField
)
from django.utils import timezone

VOLUNTEER_STATUS_CHOICES = [
    ('available', 'Available'),
    ('busy', 'Busy'),
    ('offline', 'Offline'),
]

class Volunteer(Document):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = StringField(max_length=255, required=True)
    username = StringField(max_length=255, required=True, unique=True)
    password = StringField(max_length=255, required=True)  # Dans un système réel, il faudrait hasher ce mot de passe
    cpu_model = StringField(max_length=255, required=True)
    cpu_cores = IntField(required=True)
    total_ram = IntField(required=True, help_text="RAM in MB")
    available_storage = IntField(required=True, help_text="Storage in GB")
    operating_system = StringField(max_length=255, required=True)
    last_update = DateTimeField(default=timezone.now)
    current_status = StringField(max_length=20, choices=VOLUNTEER_STATUS_CHOICES, default='available')
    gpu_available = BooleanField(default=False)
    gpu_model = StringField(max_length=255, null=True)
    gpu_memory = IntField(null=True, help_text="GPU memory in MB")
    ip_address = StringField(required=True)
    communication_port = IntField(required=True)
    preferences = DictField(default=dict)
    performance = DictField(default=dict)
    last_activity = DateTimeField(null=True)
    machine_info = DictField(default=dict)  # Pour stocker les informations détaillées de la machine

    def __str__(self):
        return f"Machine {self.name} - {self.current_status}"

    meta = {
        'collection': 'volunteers'
    }
