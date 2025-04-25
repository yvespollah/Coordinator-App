import uuid
from mongoengine import Document, StringField, IntField, DateTimeField, DictField, ListField, BooleanField
from django.utils import timezone

class Volunteer(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(max_length=100, required=True)
    cpu_model = StringField(max_length=100, required=True)
    cpu_cores = IntField(required=True)
    total_ram = IntField(help_text="RAM in MB", required=True)
    available_storage = IntField(help_text="Storage in GB", required=True)
    operating_system = StringField(max_length=255, required=True)
    gpu_available = BooleanField(default=False)
    gpu_model = StringField(max_length=255, null=True)
    gpu_memory = IntField(help_text="GPU memory in MB", null=True)
    # ip_address = StringField(required=True)
    # communication_port = IntField(required=True)
    preferences = DictField(default=dict ,null=True)

    status = StringField(default='offline', choices=['offline', 'available', 'busy'])
    last_connected = DateTimeField(null=True)
    connection_history = ListField(DictField(), default=list)
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)


    
    meta = {
        'collection': 'volunteers'
    }

    def update_status(self, new_status):
        old_status = self.status
        self.status = new_status
        self.updated_at = timezone.now()

        if not isinstance(self.connection_history, list):
            self.connection_history = []

        self.connection_history.append({
            'timestamp': timezone.now().isoformat(),
            'from': old_status,
            'to': new_status
        })

        self.save()

    def register_connection(self):
        self.last_connected = timezone.now()
        self.update_status('available')

    def register_disconnection(self):
        self.update_status('offline')


