from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at']
        read_only_fields = ['created_at']
