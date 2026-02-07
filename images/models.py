from django.db import models


class Image(models.Model):
    camera = models.ForeignKey(
        "cameras.Camera", on_delete=models.CASCADE, related_name="images"
    )
    motion_event = models.ForeignKey(
        "motions.MotionEvent",
        on_delete=models.CASCADE,
        related_name="images",
        null=False
    )
    filepath = models.URLField(null=False, blank=False)
    filesize = models.PositiveIntegerField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.camera.name} @ {self.created_at.isoformat()}"
