from django.db import models


class Alert(models.Model):
    detection = models.ForeignKey(
        "detections.Detection",
        on_delete=models.CASCADE,
        related_name="alerts",
        null=False,
        blank=False,
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)