from mongoengine import Document, StringField, DateTimeField, UUIDField, BooleanField, FloatField, DictField, ListField, IntField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField
import uuid
from datetime import datetime
from mongoengine import CASCADE, NULLIFY

# Status constants
STATUS_ACTIVE = 'active'
STATUS_INACTIVE = 'inactive'
STATUS_SUSPENDED = 'suspended'

class Manager(Document):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    username = StringField(max_length=150, unique=True, required=True)
    email = StringField(unique=True, required=True)
    password = StringField(max_length=256, required=True)
    registration_date = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField(default=datetime.utcnow)
    status = StringField(choices=[STATUS_ACTIVE, STATUS_INACTIVE, STATUS_SUSPENDED], default=STATUS_INACTIVE)

    def __str__(self):
        return f"{self.username} - {self.email} ({self.status})"

# --- Enums sous forme de constantes (MongoEngine ne gère pas TextChoices) ---
WORKFLOW_TYPE_CHOICES = (
    ('DATA_PROCESSING', 'Traitement de données'),
    ('SCIENTIFIC_COMPUTING', 'Calcul scientifique'),
    ('RENDERING', 'Rendu graphique'),
    ('MACHINE_LEARNING', 'Apprentissage automatique'),
)

WORKFLOW_STATUS_CHOICES = (
    ('CREATED', 'Créé'),
    ('VALIDATED', 'Validé'),
    ('SUBMITTED', 'Soumis'),
    ('SPLITTING', 'En découpage'),
    ('ASSIGNING', 'En attribution'),
    ('PENDING', 'En attente'),
    ('RUNNING', 'En exécution'),
    ('PAUSED', 'En pause'),
    ('PARTIAL_FAILURE', 'Échec partiel'),
    ('REASSIGNING', 'Réattribution'),
    ('AGGREGATING', 'Agrégation'),
    ('COMPLETED', 'Terminé'),
    ('FAILED', 'Échoué'),
)

TASK_STATUS_CHOICES = (
    ('PENDING', 'En attente'),
    ('ASSIGNED', 'Assigné'),
    ('RUNNING', 'En exécution'),
    ('COMPLETED', 'Terminé'),
    ('FAILED', 'Échoué'),
)

class Workflow(Document):
    """
    Modèle principal pour les workflows de calcul distribué (MongoEngine).
    """
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = StringField(max_length=255, required=True)
    description = StringField()
    workflow_type = StringField(
        max_length=30,
        choices=WORKFLOW_TYPE_CHOICES,
        default='DATA_PROCESSING'
    )
    owner = ReferenceField('Manager', reverse_delete_rule=CASCADE, required=True)
    status = StringField(
        max_length=20,
        choices=WORKFLOW_STATUS_CHOICES,
        default='CREATED'
    )
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    priority = IntField(default=1)

    estimated_resources = DictField(default=dict)
    tags = ListField(StringField(), default=list)
    metadata = DictField(default=dict)

    def __str__(self):
        return self.name

    meta = {
        'ordering': ['-created_at'],
        'verbose_name': 'Workflow',
        'verbose_name_plural': 'Workflows',
    }

class Task(Document):
    """
    Modèle pour les tâches individuelles dans un workflow (MongoEngine).
    """
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    workflow = ReferenceField('Workflow', reverse_delete_rule=CASCADE, required=True, db_field='workflow_id')
    name = StringField(max_length=255, required=True)
    description = StringField()
    command = StringField(max_length=500)
    dependencies = ListField(StringField(), default=list)
    status = StringField(max_length=20, choices=TASK_STATUS_CHOICES, default='PENDING')
    is_subtask = BooleanField(default=False)
    progress = FloatField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    required_resources = DictField(default=dict)
    assigned_to = ReferenceField('volunteer.Volunteer', reverse_delete_rule=NULLIFY, null=True)
    attempts = IntField(default=0)
    results = DictField(default=dict, null=True)
    error_details = DictField(default=dict, null=True)
    docker_image = StringField(max_length=255, null=True)

    def __str__(self):
        return f"{self.name} ({self.workflow.name})"

    meta = {
        'ordering': ['-is_subtask', 'created_at'],
        'verbose_name': 'Tâche',
        'verbose_name_plural': 'Tâches',
    }