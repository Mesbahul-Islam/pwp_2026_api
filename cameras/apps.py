"""App configuration for the cameras app."""
from django.apps import AppConfig


class CamerasConfig(AppConfig):
    """Django app configuration for cameras."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cameras'
