"""
Models for the motions app.
Defines the MotionEvent model for recording motion detection events.
"""
from django.db import models


class MotionEvent(models.Model):
    """
    Represents a motion detection event recorded by a camera.
    
    Stores the camera reference, timestamp, duration of motion,
    and the sensitivity threshold that triggered the detection.
    """
    camera = models.ForeignKey(
        'cameras.Camera',
        on_delete=models.CASCADE,
        related_name='motions_events'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    threshold = models.FloatField(default=0.25)

    def __str__(self):
        """Return a description of the motion event."""
        return f"Motion detected by {self.camera} at {self.timestamp}"
