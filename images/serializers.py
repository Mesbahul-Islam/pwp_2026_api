from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    camera = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at']
        read_only_fields = ['created_at', 'camera']

    def get_camera(self, obj):
        """Get camera ID from motion event"""
        return obj.motion_event.camera.id
