"""
Serializers for the images app.
Provides serialization for Image model with derived camera field.
"""
from rest_framework import serializers
from .models import Image
from eyesedge.schema_validation import validate_payload_with_schema


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Image model.
    
    Camera is derived from the motion event relationship
    and included as a read-only field.
    """
    camera = serializers.SerializerMethodField()

    @staticmethod
    def _json_schema(partial=False):
        schema = {
            "type": "object",
            "properties": {
                "motion_event": {
                    "description": "Related motion event ID",
                    "type": "integer",
                    "minimum": 1,
                },
                "filepath": {
                    "description": "URL path to image file",
                    "type": "string",
                    "format": "uri",
                },
                "filesize": {
                    "description": "Image file size in bytes",
                    "type": ["integer", "null"],
                    "minimum": 0,
                },
            },
            "additionalProperties": False,
        }
        if not partial:
            schema["required"] = ["motion_event", "filepath"]
        return schema

    class Meta:
        model = Image
        fields = ['id', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at']
        read_only_fields = ['created_at', 'camera']

    def validate(self, attrs):
        payload = self.initial_data if isinstance(self.initial_data, dict) else attrs
        validate_payload_with_schema(payload, self._json_schema(partial=self.partial))
        return super().validate(attrs)

    def get_camera(self, obj):
        """Get camera ID from the associated motion event."""
        return obj.motion_event.camera.id
