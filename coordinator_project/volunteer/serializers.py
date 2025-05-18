from rest_framework import serializers
from .models import Volunteer

class VolunteerSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    cpu_model = serializers.CharField()
    cpu_cores = serializers.IntegerField()
    total_ram = serializers.IntegerField()
    available_storage = serializers.IntegerField()
    operating_system = serializers.CharField()
    last_update = serializers.DateTimeField(required=False)
    current_status = serializers.CharField()
    gpu_available = serializers.BooleanField()
    gpu_model = serializers.CharField(allow_null=True, required=False)
    gpu_memory = serializers.IntegerField(allow_null=True, required=False)
    ip_address = serializers.CharField()
    communication_port = serializers.IntegerField()
    preferences = serializers.DictField(required=False)
    performance = serializers.DictField(required=False)
    last_activity = serializers.DateTimeField(allow_null=True, required=False)

    def create(self, validated_data):
        volunteer = Volunteer(**validated_data)
        volunteer.save()
        return volunteer

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance