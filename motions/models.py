from django.db import models

class MotionEvent(models.Model):
    camera = models.ForeignKey('cameras.Camera', on_delete=models.CASCADE, related_name='motions_events')
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    threshold = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Motion detected by {self.camera} at {self.timestamp}"