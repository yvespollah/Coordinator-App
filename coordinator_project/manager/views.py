from rest_framework import viewsets, permissions 
from rest_framework.response import Response
from .models import Manager
from .serializers import (
    ManagerSerializer,
    ManagerRegistrationSerializer,
    ManagerDetailSerializer
)

# Create your views here.
class ManagerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ManagerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            return Response(ManagerDetailSerializer(manager).data, status=201)
        return Response(serializer.errors, status=400)
    def update(self, request, pk=None):
        try:
            manager = Manager.objects.get(id=pk)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ManagerRegistrationSerializer(manager, data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            return Response(ManagerDetailSerializer(manager).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)