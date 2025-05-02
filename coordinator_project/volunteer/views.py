from rest_framework import viewsets, status,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .utils.jwt_utils import generate_jwt
from .decorators.auth_decorators import jwt_required
from django.utils import timezone
from .models import Volunteer
from .serializers import VolunteerSerializer

class VolunteerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        volunteers = Volunteer.objects.all()
        serializer = VolunteerSerializer(volunteers, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = VolunteerSerializer(data=request.data)
        if serializer.is_valid():
            volunteer = serializer.save()
            return Response(VolunteerSerializer(volunteer).data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        try:
            volunteer = Volunteer.objects.get(id=pk)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VolunteerSerializer(volunteer)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            volunteer = Volunteer.objects.get(id=pk)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VolunteerSerializer(volunteer, data=request.data, partial=True)
        if serializer.is_valid():
            volunteer = serializer.save()
            return Response(VolunteerSerializer(volunteer).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            volunteer = Volunteer.objects.get(id=pk)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        volunteer.delete()
        return Response({'success': 'Volunteer deleted'}, status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['get'])
    @jwt_required
    def available(self, request):
        available_volunteers = Volunteer.objects(status='available')
        serializer = VolunteerDetailSerializer(available_volunteers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_tech_specs(self, request, pk=None):
        try:
            volunteer = Volunteer.objects.get(id=pk)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        for field in ['cpu_model', 'cpu_cores', 'total_ram', 'available_storage', 'operating_system', 'gpu_available', 'gpu_model', 'gpu_memory']:
            if field in request.data:
                setattr(volunteer, field, request.data[field])
        volunteer.save()
        return Response(VolunteerDetailSerializer(volunteer).data)

    @action(detail=True, methods=['post'])
    def update_preferences(self, request, pk=None):
        try:
            volunteer = Volunteer.objects.get(id=pk)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        new_preferences = request.data.get('preferences', {})
        volunteer.preferences.update(new_preferences)
        volunteer.save()
        return Response(VolunteerDetailSerializer(volunteer).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        try:
            volunteer = Volunteer.objects.get(id=pk)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Volunteer not found'}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status')
        if new_status not in ['offline', 'available', 'busy']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        volunteer.update_status(new_status)
        return Response({'status': 'updated'})
