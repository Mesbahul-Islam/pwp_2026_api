"""
Serializers for the images app.
Provides serialization for Image model with derived camera field.
"""

from rest_framework import serializers
from rest_framework.reverse import reverse
from motions.models import MotionEvent
from eyesedge.schema_validation import validate_payload_with_schema
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Image model.
    
    Camera is derived from the motion event relationship
    and included as a read-only field.
    Code borrowed from:
    https://github.com/UniOulu-Ubicomp-Programming-Courses/
    pwp-sensorhub-example/blob/ex2-05-validation/app.py
    """
    url = serializers.SerializerMethodField()
    camera = serializers.SerializerMethodField()
    motion_event = serializers.SlugRelatedField(slug_field="uuid", queryset=MotionEvent.objects.all())

    @staticmethod
    def _json_schema(partial=False):
        schema = {
            "type": "object",
            "properties": {
                "motion_event": {
                    "description": "Related motion event ID",
                    "type": "string",
                    "format": "uuid",
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
        fields = ['uuid', 'url', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at']
        read_only_fields = ['uuid', 'created_at', 'camera']

    def validate(self, attrs):
        payload = dict(attrs)
        motion_event = payload.get("motion_event")
        if hasattr(motion_event, "uuid"):
            payload["motion_event"] = str(motion_event.uuid)

        validate_payload_with_schema(payload, self._json_schema(partial=self.partial))
        return super().validate(attrs)

    def get_camera(self, obj):
        """Get camera ID from the associated motion event."""
        return str(obj.motion_event.camera.uuid)

    def get_url(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        return reverse("image-detail", kwargs={"uuid": obj.uuid}, request=request)
