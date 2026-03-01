"""Admin configuration for the cameras app."""
from django.contrib import admin

from .models import Camera

admin.site.register(Camera)
