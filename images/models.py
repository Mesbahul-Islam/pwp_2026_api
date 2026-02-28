from django.db import models


class Image(models.Model):
    motion_event = models.ForeignKey(
        "motions.MotionEvent",
        on_delete=models.CASCADE,
        related_name="images",
        null=False
    )
    filepath = models.URLField(null=False, blank=False)
    filesize = models.PositiveIntegerField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def camera(self):
        """Access camera through motion event"""
        return self.motion_event.camera

    def __str__(self) -> str:
        return f"{self.motion_event.camera.address} @ {self.created_at.isoformat()}"

