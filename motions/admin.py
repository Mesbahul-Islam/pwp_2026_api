"""Admin configuration for the motions app."""
from django.contrib import admin

from .models import MotionEvent

admin.site.register(MotionEvent)
