from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as drf_status
from mongoengine.connection import get_db
from volunteer.models import Volunteer
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
            # Enregistrer dans MongoDB
            manager = serializer.save()
            
            # Publier sur Redis pour informer les volunteers
            message_data = {
                'username': manager.username,
                'email': manager.email,
                'status': manager.status,
                'id': str(manager.id)
            }
            
            # Publier sur le canal d'enregistrement
            message_broker.publish('auth/register', message_data)
            
            return Response(ManagerDetailSerializer(manager).data, status=201)
        return Response(serializer.errors, status=400)

    # Met à jour un manager existant
    def update(self, request, pk=None):
        try:
            manager = Manager.objects.get(id=pk)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        # Utilise ManagerSerializer pour la mise à jour (inclut status)
        serializer = ManagerSerializer(manager, data=request.data, partial=True)
        if serializer.is_valid():
            manager = serializer.save()
            
            # Si le statut a changé, publier sur Redis
            if 'status' in request.data:
                message_broker.publish('manager/status', {
                    'id': str(manager.id),
                    'username': manager.username,
                    'status': manager.status
                })
                
            return Response(ManagerSerializer(manager).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Met à jour partielle (PATCH)
    def partial_update(self, request, pk=None):
        return self.update(request, pk)

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
            
            # Publier la déconnexion sur Redis
            message_broker.publish('manager/disconnect', {
                'id': str(manager.id),
                'username': manager.username
            })
            
            # Supprimer de MongoDB
            manager.delete()
            
            return Response({'success': 'Manager deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)


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
            
            # Publier sur Redis pour informer les volunteers
            message_broker.publish('tasks/new', {
                'workflow_id': str(workflow.id),
                'name': workflow.name,
                'type': workflow.workflow_type,
                'owner': str(workflow.owner.id),
                'priority': workflow.priority
            })
            
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
            
            # Si le statut a changé, publier sur Redis
            if 'status' in request.data:
                message_broker.publish('tasks/status', {
                    'workflow_id': str(workflow.id),
                    'name': workflow.name,
                    'status': workflow.status
                })
                
            return Response(WorkflowSerializer(workflow).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Suppression d'un workflow
    def destroy(self, request, pk=None):
        try:
            workflow = Workflow.objects.get(id=pk)
            
            # Publier la suppression sur Redis
            message_broker.publish('tasks/delete', {
                'workflow_id': str(workflow.id),
                'name': workflow.name
            })
            
            workflow.delete()
            return Response({'success': 'Workflow deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Workflow.DoesNotExist:
            return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)


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
            
            # Publier sur Redis pour informer les volunteers
            message_broker.publish('tasks/assign', {
                'task_id': str(task.id),
                'name': task.name,
                'workflow_id': str(task.workflow.id),
                'required_resources': task.required_resources
            })
            
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
            
            # Si le statut a changé, publier sur Redis
            if 'status' in request.data:
                message_broker.publish(f'tasks/status/{task.id}', {
                    'task_id': str(task.id),
                    'name': task.name,
                    'status': task.status,
                    'progress': task.progress
                })
                
            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Suppression d'une tâche
    def destroy(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
            
            # Publier la suppression sur Redis
            message_broker.publish('tasks/delete', {
                'task_id': str(task.id),
                'name': task.name
            })
            
            task.delete()
            return Response({'success': 'Task deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


# System Health check endpoint
class SystemHealthView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Endpoint pour vérifier l'état du système
        """
        try:
            # Vérifier la connexion à MongoDB
            db = get_db()
            db_status = "connected" if db else "disconnected"
            
            # Compter les volunteers actifs
            active_volunteers = Volunteer.objects.filter(current_status='available').count()
            
            # Simuler d'autres vérifications de santé
            # Dans une application réelle, vous pourriez vérifier d'autres systèmes
            recent_errors = 0  # Ceci serait déterminé par un système de logging
            
            # Construire la réponse
            health_data = {
                "status": "ok" if db_status == "connected" else "warning",
                "details": {
                    "database": db_status,
                    "active_volunteers": active_volunteers,
                    "recent_errors": recent_errors,
                    "redis_connection": "connected"  # Vous pourriez vérifier cela dynamiquement
                }
            }
            
            return Response(health_data)
        except Exception as e:
            return Response({
                "status": "error",
                "details": {
                    "message": str(e)
                }
            }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour obtenir les données sur le statut des workflows
class WorkflowStatusView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Endpoint pour obtenir la distribution des statuts des workflows
        """
        try:
            # Obtenir tous les workflows
            workflows = Workflow.objects.all()
            
            # Compter les workflows par statut
            status_counts = {}
            for workflow in workflows:
                status = workflow.status
                if status in status_counts:
                    status_counts[status] += 1
                else:
                    status_counts[status] = 1
            
            # Formater les données pour le frontend (format attendu par recharts)
            result = [{"name": status, "value": count} for status, count in status_counts.items()]
            
            # Si aucun workflow n'existe, renvoyer des données de test
            if not result:
                result = [
                    {"name": "CREATED", "value": 2},
                    {"name": "RUNNING", "value": 3},
                    {"name": "COMPLETED", "value": 1}
                ]
            
            return Response(result)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour obtenir les données sur le statut des volunteers
class VolunteerStatusView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Endpoint pour obtenir la distribution des statuts des volunteers
        """
        try:
            # Obtenir tous les volunteers
            volunteers = Volunteer.objects.all()
            
            # Compter les volunteers par statut
            status_counts = {}
            for volunteer in volunteers:
                status = volunteer.current_status  # Utiliser current_status au lieu de status
                if status in status_counts:
                    status_counts[status] += 1
                else:
                    status_counts[status] = 1
            
            # Formater les données pour le frontend (format attendu par recharts)
            result = [{"name": status, "value": count} for status, count in status_counts.items()]
            
            # Si aucun volunteer n'existe, renvoyer des données de test
            if not result:
                result = [
                    {"name": "available", "value": 5},
                    {"name": "busy", "value": 3},
                    {"name": "offline", "value": 2}
                ]
            
            return Response(result)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour obtenir les données de performance des tâches
class TaskPerformanceView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Endpoint pour obtenir les données de performance des tâches
        """
        try:
            # Obtenir toutes les tâches
            tasks = Task.objects.all()
            
            # Calculer le temps moyen d'exécution par type de tâche
            # Dans un cas réel, vous auriez des données plus précises
            task_types = {}
            for task in tasks:
                task_type = task.name.split()[0] if task.name else "Unknown"
                
                # Simuler des données de performance
                if task_type not in task_types:
                    task_types[task_type] = {
                        "count": 0,
                        "total_time": 0,
                        "success_rate": 0
                    }
                
                task_types[task_type]["count"] += 1
                
                # Simuler le temps d'exécution (en minutes)
                execution_time = 0
                if task.start_time and task.end_time:
                    start = task.start_time
                    end = task.end_time
                    execution_time = (end - start).total_seconds() / 60
                else:
                    # Simuler un temps d'exécution si non disponible
                    execution_time = 10 + (hash(task.id) % 50)  # Entre 10 et 60 minutes
                
                task_types[task_type]["total_time"] += execution_time
                
                # Simuler le taux de réussite
                if task.status == "COMPLETED":
                    task_types[task_type]["success_rate"] += 1
            
            # Calculer les moyennes et formater les données
            result = []
            for task_type, data in task_types.items():
                count = data["count"]
                avg_time = data["total_time"] / count if count > 0 else 0
                success_rate = (data["success_rate"] / count * 100) if count > 0 else 0
                
                result.append({
                    "name": task_type,
                    "avgExecutionTime": round(avg_time, 2),
                    "successRate": round(success_rate, 2),
                    "count": count
                })
            
            # Si aucune tâche n'existe, renvoyer des données de test
            if not result:
                result = [
                    {"name": "Preprocessing", "avgExecutionTime": 15.5, "successRate": 92.0, "count": 12},
                    {"name": "Training", "avgExecutionTime": 45.2, "successRate": 85.5, "count": 8},
                    {"name": "Validation", "avgExecutionTime": 12.8, "successRate": 97.0, "count": 15},
                    {"name": "Deployment", "avgExecutionTime": 8.5, "successRate": 89.0, "count": 5}
                ]
            
            return Response(result)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vue pour obtenir les données d'utilisation des ressources
class ResourceUtilizationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Endpoint pour obtenir les données d'utilisation des ressources
        """
        try:
            # Dans un cas réel, vous récupéreriez ces données à partir de métriques système
            # Ici, nous simulons des données d'utilisation des ressources
            
            # Obtenir tous les volunteers pour simuler l'utilisation des ressources
            volunteers = Volunteer.objects.all()
            
            # Simuler l'utilisation des ressources pour chaque volunteer
            resource_data = []
            for i, volunteer in enumerate(volunteers):
                # Simuler des données d'utilisation CPU/RAM/Disque
                cpu_usage = 20 + (hash(str(volunteer.id)) % 60)  # Entre 20% et 80%
                ram_usage = 30 + (hash(str(volunteer.id) + "ram") % 50)  # Entre 30% et 80%
                disk_usage = 10 + (hash(str(volunteer.id) + "disk") % 70)  # Entre 10% et 80%
                
                resource_data.append({
                    "name": volunteer.name or f"Volunteer-{i+1}",
                    "cpu": cpu_usage,
                    "ram": ram_usage,
                    "disk": disk_usage
                })
            
            # Si aucun volunteer n'existe, renvoyer des données de test
            if not resource_data:
                resource_data = [
                    {"name": "Server-1", "cpu": 65, "ram": 72, "disk": 45},
                    {"name": "Server-2", "cpu": 35, "ram": 48, "disk": 30},
                    {"name": "Server-3", "cpu": 80, "ram": 65, "disk": 70},
                    {"name": "Server-4", "cpu": 45, "ram": 55, "disk": 25},
                    {"name": "Server-5", "cpu": 55, "ram": 40, "disk": 50}
                ]
            
            return Response(resource_data)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


