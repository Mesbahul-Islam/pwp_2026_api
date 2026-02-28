"""
Views for the cameras app.
Provides API endpoints for camera management and related resources.
"""
from rest_framework import generics

from images.models import Image
from images.serializers import ImageSerializer
from motions.models import MotionEvent
from motions.serializers import MotionEventSerializer
from .models import Camera
from .serializers import CameraSerializer


class CameraList(generics.ListCreateAPIView):
    """
    GET: List all cameras
    POST: Create a new camera
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific camera
    PUT: Update a camera
    DELETE: Delete a camera
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraMotionsList(generics.ListAPIView):
    """
    GET: List all motion events for a specific camera
    """
    serializer_class = MotionEventSerializer

    def get_queryset(self):
        """Return motion events filtered by camera ID."""
        camera_id = self.kwargs['pk']
        return MotionEvent.objects.filter(camera_id=camera_id)


class CameraImagesList(generics.ListAPIView):
    """
    GET: List all images for a specific camera
    """
    serializer_class = ImageSerializer

    def get_queryset(self):
        """Return images filtered by camera ID via motion event."""
        camera_id = self.kwargs['pk']
        return Image.objects.filter(motion_event__camera_id=camera_id)
