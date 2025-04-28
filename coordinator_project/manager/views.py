from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Manager, Workflow, Task
from .serializers import (
    ManagerSerializer,
    ManagerRegistrationSerializer,
    ManagerDetailSerializer,
    WorkflowSerializer,
    TaskSerializer
)

# ViewSet personnalisé pour MongoEngine
class ManagerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # Liste tous les managers
    def list(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)

    # Crée un nouveau manager
    def create(self, request):
        serializer = ManagerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            return Response(ManagerDetailSerializer(manager).data, status=201)
        return Response(serializer.errors, status=400)

    # Met à jour un manager existant
    def update(self, request, pk=None):
        try:
            manager = Manager.objects.get(id=pk)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        # Utilise le serializer classique pour la mise à jour
        serializer = ManagerSerializer(manager, data=request.data, partial=True)
        if serializer.is_valid():
            manager = serializer.save()
            return Response(ManagerDetailSerializer(manager).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Récupère le détail d'un manager (GET /manager/{id}/)
    def retrieve(self, request, pk=None):
        try:
            manager = Manager.objects.get(id=pk)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ManagerDetailSerializer(manager)
        return Response(serializer.data)

    # Supprime un manager (DELETE /manager/{id}/)
    def destroy(self, request, pk=None):
        try:
            manager = Manager.objects.get(id=pk)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        manager.delete()
        return Response({'success': 'Manager deleted'}, status=status.HTTP_204_NO_CONTENT)


# ViewSet pour le modèle Workflow (MongoEngine)
class WorkflowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # Liste tous les workflows
    def list(self, request):
        workflows = Workflow.objects.all()
        serializer = WorkflowSerializer(workflows, many=True)
        return Response(serializer.data)

    # Crée un nouveau workflow
    def create(self, request):
        serializer = WorkflowSerializer(data=request.data)
        if serializer.is_valid():
            workflow = serializer.save()
            return Response(WorkflowSerializer(workflow).data, status=201)
        return Response(serializer.errors, status=400)

    # Détail d'un workflow
    def retrieve(self, request, pk=None):
        try:
            workflow = Workflow.objects.get(id=pk)
        except Workflow.DoesNotExist:
            return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkflowSerializer(workflow)
        return Response(serializer.data)

    # Mise à jour d'un workflow
    def update(self, request, pk=None):
        try:
            workflow = Workflow.objects.get(id=pk)
        except Workflow.DoesNotExist:
            return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkflowSerializer(workflow, data=request.data, partial=True)
        if serializer.is_valid():
            workflow = serializer.save()
            return Response(WorkflowSerializer(workflow).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Suppression d'un workflow
    def destroy(self, request, pk=None):
        try:
            workflow = Workflow.objects.get(id=pk)
        except Workflow.DoesNotExist:
            return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)
        workflow.delete()
        return Response({'success': 'Workflow deleted'}, status=status.HTTP_204_NO_CONTENT)


# ViewSet pour le modèle Task (MongoEngine)
class TaskViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # Liste toutes les tâches
    def list(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    # Crée une nouvelle tâche
    def create(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=201)
        return Response(serializer.errors, status=400)

    # Détail d'une tâche
    def retrieve(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    # Mise à jour d'une tâche
    def update(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Suppression d'une tâche
    def destroy(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        task.delete()
        return Response({'success': 'Task deleted'}, status=status.HTTP_204_NO_CONTENT)