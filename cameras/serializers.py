"""
Serializers for the cameras app.
Provides serialization for Camera model.
"""
from rest_framework import serializers
from .models import Camera
from eyesedge.schema_validation import validate_payload_with_schema


class CameraSerializer(serializers.ModelSerializer):
    """Serializer for Camera model with all configuration fields."""

    @staticmethod
    def _json_schema(partial=False):
        schema = {
            "type": "object",
            "properties": {
                "address": {
                    "description": "Camera stream URL",
                    "type": "string",
                    "format": "uri",
                },
                "resolution": {
                    "description": "Camera resolution",
                    "type": "string",
                    "enum": [
                        Camera.RESOLUTION_720P,
                        Camera.RESOLUTION_1080P,
                        Camera.RESOLUTION_4K,
                    ],
                },
                "fps": {
                    "description": "Frames per second",
                    "type": "integer",
                    "minimum": 1,
                },
                "status": {
                    "description": "Camera status",
                    "type": "string",
                    "enum": ["active", "inactive"],
                },
            },
            "additionalProperties": False,
        }
        if not partial:
            schema["required"] = ["address", "resolution"]
        return schema

    def validate(self, attrs):
        payload = self.initial_data if isinstance(self.initial_data, dict) else attrs
        validate_payload_with_schema(payload, self._json_schema(partial=self.partial))
        return super().validate(attrs)

    class Meta:
        model = Camera
        fields = ['id', 'address', 'resolution', 'fps', 'status']
