"""Views for the motions app."""
from rest_framework import generics

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


class MotionEventDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific motion event
    PUT: Update a motion event
    DELETE: Delete a motion event
    """
    queryset = MotionEvent.objects.all()
    serializer_class = MotionEventSerializer


class MotionEventImagesList(generics.ListAPIView):
    """
    GET: List all images for a specific motion event
    """
    serializer_class = ImageSerializer

    def get_queryset(self):
        """Return images filtered by the motion event ID from URL."""
        motion_id = self.kwargs['pk']
        return Image.objects.filter(motion_event_id=motion_id)
