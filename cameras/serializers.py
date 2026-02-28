"""
Serializers for the cameras app.
Provides serialization for Camera model.
"""
from rest_framework import serializers
from .models import Camera


class CameraSerializer(serializers.ModelSerializer):
    """Serializer for Camera model with all configuration fields."""

    class Meta:
        model = Camera
        fields = ['id', 'address', 'resolution', 'fps', 'motion_sensitivity', 'status']
