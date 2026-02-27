from rest_framework import serializers
from .models import MotionEvent


class MotionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotionEvent
        fields = ['id', 'camera', 'timestamp', 'duration', 'threshold', 'created_at']
        read_only_fields = ['timestamp', 'created_at']
