from rest_framework import serializers
from .models import Volunteer
from django.contrib.auth.hashers import make_password

class VolunteerSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    cpu_model = serializers.CharField(max_length=100)
    cpu_cores = serializers.IntegerField()
    total_ram = serializers.IntegerField()
    available_storage = serializers.IntegerField()
    operating_system = serializers.CharField(max_length=100)
    gpu_available = serializers.BooleanField(default=False)
    gpu_model = serializers.CharField(max_length=255)
    gpu_memory = serializers.IntegerField()
    status = serializers.CharField()
    last_connected = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class VolunteerRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    cpu_model = serializers.CharField(max_length=100)
    cpu_cores = serializers.IntegerField()
    total_ram = serializers.IntegerField()
    available_storage = serializers.IntegerField()
    operating_system = serializers.CharField(max_length=100)
    gpu_available = serializers.BooleanField(default=False)
    gpu_model = serializers.CharField(max_length=255)
    gpu_memory = serializers.IntegerField()
    # preferences = serializers.DictField(allow_null=True)

    def create(self, validated_data):
        volunteer = Volunteer(**validated_data)
        volunteer.save()
        return volunteer

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class VolunteerDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    status = serializers.CharField()
    cpu_model = serializers.CharField(max_length=100)
    cpu_cores = serializers.IntegerField()
    total_ram = serializers.IntegerField()
    available_storage = serializers.IntegerField()
    operating_system = serializers.CharField(max_length=100)
    gpu_available = serializers.BooleanField(default=False)
    gpu_model = serializers.CharField(max_length=255)
    gpu_memory = serializers.IntegerField()
    last_connected = serializers.DateTimeField(allow_null=True)

""" class VolunteerRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    tech_specs = serializers.DictField()
    preferences = serializers.DictField()

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        volunteer = Volunteer(**validated_data)
        volunteer.save()
        return volunteer """