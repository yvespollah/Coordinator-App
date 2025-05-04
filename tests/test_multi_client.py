import sys
import os
import json
import time
import redis
from datetime import datetime
from threading import Thread

# Add project root to Python path
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

class TestClient:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.token = None
        self.client_id = None
        self.channels = []
        self.running = True
        
    def subscribe(self, channel):
        """Subscribe to a channel"""
        self.pubsub.subscribe(channel)
        
    def publish(self, channel, message):
        """Publish a message to a channel"""
        if isinstance(message, (ManagerRegistrationMessage, VolunteerRegistrationMessage,
                              AuthResponseMessage, TaskMessage, ResultMessage,
                              VolunteerStatusMessage)):
            message = json.dumps(message.to_dict())
        self.redis.publish(channel, message)
        
    def get_message(self):
        """Get a message from subscribed channels"""
        message = self.pubsub.get_message()
        if message and message['type'] == 'message':
            return json.loads(message['data'])
        return None

class Manager(TestClient):
    def __init__(self, username, email, redis_host='localhost', redis_port=6379):
        super().__init__(redis_host, redis_port)
        self.username = username
        self.email = email
        
    def register(self):
        """Register with the coordinator"""
        self.subscribe(AUTH_CHANNEL)
        
        reg_msg = ManagerRegistrationMessage(
            username=self.username,
            email=self.email,
            password="test123"
        )
        print(f"Manager {self.username}: Sending registration...")
        self.publish(REGISTRATION_CHANNEL, reg_msg)
        
        # Wait for auth response
        while self.running:
            message = self.get_message()
            if message and message.get('message_type') == 'auth_response':
                self.token = message['token']
                self.client_id = message['client_id']
                self.channels = message['channels']
                print(f"Manager {self.username}: Registered with ID {self.client_id}")
                break
            time.sleep(0.1)
    
    def submit_task(self, task_id, name, command):
        """Submit a task"""
        task = TaskMessage(
            task_id=task_id,
            workflow_id=f"workflow_{task_id}",
            name=name,
            command=command,
            token=self.token,
            required_resources={"cpu_cores": 1, "ram_mb": 512}
        )
        print(f"Manager {self.username}: Submitting task {task_id}")
        self.publish(MANAGER_TASKS_CHANNEL, task)

class Volunteer(TestClient):
    def __init__(self, name, cpu_cores, total_ram, gpu_available=False,
                 redis_host='localhost', redis_port=6379):
        super().__init__(redis_host, redis_port)
        self.name = name
        self.cpu_cores = cpu_cores
        self.total_ram = total_ram
        self.gpu_available = gpu_available
        
    def register(self):
        """Register with the coordinator"""
        self.subscribe(AUTH_CHANNEL)
        
        reg_msg = VolunteerRegistrationMessage(
            name=self.name,
            cpu_model="Intel i7",
            cpu_cores=self.cpu_cores,
            total_ram=self.total_ram,
            available_storage=500,
            operating_system="Linux",
            gpu_available=self.gpu_available,
            gpu_model="NVIDIA RTX 3060" if self.gpu_available else None,
            gpu_memory=6144 if self.gpu_available else None,
            ip_address="127.0.0.1",
            communication_port=5000
        )
        print(f"Volunteer {self.name}: Sending registration...")
        self.publish(REGISTRATION_CHANNEL, reg_msg)
        
        # Wait for auth response
        while self.running:
            message = self.get_message()
            if message and message.get('message_type') == 'auth_response':
                self.token = message['token']
                self.client_id = message['client_id']
                self.channels = message['channels']
                print(f"Volunteer {self.name}: Registered with ID {self.client_id}")
                break
            time.sleep(0.1)
        
        # Subscribe to task channel
        self.subscribe(VOLUNTEER_TASKS_CHANNEL)
    
    def run(self):
        """Main loop to process tasks"""
        while self.running:
            message = self.get_message()
            if message and message.get('message_type') == 'task':
                task_id = message['task_id']
                print(f"Volunteer {self.name}: Received task {task_id}")
                
                # Simulate working on task
                time.sleep(2)
                
                # Send result
                result = ResultMessage(
                    task_id=task_id,
                    workflow_id=message['workflow_id'],
                    volunteer_id=self.client_id,
                    token=self.token,
                    status="COMPLETED",
                    progress=100,
                    results={"output": f"Task {task_id} completed by {self.name}"},
                    execution_time=2.0
                )
                print(f"Volunteer {self.name}: Completed task {task_id}")
                self.publish(VOLUNTEER_RESULTS_CHANNEL, result)
                
                # Update status
                status = VolunteerStatusMessage(
                    volunteer_id=self.client_id,
                    token=self.token,
                    current_status="AVAILABLE",
                    resources={
                        "cpu_usage": 10,
                        "ram_usage": self.total_ram // 4,
                        "gpu_usage": 0
                    },
                    performance={
                        "tasks_completed": 1,
                        "avg_execution_time": 2.0
                    }
                )
                self.publish(VOLUNTEER_STATUS_CHANNEL, status)
            
            time.sleep(0.1)

def run_manager(username, email):
    """Run a manager instance"""
    manager = Manager(username, email)
    manager.register()
    
    # Submit some tasks
    for i in range(3):
        task_id = f"{username}_task_{i}"
        manager.submit_task(task_id, f"Test Task {i}", f"echo 'Task {i}'")
        time.sleep(1)
    
    time.sleep(10)  # Wait for results
    manager.running = False

def run_volunteer(name, cpu_cores, total_ram, gpu_available=False):
    """Run a volunteer instance"""
    volunteer = Volunteer(name, cpu_cores, total_ram, gpu_available)
    volunteer.register()
    volunteer.run()

def main():
    """Run multiple managers and volunteers"""
    print("Starting multi-client test...")
    
    # Create manager threads
    manager_threads = [
        Thread(target=run_manager, args=(f"manager_{i}", f"manager_{i}@test.com"))
        for i in range(2)
    ]
    
    # Create volunteer threads
    volunteer_threads = [
        Thread(target=run_volunteer, args=(f"volunteer_{i}", 4, 8192, i % 2 == 0))
        for i in range(3)
    ]
    
    # Start all threads
    for thread in manager_threads + volunteer_threads:
        thread.start()
    
    # Wait for managers to finish
    for thread in manager_threads:
        thread.join()
    
    # Stop volunteers
    print("\nStopping volunteers...")
    for volunteer in volunteer_threads:
        volunteer._target.__self__.running = False
    
    for thread in volunteer_threads:
        thread.join()
    
    print("Test completed!")

if __name__ == "__main__":
    main()
