"""
Models for the images app.
Defines the Image model for storing captured photographs.
"""
from django.db import models


class Image(models.Model):
    """
    Represents a captured photograph from a camera.
    
    Images are linked to motion events. The camera is accessed
    through the motion event relationship to avoid redundancy.
    """
    motion_event = models.ForeignKey(
        "motions.MotionEvent",
        on_delete=models.CASCADE,
        related_name="images",
        null=False,
        blank=False,
    )
    filepath = models.URLField(null=False, blank=False)
    filesize = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def camera(self):
        """Access camera through motion event relationship."""
        return self.motion_event.camera

    def __str__(self) -> str:
        """Return a description of the image with camera and timestamp."""
        return f"{self.motion_event.camera.address} @ {self.created_at.isoformat()}"
