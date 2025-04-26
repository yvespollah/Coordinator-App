from rest_framework import serializers
from .models import Manager
from django.contrib.auth.hashers import make_password

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

class ManagerRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        manager = Manager(**validated_data)
        manager.save()
        return manager
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ManagerDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    status = serializers.CharField()
    last_login = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
