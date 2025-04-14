from rest_framework import serializers
from .models import *

# Manager serializer
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

# Workflow serializer
class WorkflowSerializer(serializers.ModelSerializer):
    owner = ManagerSerializer(read_only=True)

    class Meta:
        model = Workflow
        fields = '__all__'

# Task serializer
class TaskSerializer(serializers.ModelSerializer):
    workflow = serializers.PrimaryKeyRelatedField(queryset=Workflow.objects.all())
    parent_task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Task
        fields = '__all__'

# Machine serializer
class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

# Availability serializer
class AvailabilitySerializer(serializers.ModelSerializer):
    machine = serializers.PrimaryKeyRelatedField(queryset=Machine.objects.all())

    class Meta:
        model = Availability
        fields = '__all__'
