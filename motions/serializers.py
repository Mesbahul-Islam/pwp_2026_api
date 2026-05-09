"""
Serializers for the motions app.
Provides serialization for MotionEvent model.
"""

from rest_framework import serializers
from rest_framework.reverse import reverse
from cameras.models import Camera
from .models import MotionEvent
from eyesedge.schema_validation import validate_payload_with_schema


class MotionEventSerializer(serializers.ModelSerializer):
    """Serializer for MotionEvent model with timestamp as read-only.
    Code borrowed from 
    https://github.com/UniOulu-Ubicomp-Programming-Courses/
    pwp-sensorhub-example/blob/ex2-05-validation/app.py"""

    url = serializers.SerializerMethodField()
    camera = serializers.SlugRelatedField(slug_field="uuid", queryset=Camera.objects.all())

    @staticmethod
    def _json_schema(partial=False):
        schema = {
            "type": "object",
            "properties": {
                "camera": {
                    "description": "Related camera ID",
                    "type": "string",
                    "format": "uuid",
                },
                "duration": {
                    "description": "Motion duration in seconds",
                    "type": "number",
                    "minimum": 0,
                },
                "threshold": {
                    "description": "Motion threshold used by detector",
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
            },
            "additionalProperties": False,
        }
        if not partial:
            schema["required"] = ["camera", "duration"]
        return schema

    def validate(self, attrs):
        payload = dict(attrs)
        camera = payload.get("camera")
        if hasattr(camera, "uuid"):
            payload["camera"] = str(camera.uuid)

        validate_payload_with_schema(payload, self._json_schema(partial=self.partial))
        return super().validate(attrs)

    def get_url(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        return reverse("motion-detail", kwargs={"uuid": obj.uuid}, request=request)

    class Meta:
        model = MotionEvent
        fields = ['uuid', 'url', 'camera', 'timestamp', 'duration', 'threshold', 'created_at']
        read_only_fields = ['uuid', 'timestamp', 'created_at']
