from django.db import models
from django.utils import timezone
import uuid


# Status enum
class Status(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'

# Manager model
class Manager(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    def __str__(self):
        return f"{self.username} - {self.email} ({self.status})"
    
class WorkflowType(models.TextChoices):
    DATA_PROCESSING = 'DATA_PROCESSING', 'Traitement de données'
    SCIENTIFIC_COMPUTING = 'SCIENTIFIC_COMPUTING', 'Calcul scientifique'
    RENDERING = 'RENDERING', 'Rendu graphique'
    MACHINE_LEARNING = 'MACHINE_LEARNING', 'Apprentissage automatique'

class WorkflowStatus(models.TextChoices):
    CREATED = 'CREATED', 'Créé'
    VALIDATED = 'VALIDATED', 'Validé'
    SUBMITTED = 'SUBMITTED', 'Soumis'
    SPLITTING = 'SPLITTING', 'En découpage'
    ASSIGNING = 'ASSIGNING', 'En attribution'
    PENDING = 'PENDING', 'En attente'
    RUNNING = 'RUNNING', 'En exécution'
    PAUSED = 'PAUSED', 'En pause'
    PARTIAL_FAILURE = 'PARTIAL_FAILURE', 'Échec partiel'
    REASSIGNING = 'REASSIGNING', 'Réattribution'
    AGGREGATING = 'AGGREGATING', 'Agrégation'
    COMPLETED = 'COMPLETED', 'Terminé'
    FAILED = 'FAILED', 'Échoué'

class TaskStatus(models.TextChoices):
    PENDING = 'PENDING', 'En attente'
    ASSIGNED = 'ASSIGNED', 'Assigné'
    RUNNING = 'RUNNING', 'En exécution'
    COMPLETED = 'COMPLETED', 'Terminé'
    FAILED = 'FAILED', 'Échoué'

class Workflow(models.Model):
    """
    Modèle principal pour les workflows de calcul distribué.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(
        max_length=30, 
        choices=WorkflowType.choices,
        default=WorkflowType.DATA_PROCESSING
    )
    owner = models.ForeignKey(Manager, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=WorkflowStatus.choices, 
        default=WorkflowStatus.CREATED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=1)
    
    # Champs pour stocker des informations structurées sous forme JSON
    estimated_resources = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'

class Task(models.Model):
    """
    Modèle pour les tâches individuelles dans un workflow.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    command = models.CharField(max_length=500)
    parameters = models.JSONField(default=list)
    dependencies = models.JSONField(default=list)
    status = models.CharField(
        max_length=20, 
        choices=TaskStatus.choices, 
        default=TaskStatus.PENDING
    )
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks')
    is_subtask = models.BooleanField(default=False)
    progress = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    required_resources = models.JSONField(default=dict)
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    attempts = models.IntegerField(default=0)
    results = models.JSONField(default=dict, blank=True, null=True)
    error_details = models.JSONField(default=dict, blank=True, null=True)
    docker_image = models.CharField(max_length=255, blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.workflow.name})"
    
    class Meta:
        ordering = ['-is_subtask', 'created_at']
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'




class Machine(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  
    cpu_model = models.CharField(max_length=255) 
    cpu_cores = models.IntegerField() 
    total_ram = models.IntegerField(help_text="RAM in MB")
    available_storage = models.IntegerField(help_text="Storage in GB") 
    operating_system = models.CharField(max_length=255) 
    last_update = models.DateTimeField(auto_now=True) 
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available') 
    gpu_available = models.BooleanField(default=False)
    gpu_model = models.CharField(max_length=255, blank=True, null=True) 
    gpu_memory = models.IntegerField(help_text="GPU memory in MB", blank=True, null=True) 
    ip_address = models.GenericIPAddressField()  
    communication_port = models.IntegerField() 

    def __str__(self):
        return f"Machine {self.name} - {self.current_status}"

class Availability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('disconnected', 'Disconnected'),
        ('idle', 'Idle'),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='availabilities')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    last_update = models.DateTimeField(auto_now=True)
    running_tasks_count = models.PositiveIntegerField(default=0)
    cpu_limit = models.DecimalField(max_digits=5, decimal_places=2, help_text="CPU limit percentage, e.g., 75.00")
    ram_limit = models.PositiveIntegerField(help_text="RAM limit in MB")
    available_time_slots = models.CharField(max_length=255, help_text="e.g., 08:00-12:00, 14:00-18:00")

    def __str__(self):
        return f"Availability of {self.machine.hostname} - {self.status}"