"""
Views for the cameras app.
Provides API endpoints for camera management and related resources.
"""
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["address", "resolution", "fps", "status"]


class CameraDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific camera
    PUT: Update a camera
    DELETE: Delete a camera
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]


class CameraMotionsList(generics.ListCreateAPIView):
    """
    GET: List all motion events for a specific camera
    POST: Create a motion event for a specific camera
    """
    serializer_class = MotionEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["duration", "threshold", "timestamp"]

    def get_queryset(self):
        """Return motion events filtered by camera ID."""
        camera_id = self.kwargs['pk']
        return MotionEvent.objects.filter(camera_id=camera_id)

    def create(self, request, *args, **kwargs):
        """Create a motion event and force camera from URL path."""
        payload = request.data.copy()
        payload["camera"] = self.kwargs["pk"]

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CameraImagesList(generics.ListAPIView):
    """
    GET: List all images for a specific camera
    """
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["filepath", "filesize", "motion_event"]

    def get_queryset(self):
        """Return images filtered by camera ID via motion event."""
        camera_id = self.kwargs['pk']
        return Image.objects.filter(motion_event__camera_id=camera_id)
