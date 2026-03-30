"""Views for the motions app."""
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from images.models import Image
from images.serializers import ImageSerializer

from .models import MotionEvent
from .serializers import MotionEventSerializer


class MotionEventList(generics.ListCreateAPIView):
    """
    GET: List all motion events
    POST: Create a new motion event
    """
    queryset = MotionEvent.objects.all()
    serializer_class = MotionEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "camera", "duration", "threshold", "timestamp", "created_at"]


class MotionEventDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific motion event
    PUT: Update a motion event
    DELETE: Delete a motion event
    """
    queryset = MotionEvent.objects.all()
    serializer_class = MotionEventSerializer
    permission_classes = [permissions.IsAuthenticated]


class MotionEventImagesList(generics.ListCreateAPIView):
    """
    GET: List all images for a specific motion event
    POST: Create a new image for a specific motion event
    """
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "filepath", "filesize", "created_at", "motion_event"]

    def get_queryset(self):
        """Return images filtered by the motion event ID from URL."""
        motion_id = self.kwargs['pk']
        return Image.objects.filter(motion_event_id=motion_id)

    def create(self, request, *args, **kwargs):
        """Create an image and force motion event from URL path."""
        payload = request.data.copy()
        payload["motion_event"] = self.kwargs["pk"]

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
