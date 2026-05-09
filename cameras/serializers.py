"""
Serializers for the cameras app.
Provides serialization for Camera model.
"""

from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Camera
from eyesedge.schema_validation import validate_payload_with_schema


class CameraSerializer(serializers.ModelSerializer):
    """Serializer for Camera model with all configuration fields.

    Code borrowed from:
    https://github.com/UniOulu-Ubicomp-Programming-Courses/
    pwp-sensorhub-example/blob/ex2-05-validation/app.py
    """

    url = serializers.SerializerMethodField()

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
        validate_payload_with_schema(attrs, self._json_schema(partial=self.partial))
        return super().validate(attrs)

    def get_url(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        return reverse("camera-detail", kwargs={"uuid": obj.uuid}, request=request)

    class Meta:
        model = Camera
        fields = ['uuid', 'url', 'address', 'resolution', 'fps', 'status']
        read_only_fields = ['uuid']
