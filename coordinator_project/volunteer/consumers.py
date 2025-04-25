import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Volunteer

class VolunteerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        token = self.scope['query_string'].decode().split('token=')[-1]

        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            volunteer_id = payload.get("id")
            self.volunteer = await database_sync_to_async(Volunteer.objects(id=volunteer_id).first)()

            if not self.volunteer:
                await self.close()
                return

            # Set group names
            self.volunteer_group_name = f'volunteer_{self.volunteer.id}'

            # Accept connection
            await self.accept()

            # Join personal group
            await self.channel_layer.group_add(
                self.volunteer_group_name,
                self.channel_name
            )

            # Join available group if status is available
            if self.volunteer.status == "available":
                await self.channel_layer.group_add(
                    "available_volunteers",
                    self.channel_name
                )

            await self.send(text_data=json.dumps({
                "message": f"Connected as {self.volunteer.name}"
            }))

        except jwt_exceptions.InvalidTokenError:
            await self.close()

    

    
    # async def connect(self):
        # Set volunteer_id for later use
        self.volunteer_id = "some_unique_id_or_from_token"

        # Set group name
        self.volunteer_group_name = f'volunteer_{self.volunteer_id}'
        await self.channel_layer.group_add(self.volunteer_group_name, self.channel_name)
        await self.channel_layer.group_add("available_volunteers", self.channel_name)

        await self.accept()
        #await self.update_volunteer_status('available')

    async def disconnect(self):
        # Leave both groups
        await self.channel_layer.group_discard(
            self.volunteer_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            "available_volunteers",
            self.channel_name
        )
        await self.update_volunteer_status('offline')

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'heartbeat':
            await self.update_volunteer_last_connection()
            await self.send(text_data=json.dumps({
                'type': 'heartbeat_response',
                'status': 'received'
            }))

        elif message_type == 'status_update':
            status = data.get('status')
            if status in ['available', 'busy', 'offline']:
                await self.update_volunteer_status(status)
                await self.send(text_data=json.dumps({
                    'type': 'status_updated',
                    'status': status
                }))

        elif message_type == 'tech_specs_update':
            tech_specs = data.get('tech_specs', {})
            await self.update_volunteer_tech_specs(tech_specs)
            await self.send(text_data=json.dumps({
                'type': 'tech_specs_updated'
            }))

        elif message_type == 'preferences_update':
            preferences = data.get('preferences', {})
            await self.update_volunteer_preferences(preferences)
            await self.send(text_data=json.dumps({
                'type': 'preferences_updated'
            }))

    # Personal task assignment
    async def task_assignment(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_assignment',
            'task_id': event['task_id'],
            'task_data': event['task_data']
        }))
        await self.update_volunteer_status('busy')

    # Group-wide announcement
    async def system_announcement(self, event):
        await self.send(text_data=json.dumps({
            'type': 'announcement',
            'message': event['message']
        }))

    # DB methods
    @database_sync_to_async
    def update_volunteer_status(self, status):
        try:
            volunteer = Volunteer.objects.get(id=self.volunteer_id)
            volunteer.update_status(status)
            return True
        except Volunteer.DoesNotExist:
            return False

    @database_sync_to_async
    def update_volunteer_last_connection(self):
        try:
            volunteer = Volunteer.objects.get(id=self.volunteer_id)
            volunteer.last_connected = timezone.now()
            volunteer.save()
            return True
        except Volunteer.DoesNotExist:
            return False

    @database_sync_to_async
    def update_volunteer_tech_specs(self, tech_specs):
        try:
            volunteer = Volunteer.objects.get(id=self.volunteer_id)
            if not isinstance(volunteer.tech_specs, dict):
                volunteer.tech_specs = {}
            volunteer.tech_specs.update(tech_specs)
            volunteer.save()
            return True
        except Volunteer.DoesNotExist:
            return False

    @database_sync_to_async
    def update_volunteer_preferences(self, preferences):
        try:
            volunteer = Volunteer.objects.get(id=self.volunteer_id)
            if not isinstance(volunteer.preferences, dict):
                volunteer.preferences = {}
            volunteer.preferences.update(preferences)
            volunteer.save()
            return True
        except Volunteer.DoesNotExist:
            return False
    
        
"""     async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle incoming data from the volunteer
        await self.send(text_data=json.dumps({"message": "Data received", "data": data})) """