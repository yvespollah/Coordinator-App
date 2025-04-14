from rest_framework import viewsets,permissions
from .models import Manager, Workflow, Task, Machine, Availability
from .serializers import (
    ManagerSerializer,
    WorkflowSerializer,
    TaskSerializer,
    MachineSerializer,
    AvailabilitySerializer
)

# Manager ViewSet
class ManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer


# Workflow ViewSet
class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer


# Task ViewSet
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


# Machine ViewSet
class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


# Availability ViewSet
class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
