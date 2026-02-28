"""App configuration for the motions app."""
from django.apps import AppConfig


class MotionsConfig(AppConfig):
    """Django app configuration for motions."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'motions'
