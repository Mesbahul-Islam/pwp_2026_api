from django.db import models


class Camera(models.Model):
    RESOLUTION_720P = "1280x720"
    RESOLUTION_1080P = "1920x1080"
    RESOLUTION_4K = "3840x2160"

    RESOLUTION_CHOICES = [
        (RESOLUTION_720P, "720p"),
        (RESOLUTION_1080P, "1080p"),
        (RESOLUTION_4K, "4k"),
    ]
    address = models.URLField(unique=True)
    resolution = models.CharField(max_length=15, choices=RESOLUTION_CHOICES)
    fps = models.PositiveIntegerField(default=25)
    motion_sensitivity = models.FloatField(default=0.25, null=False)
    status = models.CharField(max_length=20, default="active")


    def __str__(self):
        return self.address