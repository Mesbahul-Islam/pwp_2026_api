"""
Serializers for the motions app.
Provides serialization for MotionEvent model.
"""
from rest_framework import serializers
from .models import MotionEvent
from eyesedge.schema_validation import validate_payload_with_schema


class MotionEventSerializer(serializers.ModelSerializer):
    """Serializer for MotionEvent model with timestamp as read-only."""

    @staticmethod
    def _json_schema(partial=False):
        schema = {
            "type": "object",
            "properties": {
                "camera": {
                    "description": "Related camera ID",
                    "type": "integer",
                    "minimum": 1,
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
        payload = self.initial_data if isinstance(self.initial_data, dict) else attrs
        validate_payload_with_schema(payload, self._json_schema(partial=self.partial))
        return super().validate(attrs)

    class Meta:
        model = MotionEvent
        fields = ['id', 'camera', 'timestamp', 'duration', 'threshold', 'created_at']
        read_only_fields = ['timestamp', 'created_at']
