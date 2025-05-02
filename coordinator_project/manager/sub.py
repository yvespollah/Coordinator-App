import redis
import json
from .models import Manager
from datetime import datetime
from mongoengine import connect

# Ensure connection to the administration database (if different from default)
connect(
    db='coordinator_db',  # Change this if you want a different db
    host='localhost',
    port=27017,

)

def subscribe_to_manager_channel():
    r = redis.Redis(host='localhost', port=6379, db=0) # Connect to Redis server (broker ip)
    pubsub = r.pubsub() # Create a pubsub object
    pubsub.subscribe('manager_channel') # Subscribe to manager channel (manager_channel:topic)
    print('Subscribed to manager_channel, waiting for messages...')
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            manager = Manager(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                registration_date=data['registration_date'],
                last_login=data['last_login'],
                status=data['status']
            )
            manager.save()
            print(f"Stored manager: {manager}")
