"""
Serializers for the motions app.
Provides serialization for MotionEvent model.
"""
from rest_framework import serializers
from .models import MotionEvent


class MotionEventSerializer(serializers.ModelSerializer):
    """Serializer for MotionEvent model with timestamp as read-only."""

    class Meta:
        model = MotionEvent
        fields = ['id', 'camera', 'timestamp', 'duration', 'threshold', 'created_at']
        read_only_fields = ['timestamp', 'created_at']
