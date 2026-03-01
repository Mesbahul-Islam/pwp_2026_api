"""
Serializers for the images app.
Provides serialization for Image model with derived camera field.
"""
from rest_framework import serializers
from models import Image


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Image model.
    
    Camera is derived from the motion event relationship
    and included as a read-only field.
    """
    camera = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at']
        read_only_fields = ['created_at', 'camera']

    def get_camera(self, obj):
        """Get camera ID from the associated motion event."""
        return obj.motion_event.camera.id
