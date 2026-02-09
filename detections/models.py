from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Detection(models.Model):
    motion_event = models.ForeignKey(
        "motions.MotionEvent",
        on_delete=models.CASCADE,
        related_name="detections",
        null=True,
        blank=True,
    )
    image = models.ForeignKey(
        "images.Image",
        on_delete=models.CASCADE,
        related_name="detections",
        null=True,
        blank=True,
    )
    object_class = models.CharField(max_length=100)
    confidence = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.object_class} ({self.confidence:.2f})"
