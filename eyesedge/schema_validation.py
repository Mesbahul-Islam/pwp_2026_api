"""Utilities for request payload validation against JSON Schema."""

from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import FormatChecker
from jsonschema import validate
from rest_framework import serializers


def validate_payload_with_schema(data, schema):
    """Valide with Jsonschema and raise DRF error."""
    try:
        validate(instance=data, schema=schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as exc:
        if exc.path:
            field_name = str(exc.path[-1])
            raise serializers.ValidationError({field_name: [exc.message]}) from exc

        raise serializers.ValidationError({"non_field_errors": [exc.message]}) from exc
