from mongoengine import Document, StringField, DateTimeField, UUIDField, BooleanField, FloatField, DictField, ListField, IntField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField
import uuid
from datetime import datetime

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